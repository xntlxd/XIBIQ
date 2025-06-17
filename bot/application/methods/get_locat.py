import httpx


async def get_location_by_ip(ip: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://ip-api.com/json/{ip}")
            data = response.json()
            return {"country": data.get("country"), "city": data.get("city")}
    except Exception as e:
        return {"error": str(e)}
