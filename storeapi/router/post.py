from fastapi import APIRouter, HTTPException
from storeapi.models.post import Post, PostData, Comment, CommentData, User, UserData
from storeapi.database import database, post_table, comment_table, user_table
import logging
logger = logging.getLogger(__name__)
router = APIRouter()
@router.post("/signup", response_model=User)
async def signup(user: UserData):
    data=user.model_dump()
    query=user_table.select().where(user_table.c.name==data["name"])
    existing_user=await database.fetch_one(query)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    query=user_table.insert().values(**data)
    user_id=await database.execute(query)
    return {**data,"id":user_id}

@router.post("/post", response_model=Post)
async def create_post(post:PostData):
    data=post.model_dump()
    query=user_table.select().where(user_table.c.id==data["owner"])
    existing_user=await database.fetch_one(query)
    if not existing_user:
        raise HTTPException(status_code=400, detail="User does not exist")
    query=post_table.insert().values(**data)
    post_id=await database.execute(query)
    return {**data,"id":post_id}
@router.post("/comment", response_model=Comment)
async def create_comment(comment:CommentData):
    data=comment.model_dump()
    query=user_table.select().where(user_table.c.id==data["owner"])
    existing_user=await database.fetch_one(query)
    if not existing_user:
        raise HTTPException(status_code=400, detail="User does not exist")
    query=post_table.select().where(post_table.c.id==data["post_id"])
    existing_post=await database.fetch_one(query)
    if not existing_post:
        raise HTTPException(status_code=400, detail="Post does not exist")
    query=comment_table.insert().values(**data)
    comment_id=await database.execute(query)
    return {**data,"id":comment_id}
@router.get("/posts", response_model=list[Post])#logging query in file and console
async def get_posts():
    query=post_table.select()
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
