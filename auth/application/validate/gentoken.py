async def gen_token(type: str, subject: str | None = None):
    return {"type": type, "sub": subject}
