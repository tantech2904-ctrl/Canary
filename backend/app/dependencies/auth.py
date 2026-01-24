from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from ..core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        return {"id": int(payload["sub"]), "role": payload.get("role", "viewer")}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_role(required: str):
    async def checker(user=Depends(get_current_user)):
        roles_order = {"viewer": 1, "analyst": 2, "admin": 3}
        if roles_order.get(user["role"], 0) < roles_order.get(required, 0):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return checker
