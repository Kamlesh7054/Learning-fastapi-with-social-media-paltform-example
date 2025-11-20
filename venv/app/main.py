from typing import Optional
from fastapi import FastAPI, HTTPException, status, Depends, Response
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from sqlalchemy.orm import Session
from . import models # import models module
from .database import engine, get_db# get_db is a function to get a database session

models.Base.metadata.create_all(bind=engine) # create the database tables



app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True # default value is true
    # rating: Optional[int] = None # optional field


while True:

    try:
        # connect to an existing database with a cursor that returns dictionary-like rows
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres',
                                password='1234', cursor_factory=RealDictCursor)
        cursor = conn.cursor() # create a cursor object to interact with the database
        print("Database connection was successful")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error:", error)
        time.sleep(2)


'''.get() is http method for retrieving data from a server. there are multiple http
 methods like post, put, delete etc
 -> and "/" is the path for the root endpoint of the api
 -> if there two root endpoints it will give first one only
 '''



# creating a list of posts as a sample database
my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "favorite food", "content": "I love burger", "id": 2}]

# Function to find a post by id; returns the post dictionary if found, otherwise None
def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p

@app.get("/") 
def read_root():
    return {"message" : "Welcome to xyz_social_app!!!!"}




@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all() #query(models.Post) is the query which is abstract
                                        #representation of "select * from posts"
    return {"data": posts}




@app.get("/posts")# this endpoint will return a list of posts
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""select * from posts""")# execute the SQL query to fetch all posts but not storing the result
    # posts = cursor.fetchall() # fetch all the results from the executed query
    # print(posts)
    posts = db.query(models.Post).all() # ORM way to get all posts
    return {"data": posts}



@app.post("/posts", status_code = status.HTTP_201_CREATED) # this endpoint will create a new post
def create_post(post: Post, db: Session = Depends(get_db)):
    # cursor.execute("""insert into posts (title, content, published) values(%s, %s, %s) returning *""",
    #                 (post.title, post.content, post.published))
    # new_post = cursor.fetchone() # fetch the newly created post
    # conn.commit() # commit the transaction to save changes to the database

    # ORM way to create a new post
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)

    #scalable way to create a new post
    new_post = models.Post(**post.dict()) # more efficient way to create a new post
                                        # ** unpacks the dictionary returned by post.dict() into keyword arguments
    db.add(new_post) # add the new post to the session
    db.commit() # commit the transaction to save changes to the database
    db.refresh(new_post) # work as returning * in raw sql to get the newly created post with id
    return {"data": new_post} # return the newly created post

#retriving one individual post by id
@app.get("/posts/{id}") # path parameter
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""select * from posts where id = %s""", (str(id),)) # execute the SQL query to fetch post by id
    # post = cursor.fetchone() # fetch the result from the executed query

    # filter works as "where" clause in sql and first() returns the first result of the query
    post = db.query(models.Post).filter(models.Post.id == id).first() # ORM way to get the post by id

    if not post:
        #handle error if post not found using HTTPException; 
        # you should import HTTPException and status from fastapi
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT) # delete a post by id
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""delete from posts where id = %s returning *""", (str(id),))
    # delete_post = cursor.fetchone()
    # conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)# get the post to be deleted

    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} does not exist")
    
    post.delete(synchronize_session=False)# delete the post
    db.commit()# commit the transaction
    return Response(status_code=status.HTTP_204_NO_CONTENT) # no content to return
   

def find_post_index(id):
    """
    Returns the index of the post with the given id in my_posts, or None if not found.
    """
    for index, p in enumerate(my_posts):
        if p['id'] == id:
            return index
    return None

@app.put("/posts/{id}") # update a post by id
def update_post(id: int, post_data: Post, db: Session = Depends(get_db)):
    # cursor.execute("""update posts set title = %s, content = %s, published = %s where id = %s
    #                returning *""", (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)# get the post to be updated
    
    db_post = post_query.first()# fetch the post to be updated
    
    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"post with id: {id} does not exist") 
    
    post_query.update(post_data.model_dump(), synchronize_session=False)# update the post with new data
    db.commit()# commit the transaction
    
    return {"data": post_query.first()}# return the updated post
    
