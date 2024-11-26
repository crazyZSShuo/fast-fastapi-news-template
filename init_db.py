from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app.crud import crud_user
from app.schemas.user import UserCreate
from app.core.config import settings

def init_db(db: Session) -> None:
    # 创建管理员用户
    admin = crud_user.user.get_by_email(db, email="zs@qq.com")
    if not admin:
        user_in = UserCreate(
            email="zs@qq.com",
            username="zs",
            password="zs1024"
        )
        user = crud_user.user.create(db, obj_in=user_in)
        # 将用户设置为管理员
        user.role = "admin"
        db.add(user)
        db.commit()
        print("Created admin user: zs@qq.com")
    else:
        print("Admin user already exists")

def main() -> None:
    print("Creating initial data")
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    init_db(db)
    print("Initial data created")

if __name__ == "__main__":
    main()
