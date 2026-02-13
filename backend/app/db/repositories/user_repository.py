from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.models.user import User, UserRole
from app.utils.security_utils import get_password_hash
from datetime import datetime


class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create(
        self, 
        username: str, 
        email: str, 
        password: str, 
        full_name: Optional[str] = None,
        role: UserRole = UserRole.EMPLOYEE,
        created_by: Optional[int] = None
    ) -> User:
        """Create new user"""
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            created_by=created_by
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_employees(self) -> List[User]:
        """Get all employees"""
        return self.db.query(User).filter(User.role == UserRole.EMPLOYEE).all()
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        return self.db.query(User).all()
    
    def update_last_login(self, user_id: int):
        """Update user's last login time"""
        user = self.get_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()