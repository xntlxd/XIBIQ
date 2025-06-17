from fastapi import APIRouter


from application.serialized import Answer
from application.validate import GetCloudKeys
from application.auth import decode_token

router = APIRouter(prefix="/update", tags=["update"])


#! Добавление облачных ключей
@router.patch("/cloud_keys", response_model=Answer)
async def update_cloud_keys(data: GetCloudKeys) -> Answer:
    payload = decode_token(data.token)
    data.token = payload

    return Answer(data=data.model_dump())
