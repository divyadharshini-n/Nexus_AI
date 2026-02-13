from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.db.models.user import User, UserRole
from app.db.repositories.user_repository import UserRepository
from app.schemas.admin_schemas import EmployeeResponse

router = APIRouter()


@router.get("/employees/list", response_model=List[EmployeeResponse])
async def list_employees_for_sharing(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of all employees (for sharing dropdown)"""
    user_repo = UserRepository(db)
    
    # Get all employees
    employees = user_repo.get_employees()
    
    # Exclude current user if they're an employee
    if current_user.role == UserRole.EMPLOYEE:
        employees = [emp for emp in employees if emp.id != current_user.id]
    
    return [
        EmployeeResponse(
            id=emp.id,
            username=emp.username,
            email=emp.email,
            full_name=emp.full_name,
            role=emp.role.value,
            is_active=emp.is_active,
            created_by=emp.created_by,
            created_at=emp.created_at
        )
        for emp in employees
    ]
