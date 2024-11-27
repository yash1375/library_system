from ..Db.db import Connect_mongo
from fastapi import Request , HTTPException
from datetime import datetime,timezone

async def loginAndPerm(request:Request):
    '''
    Function that User session is valid or not 
    and return role 
    '''
    session = request.cookies.get("session_token")
    #cookie not exist
    if session == None:
        raise HTTPException(status_code=401 ,detail={"message": "please login"})
    #checking information in database
    db = Connect_mongo()["session"]
    sessionCheck = db.find_one({"token":session})
    if (sessionCheck == None):
        raise HTTPException(status_code=401 ,detail={"message": "session expiry"})
    # checking if session expire or not 
    elif sessionCheck["expires_at"] < datetime.now(timezone.utc).replace(tzinfo=None):
        db.find_one_and_delete(sessionCheck)
        request.cookies.pop("session_token")
        raise HTTPException(status_code=401 ,detail={"message": "session Expire"})
    # finding and returning user role
    db = Connect_mongo()["users"]
    try:
        permission = db.find_one({"email":sessionCheck["email"]})["admin"]
    except:
        raise HTTPException(status_code=500 ,detail={"message": "something wrong"})
    return permission 
