from pydantic import BaseModel
class UserData(BaseModel):
    name: str
    password: str

class User(UserData):
    id: int

class PostData(BaseModel):
    body: str

class Post(PostData):
    id: int

    
class CommentData(BaseModel):
    body: str
    post_id: int

class Comment(CommentData):
    id: int

class PostWithLikes(BaseModel):
    body: str
    likes: int