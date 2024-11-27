from fastapi import status, APIRouter , Response,Request
from ..Models.User import User,Login,Sessiondb
from ..Db.db import Connect_mongo
import hashlib
import time
from datetime import datetime,timedelta,timezone
loginRoute = APIRouter()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_session_token(username: str) -> str:
    return f"{username}_{hash_password(username + str(time.time()))}"

def get_cookie_expiration(remember_me: bool) -> datetime:
    if remember_me:
        return (datetime.now(timezone.utc)+ timedelta(days=7))
    else: 
        return None

@loginRoute.post("/register")
def register(user: User,response:Response):
    data = Connect_mongo()["users"]
    existing_user = data.find_one({"email": user.email})
    if existing_user:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "email already exits"
    user.password = hash_password(user.password)
    data.insert_one(dict(user))
    response.status_code = status.HTTP_201_CREATED
    return {"message": "User registered successfully"}


@loginRoute.post("/login")
def login(user:Login,response:Response):
    connect = Connect_mongo()
    db = connect["users"]
    sessionData = connect["session"]
    userdata = db.find_one({"email": user.email},{"_id": False,"admin":0})
    if userdata is None or userdata["password"] != hash_password(user.password):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return("wrong pass or email")
    session_token = create_session_token(userdata["username"])
    cookie_expiration = get_cookie_expiration(user.remember_me)
    session = Sessiondb(username=userdata["username"],email=userdata["email"],token=session_token,expires_at=(datetime.now(timezone.utc)+ timedelta(hours=1) 
                                                                                                if cookie_expiration == None else cookie_expiration))
                                                                                                #value = to utc time + 1 hours if remember me false 
                                                                                                #otherwise utc time + 7 days
    sessionData.insert_one(dict(session))
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,  # Set to True when in production
        expires=cookie_expiration
    )
    return {"message": "Logged in successfully"}

@loginRoute.post("/logout")
def logout(response:Response,request:Request):
    db = Connect_mongo()["session"]
    token = request.cookies.get("session_token")
    db.find_one_and_delete({"token":token})
    response.delete_cookie("session_token")
    
    return {"message": "Logged out successfully"}