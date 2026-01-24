from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token
from app.db.session import async_session
from app.services.users import authenticate_user
from app.schemas.auth import Token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    async with async_session() as session:
        user = await authenticate_user(session, form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token = create_access_token(subject=user["id"], role=user["role"]) 
        return Token(access_token=access_token, token_type="bearer")
