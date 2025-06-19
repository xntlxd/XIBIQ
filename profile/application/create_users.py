from fastapi import APIRouter, HTTPException

from application.serialized import Answer
from application.validate import CreateUser
from application.database import get_session
from application.models import User

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def get_user():
    return {"message": "Hello World"}


@router.post("/", response_model=Answer, summary="Создание пользователя")
async def create_user(data: CreateUser):
    if data.first_name is None and data.last_name is None:
        raise HTTPException(
            status_code=400, detail="First name and last name cannot be empty"
        )

    async with get_session() as session:
        try:
            new_user = User(
                telephone=data.telephone,
                first_name=data.first_name,
                last_name=data.last_name,
                avatar=data.avatar,
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
        except IntegrityError:
            raise HTTPException(
                status_code=400, detail="User with this telephone already exists"
            )
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Database error!")

    return Answer(
        data={
            "id": new_user.id,
            "telephone": new_user.telephone,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "avatar": new_user.avatar,
        },
        message="User created successfully",
    )
