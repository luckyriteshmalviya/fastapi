import jwt
import time
from decouple import config
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..mopid.user.model import User

JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITHM = config("JWT_ALGORITHM")

security = HTTPBearer()

async def hasAccess(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = decodeJWT(token)
        if payload: return payload
        else: raise HTTPException(
            status_code=401,
            detail='Invalid token')
    except:
        raise HTTPException(
            status_code=401,
            detail='Invalid token')

async def isAdminAccess(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = decodeJWT(token)

        if payload and payload['role']=='admin':
            return payload
        else: raise HTTPException(status_code=403,detail='Forbidden')
    except Exception as e:
        raise HTTPException(status_code=403,detail='Forbidden')

async def isFacultyAccess(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = decodeJWT(token)

        if payload and payload['role']=='admin':
            return payload
        else: raise HTTPException(status_code=403,detail='Forbidden')
    except Exception as e:
        raise HTTPException(status_code=403,detail='Forbidden')
    
def signJWT(user: User):
    payload={
        "id": user.id,
        "name": user.name,
        "mobileNo": user.phone,
        "email": user.email,
        "type": user.type,
        "expiry": time.time() + 86400
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decodeJWT(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decode_token #if decode_token['expiry'] >= time.time() else None
    except:
        return {}

def getToken(credentials: HTTPAuthorizationCredentials = Depends(security)): 
    try: 
        token = credentials.credentials
        return token 
    except Exception as e: 
        raise HTTPException(status_code=404, detail="token not found")