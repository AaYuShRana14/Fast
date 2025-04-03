from storeapi.config import config
from fastapi import HTTPException
from datetime import  timedelta,timezone,datetime
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from storeapi.database import user_table,database
from typing import Literal
pwd_context = CryptContext(schemes=["bcrypt"])

def createToken(email:str,type:Literal["auth","verify"],id:int) -> str:
    expire_time = datetime.now(timezone.utc)+ timedelta(hours=1)
    jwt_data = {
        "email": email,
        "id": id,
        "type": type,
        "exp": expire_time
    }
    if type == "verify":
        expire_time = datetime.now(timezone.utc)+ timedelta(days=1)
        jwt_data["exp"] = expire_time
    token = jwt.encode(jwt_data, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return token
def decodeToken(token: str,type:Literal["auth","verify"]) -> str:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if(payload["type"]!=type):
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id": payload["id"], "email": payload["email"]}

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
async def get_current_user(token: str,type:Literal["auth","verify"]) -> str:
    try:
        payload = decodeToken(token,type)
        query = user_table.select().where(user_table.c.id == payload["id"])
        user = await database.fetch_one(query)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = dict(user)
        del user["password"]
        return user
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")