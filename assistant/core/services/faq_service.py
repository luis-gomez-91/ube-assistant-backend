import httpx
from assistant.settings import API_UBE_URL
from schemas.faq import VerifyModel, PasswordRecoveryModel


async def fetch_verify(token: str) -> VerifyModel:
    headers = {"Authorization": token}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_UBE_URL}auth/verify/", headers=headers)
        response.raise_for_status()
        data = response.json()
        return VerifyModel(**data)

async def password_recovery(token: str, telefono: str) -> PasswordRecoveryModel:
    headers = {"Authorization": token}
    data = {"telefono": telefono}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_UBE_URL}password_recovery/", headers=headers, json=data)
        response.raise_for_status()
        data = response.json()
        print(f"DATA: {data}")
        return PasswordRecoveryModel(**data)