from fastapi import APIRouter, Depends


user_router = APIRouter(prefix="/user", tags=["user"])