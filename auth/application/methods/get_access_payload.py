from application.models import Users


async def get_access_payload(user: Users, ffl: bool = True):
    payload = {"ffl": ffl, "adm": user.is_admin, "sud": user.is_sudo}
    return payload
