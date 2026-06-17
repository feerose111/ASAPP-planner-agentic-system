from pydantic import BaseModel, EmailStr

class SignUpRequest(BaseModel):
    username: str | None = None
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    username: str | None = None
    password: str

