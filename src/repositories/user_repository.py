from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database.models import User
from src.exceptions.custom_exceptions import DatabaseError


class UserRepository:
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_user_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, username: str, email: str, password: str) -> User:
        try:
            hashed_password = self.pwd_context.hash(password)
            user = User(username=username, email=email, hashed_password=hashed_password)
            self.db.add(user)
            self.db.commit()
            return user
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Database error while creating user: {str(e)}")
