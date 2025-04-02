import databases
import sqlalchemy
from storeapi.config import config
metadata = sqlalchemy.MetaData()
user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(255)),
    sqlalchemy.Column("password", sqlalchemy.String(255)),
)
post_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String(255)),
    sqlalchemy.Column("owner",sqlalchemy.ForeignKey("users.id"),nullable=False)
)
comment_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String(255)),
    sqlalchemy.Column("post_id",sqlalchemy.ForeignKey("posts.id"),nullable=False),
    sqlalchemy.Column("owner",sqlalchemy.ForeignKey("users.id"),nullable=False)
)
like_table=sqlalchemy.Table(
    "likes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("post_id",sqlalchemy.ForeignKey("posts.id"),nullable=False)
)
engine=sqlalchemy.create_engine(config.DATABASE_URL,connect_args={"check_same_thread":False})
metadata.create_all(engine)
database=databases.Database(config.DATABASE_URL,force_rollback=config.DB_FORCE_ROLL_BACK)