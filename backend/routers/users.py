from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from users_auth.authentication import AuthHandler
from models.car_model import CurrentUserModel, LoginModel, UserModel


router = APIRouter()
auth_handler = AuthHandler()

@router.post("/register", response_description="Register a new user")
async def register(
    request: Request,
    new_user: LoginModel = Body(...)
) -> UserModel:
    """
    Register a new user with a username and password.
    """
    users = request.app.db["users"]
    
    new_user.password = auth_handler.get_password_hash(new_user.password)
    new_user = new_user.model_dump()
    # Check if the username already exists
    if (
        existing_user := await users.find_one({"username": new_user["username"]})
        is not None
    ):
        raise HTTPException(
            status_code=409,
            detail=f"User with username {new_user['username']} already exists"
        )
    verified_user = await users.insert_one(new_user)
    created_user = await users.find_one({"_id": verified_user.inserted_id})
    return created_user 

@router.post("/login", response_description="Login a user")
async def login(
    request: Request,
    login_data: LoginModel = Body(...)
) -> str:   
    """
    Login a user and return a JWT token
    """
    users = request.app.db["users"]
    
    user = await users.find_one({"username": login_data.username})
    if (user is None) or (
        not auth_handler.verify_password(login_data.password, user["password"])
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username and/or password"
        )
    token = auth_handler.encode_token(str(user["_id"]), user["username"])
    response = JSONResponse(
        content={
            "token": token,
            "username": user["username"]
        }
    )
    return response

@router.get(
    "/me",
    response_description="Get current user",
    response_model=CurrentUserModel
)
async def get_current_user(
    request: Request,
    response: Response,
    user_data= Depends(auth_handler.auth_wrapper)
) -> CurrentUserModel:
    """
    Get the current logged-in user.
    """
    users = request.app.db["users"]
    user = await users.find_one({"_id": ObjectId(user_data["user_id"])})
    
    return user