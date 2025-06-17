from fastapi import HTTPException, status


def get_token(token: str) -> str:
    if not token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    return token[7:]
