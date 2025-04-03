from fastapi import APIRouter, HTTPException, Depends,Request
import sqlalchemy
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from storeapi.models.post import Post, PostData, Comment, CommentData, User, UserData,PostWithLikes,loginData
from storeapi.database import database, post_table, comment_table, user_table,like_table
from storeapi.security import createToken, get_password_hash, verify_password, get_current_user
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

class PostSorting(str, Enum):
    asc = "asc"
    desc = "desc"
select_post_with_likes=sqlalchemy.select(post_table,sqlalchemy.func.count(like_table.c.id).label("likes")).select_from(post_table.outerjoin(like_table)).group_by(post_table.c.id).group_by(post_table.c.id)

@router.post("/signup")
async def signup(user: UserData,request:Request):
    data=user.model_dump()
    query=user_table.select().where(user_table.c.email==data["email"])
    existing_user=await database.fetch_one(query)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    data["password"]=get_password_hash(data["password"])
    data["verified"]=False
    query=user_table.insert().values(**data)
    user_id=await database.execute(query)
    token=createToken( data["email"],"auth",user_id)
    logger.info(f"User {data['name']} created with id {user_id}")
    verify_token=createToken( data["email"],"verify",user_id)
    return {"id":user_id,"token":token,"verify_token":verify_token,"url":request.url_for("verify_user",token=verify_token)}

@router.post("/login")
async def login(user: loginData):
    data=user.model_dump()
    query=user_table.select().where(user_table.c.email==data["email"])
    existing_user=await database.fetch_one(query)
    if not existing_user:
        raise HTTPException(status_code=400, detail="User does not exist")
    if not verify_password(data["password"], existing_user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect password")
    token=createToken(data["email"],"auth",existing_user["id"])
    return {"message":"Login successful","token":token}
@router.post("/post", response_model=Post)
async def create_post(post:PostData,credentials:HTTPAuthorizationCredentials=Depends(security)):
    current_user=await get_current_user(credentials.credentials,"auth")
    print(current_user)
    if current_user["verified"]==False:
        raise HTTPException(status_code=400, detail="User not verified")
    data=post.model_dump()
    data["owner"]=current_user["id"]
    query=post_table.insert().values(**data)
    post_id=await database.execute(query)
    return {**data,"id":post_id}
@router.post("/comment", response_model=Comment)
async def create_comment(comment:CommentData,credentials=Depends(security)):
    current_user=await get_current_user(credentials.credentials,"auth")
    print(current_user)
    if current_user["verified"]==False:
        raise HTTPException(status_code=400, detail="User not verified")
    data=comment.model_dump()
    query=post_table.select().where(post_table.c.id==data["post_id"])
    existing_post=await database.fetch_one(query)
    if not existing_post:
        raise HTTPException(status_code=400, detail="Post does not exist")
    data["owner"]=current_user["id"]
    query=comment_table.insert().values(**data)
    comment_id=await database.execute(query)
    return {**data,"id":comment_id}
@router.get("/posts")#logging query in file and console
async def get_posts(sorting: PostSorting=PostSorting.desc):
    if(sorting==PostSorting.asc):
        query=select_post_with_likes.order_by(post_table.c.id.asc())
    else:
        query=select_post_with_likes.order_by(post_table.c.id.desc())
    logger.info("Fetching all posts")
    posts=await database.fetch_all(query)
    logger.debug(query)
    return posts
@router.get("/comments", response_model=list[Comment])
async def get_comments():
    query=comment_table.select()
    comments=await database.fetch_all(query)
    return comments
@router.get("/post/{id}/owner")
async def get_post_owner(id:int):
    query=post_table.select().where(post_table.c.id==id)
    post=await database.fetch_one(query)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    query=user_table.select().where(user_table.c.id==post["owner"])
    user=await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"name":user["name"]}

@router.post("/authenticate/{token}")
async def getuserbytoken(token:str):
    return get_current_user(token,"auth")


@router.post("/like/{post_id}")
async def like_post(post_id:int,credentials:HTTPAuthorizationCredentials=Depends(security)):
    current_user=get_current_user(credentials.credentials,"auth")
    query=post_table.select().where(post_table.c.id==post_id)
    existing_post=await database.fetch_one(query)
    if not existing_post:
        raise HTTPException(status_code=400, detail="Post does not exist")
    query=like_table.insert().values(post_id=post_id)
    await database.execute(query)
    return {"message":"Post liked successfully"}


@router.get("/post/{post_id}",response_model=PostWithLikes)
async def get_post(post_id:int):
    query=select_post_with_likes.where(post_table.c.id==post_id)
    post=await database.fetch_one(query)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/verify/{token}")
async def verify_user(token:str):
    try:
        payload=await get_current_user(token,"verify")
        query=user_table.select().where(user_table.c.id==payload["id"])
        user=await database.fetch_one(query)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        query=user_table.update().where(user_table.c.id==payload["id"]).values(verified=True)
        await database.execute(query)
        return {"message":"User verified successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
