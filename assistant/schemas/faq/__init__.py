from typing import Optional
from pydantic import BaseModel, Field


class VerifyModel(BaseModel):
    id: int
    username: str
    email: str
    name: str
    perfil: Optional[str] = None
    photo: Optional[str] = None

class PasswordRecoveryModel(BaseModel):
    message: Optional[str] = Field(default=None)
    whatsapp_response: Optional[str] = Field(default=None, alias="whatsaap_response")
    error: Optional[str] = Field(default=None)