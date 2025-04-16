from fastapi import HTTPException
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
# from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


my_posts = [
    {"title": "title of post 1", "content": "content of post1", "id": 1},
    {"title": "Favourite foods", "content": "I like pizza", "id": 2},
    {"title": "Tropical Climate", "content": "It can get as hot as 45c", "id": 3},
    {"title": "Desert Fune", "content": "Dubai is really fun in the summer", "id": 4}

]

while True:
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='fastapi',
            user='postgres',
            password='postgres',
            cursor_factory=RealDictCursor
        )

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("Database connection was successful")
        break
    except Exception as error:
        print("Database connection was not successful")
        print("Error: ", error)
    time.sleep(2)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


class Updatepost(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


def find_post_by_id(id: int):
    for p in my_posts:
        if p['id'] == id:
            return p
    return None


def find_post_index_by_id(id: int):
    for index, p in enumerate(my_posts):
        if p['id'] == id:
            return index
    return None


# @app.get("/")
# async def root():
#     return {"message": my_posts}


@app.get("/posts")
async def get_all_post():
    cursor.execute("""SELECT * FROM posts""")
    post = cursor.fetchall()
    print(post)
    return {"message": post}


@app.post("/createposts", status_code=status.HTTP_201_CREATED)
def create_posts(new_post: Post):
    print(new_post.title)

    # Convert Pydantic model to dictionary
    post_dict = new_post.model_dump()
    post_dict['id'] = randrange(0, 100000000)

    # Append the new post to the list
    my_posts.append(post_dict)
    print(my_posts)

    return {"data": post_dict}


@app.get("/posts/{id}")
def get_post_by_id(id: int, response: Response):
    post = find_post_by_id(id)
    if not post:

        # response.status_code= status.HTTP_404_NOT_FOUND
        # return {"message": f"Post with id {id} not found"}

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")

    return {"post_detail": post}


@app.delete("/posts/{id}")
def delete_post(id: int, post):
    # deleteing a post
    # find the index in the array of the post to be deleted
    # my_posts.pop(index)

    index = find_post_index_by_id(id)

    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Updatepost):
    # deleteing a post
    # find the index in the array of the post to be deleted
    # my_posts.pop(index)

    index = find_post_index_by_id(id)

    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    post_dict = post.model_dump()
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {"data": post_dict}

    # return {"post_detail": post_dict} # return {"post_detail": post}
