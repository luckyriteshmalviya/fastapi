from fastapi import Header, HTTPException

async def verifyTokenHeader(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")
    return "Foobar"