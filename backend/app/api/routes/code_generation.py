from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.repositories.stage_repository import StageRepository
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.code_repository import CodeRepository
from app.schemas.code_schemas import GenerateCodeRequest, GeneratedCodeResponse, UpdateCodeRequest, UpdateCodeResponse
from app.core.code_generation.structured_text_generator import st_generator
from app.services.version_history_service import VersionHistoryService
from app.core.code_generation.labels_csv_exporter import labels_csv_exporter
from app.services.global_labels_service import GlobalLabelsService

router = APIRouter()


@router.post("/generate", response_model=GeneratedCodeResponse)
async def generate_code(
    request: GenerateCodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate Structured Text code for ALL stages (requires all stages to be validated)
    """
    # Get stage
    stage_repo = StageRepository(db)
    stage = stage_repo.get_by_id(request.stage_id)
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    # Verify project ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(stage.project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Get ALL stages for this project
    all_stages = stage_repo.get_by_project(stage.project_id)
    
    # Check if ALL stages are validated
    unvalidated_stages = [s for s in all_stages if not s.is_validated]
    if unvalidated_stages:
        stage_names = ', '.join([s.stage_name for s in unvalidated_stages])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"All stages must be validated before generating code. Unvalidated stages: {stage_names}"
        )
    
    # Initialize services
    global_labels_service = GlobalLabelsService(db)
    code_repo = CodeRepository(db)
    version_service = VersionHistoryService(db)
    
    # Generate code for ALL stages
    generated_results = []
    all_global_labels = []
    
    try:
        for stg in all_stages:
            # Prepare stage data
            stage_data = {
                "id": stg.id,
                "stage_number": stg.stage_number,
                "stage_name": stg.stage_name,
                "stage_type": stg.stage_type,
                "description": stg.description,
                "original_logic": stg.original_logic,
                "edited_logic": stg.edited_logic
            }
            
            # Generate code for this stage
            result = await st_generator.generate_code(stage_data)
            
            if result['success']:
                # Collect all global labels from all stages
                all_global_labels.extend(result.get('global_labels', []))
                generated_results.append((stg, result))
            else:
                raise Exception(f"Failed to generate code for stage: {stg.stage_name}")
        
        # Merge all global labels (deduplicate)
        merged_global_labels = global_labels_service.merge_global_labels([], all_global_labels)
        
        # Save code for ALL stages with unified global labels
        for stg, result in generated_results:
            # Delete existing code for this stage
            code_repo.delete_by_stage(stg.id)
            
            # Create new code with unified global labels
            new_code = code_repo.create(
                project_id=stg.project_id,
                stage_id=stg.id,
                global_labels=merged_global_labels,  # Same for all stages
                local_labels=result.get('local_labels', []),
                program_body=result.get('program_body', ''),
                program_name=result['metadata'].get('program_name', ''),
                execution_type=result['metadata'].get('execution_type', 'Scan'),
                metadata=result['metadata'],
                program_blocks=result.get('program_blocks', []),
                functions=result.get('functions', []),
                function_blocks=result.get('function_blocks', [])
            )
            
            # Track version history
            version_service.create_version_entry(
                code_id=new_code.id,
                stage_id=stg.id,
                user_id=current_user.id,
                action_type="generate_code",
                new_data={
                    "program_body": result.get('program_body', ''),
                    "global_labels_count": len(merged_global_labels),
                    "local_labels_count": len(result.get('local_labels', [])),
                    "program_blocks_count": len(result.get('program_blocks', [])),
                    "functions_count": len(result.get('functions', [])),
                    "function_blocks_count": len(result.get('function_blocks', []))
                },
                metadata={
                    "description": "Code generated for all stages",
                    "program_name": result['metadata'].get('program_name', '')
                }
            )
        
        # Return the result for the requested stage
        requested_stage_result = next((r for s, r in generated_results if s.id == stage.id), None)
        
        if requested_stage_result:
            return GeneratedCodeResponse(
                success=True,
                stage_id=requested_stage_result['stage_id'],
                stage_name=requested_stage_result['stage_name'],
                global_labels=merged_global_labels,
                local_labels=requested_stage_result.get('local_labels', []),
                program_body=requested_stage_result.get('program_body', ''),
                metadata=requested_stage_result['metadata'],
                program_blocks=requested_stage_result.get('program_blocks', []),
                functions=requested_stage_result.get('functions', []),
                function_blocks=requested_stage_result.get('function_blocks', [])
            )
        else:
            raise Exception("Could not find result for requested stage")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code generation error: {str(e)}"
        )


@router.get("/stage/{stage_id}")
async def get_stage_code(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get generated code for a stage"""
    # Get stage
    stage_repo = StageRepository(db)
    stage = stage_repo.get_by_id(stage_id)
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(stage.project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Get code
    code_repo = CodeRepository(db)
    code = code_repo.get_by_stage(stage_id)
    
    if not code:
        return {
            "success": False,
            "message": "No code generated for this stage yet"
        }
    
    return {
        "success": True,
        "code": {
            "global_labels": code.global_labels,
            "local_labels": code.local_labels,
            "program_body": code.program_body,
            "program_name": code.program_name,
            "execution_type": code.execution_type,
            "metadata": code.code_metadata,
            "program_blocks": code.program_blocks or [],
            "functions": code.functions or [],
            "function_blocks": code.function_blocks or []
        }
    }


@router.get("/project/{project_id}")
async def get_project_codes(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all generated codes for a project"""
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Get codes
    code_repo = CodeRepository(db)
    codes = code_repo.get_project_codes(project_id)
    
    return {
        "success": True,
        "codes": codes
    }


@router.get("/stage/{stage_id}/export-labels")
async def export_stage_labels(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export local labels for a specific stage in GX Works 3 format"""
    # Get stage
    stage_repo = StageRepository(db)
    stage = stage_repo.get_by_id(stage_id)
    
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(stage.project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get generated code for this stage
    code_repo = CodeRepository(db)
    code = code_repo.get_by_stage(stage_id)
    
    if not code:
        raise HTTPException(
            status_code=404,
            detail="No generated code found for this stage. Please generate code first."
        )
    
    # Export local labels to GX Works 3 CSV format (export empty list if no labels)
    stage_name = f"Stage {stage.stage_number} - {stage.stage_name}"
    local_labels = code.local_labels if code.local_labels is not None else []
    csv_file = labels_csv_exporter.export_local_labels_gx_format(
        local_labels=local_labels,
        stage_name=stage_name
    )
    
    # Create filename
    filename = f"Stage_{stage.stage_number}_{stage.stage_name.replace(' ', '_')}_Local_Labels.csv"
    
    # Reset stream position
    csv_file.seek(0)
    
    # Return as streaming response with proper encoding for tab-separated format
    return StreamingResponse(
        csv_file,
        media_type="text/tab-separated-values; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/project/{project_id}/export-all-labels")
async def export_all_stages_labels(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export labels from all stages of a project to CSV"""
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get all stages for this project
    stage_repo = StageRepository(db)
    stages = stage_repo.get_by_project(project_id)
    
    if not stages:
        raise HTTPException(status_code=404, detail="No stages found for this project")
    
    # Collect labels from all stages
    code_repo = CodeRepository(db)
    stages_data = []
    
    for stage in stages:
        code = code_repo.get_by_stage(stage.id)
        if code and (code.global_labels or code.local_labels):
            stages_data.append({
                'stage_number': stage.stage_number,
                'stage_name': stage.stage_name,
                'global_labels': code.global_labels or [],
                'local_labels': code.local_labels or []
            })
    
    if not stages_data:
        raise HTTPException(
            status_code=404,
            detail="No generated code found for any stage. Please generate code first."
        )
    
    # Export to CSV
    csv_file = labels_csv_exporter.export_all_stages_labels(stages_data)
    
    # Create filename
    filename = f"All_Labels_{project.name.replace(' ', '_')}.csv"
    
    # Reset stream position
    csv_file.seek(0)
    
    # Return as streaming response with proper encoding for tab-separated format
    return StreamingResponse(
        csv_file,
        media_type="text/tab-separated-values; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/project/{project_id}/export-global-labels")
async def export_global_labels(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export global labels from the project in GX Works 3 format"""
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get all stages for this project
    stage_repo = StageRepository(db)
    stages = stage_repo.get_by_project(project_id)
    
    if not stages:
        raise HTTPException(status_code=404, detail="No stages found for this project")
    
    # Collect global labels from any stage (they should be the same across all stages)
    code_repo = CodeRepository(db)
    global_labels = []
    
    for stage in stages:
        code = code_repo.get_by_stage(stage.id)
        if code and code.global_labels:
            global_labels = code.global_labels
            break  # Global labels are the same for all stages, so we only need one
    
    if not global_labels:
        raise HTTPException(
            status_code=404,
            detail="No global labels found. Please generate code first."
        )
    
    # Export to CSV in GX Works 3 format
    csv_file = labels_csv_exporter.export_global_labels_gx_format(global_labels)
    
    # Create filename
    filename = f"{project.name.replace(' ', '_')}_Global_Labels.csv"
    
    # Reset stream position
    csv_file.seek(0)
    
    # Return as streaming response with proper encoding for tab-separated format
    return StreamingResponse(
        csv_file,
        media_type="text/tab-separated-values; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.put("/update", response_model=UpdateCodeResponse)
async def update_generated_code(
    request: UpdateCodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update generated code and synchronize labels across the project"""
    # Get stage
    stage_repo = StageRepository(db)
    stage = stage_repo.get_by_id(request.stage_id)
    
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(stage.project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get existing code
    code_repo = CodeRepository(db)
    code = code_repo.get_by_stage(request.stage_id)
    
    if not code:
        raise HTTPException(status_code=404, detail="No generated code found")
    
    try:
        # Update the code in database
        code.program_body = request.program_body
        
        # Update labels - use 'is not None' to allow empty lists (when all labels removed)
        if request.global_labels is not None:
            code.global_labels = request.global_labels
        if request.local_labels is not None:
            code.local_labels = request.local_labels
            
        db.commit()
        db.refresh(code)
        
        # Track version history
        version_service = VersionHistoryService(db)
        version_service.create_version_entry(
            code_id=code.id,
            stage_id=stage.id,
            user_id=current_user.id,
            action_type="edit_code",
            new_data={
                "program_body": request.program_body[:200] + "..." if len(request.program_body) > 200 else request.program_body,
                "global_labels_count": len(code.global_labels or []),
                "local_labels_count": len(code.local_labels or [])
            },
            metadata={
                "description": "Code manually edited"
            }
        )
        
        return UpdateCodeResponse(
            success=True,
            message="Code updated successfully. Labels synchronized across project.",
            stage_id=stage.id
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update code: {str(e)}"
        )
