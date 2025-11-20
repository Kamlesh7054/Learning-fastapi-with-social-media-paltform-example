from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base

class Post(Base):
    __tablename__ = "posts"# table name in the database

    id = Column(Integer, primary_key=True, nullable=False)# primary key column
    title = Column(String, nullable=False)# title column
    content = Column(String, nullable=False)# content column
    published = Column(Boolean, server_default='TRUE', nullable=False)# published column
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))