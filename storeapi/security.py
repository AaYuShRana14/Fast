from storeapi.config import config
from fastapi import HTTPException
from datetime import  timedelta,timezone,datetime
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
pwd_context = CryptContext(schemes=["bcrypt"])
def createToken(name: str) -> str:
    expire_time = datetime.now(timezone.utc)+ timedelta(hours=1)
    jwt_data={"sub": name,"exp": int(expire_time.timestamp())}
    token = jwt.encode(jwt_data, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return token
def decodeToken(token: str) -> str:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload["name"]
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
def get_current_user(token: str) -> str:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload["sub"]
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")