from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.api.deps import get_current_user
from app.db.models.user import User, UserRole
from app.db.repositories.user_repository import UserRepository
from app.schemas.admin_schemas import CreateEmployeeRequest, EmployeeResponse, UpdateEmployeeRequest

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to ensure user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/employees", response_model=EmployeeResponse)
def create_employee(
    employee_data: CreateEmployeeRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Admin creates employee account"""
    user_repo = UserRepository(db)
    
    # Check if username exists
    if user_repo.get_by_username(employee_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email exists
    if user_repo.get_by_email(employee_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create employee
    employee = user_repo.create(
        username=employee_data.username,
        email=employee_data.email,
        password=employee_data.password,
        full_name=employee_data.full_name,
        role=UserRole.EMPLOYEE,
        created_by=admin.id
    )
    
    return employee


@router.get("/employees", response_model=List[EmployeeResponse])
def list_employees(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Admin lists all employees"""
    user_repo = UserRepository(db)
    employees = user_repo.get_employees()
    return employees


@router.patch("/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    update_data: UpdateEmployeeRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Admin updates employee"""
    user_repo = UserRepository(db)
    employee = user_repo.get_by_id(employee_id)
    
    if not employee or employee.role != UserRole.EMPLOYEE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Update employee
    if update_data.is_active is not None:
        employee.is_active = update_data.is_active
    if update_data.full_name is not None:
        employee.full_name = update_data.full_name
    
    db.commit()
    db.refresh(employee)
    
    return employee


@router.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Admin deletes employee (deactivates)"""
    user_repo = UserRepository(db)
    employee = user_repo.get_by_id(employee_id)
    
    if not employee or employee.role != UserRole.EMPLOYEE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    employee.is_active = False
    db.commit()
    
    return {"success": True, "message": "Employee deactivated"}
