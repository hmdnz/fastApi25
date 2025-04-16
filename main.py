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
import logging
logging.basicConfig(level=logging.DEBUG)


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


@app.post("/createpost", status_code=status.HTTP_201_CREATED)
def create_post(new_post: Post):
    cursor.execute(
        """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
        (new_post.title, new_post.content, new_post.published)
    )
    new_post_db = cursor.fetchone()
    conn.commit()
    return {"data": new_post_db}


@app.get("/posts/{id}")
def get_post_by_id(id: int, response: Response):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    post = cursor.fetchone()

    print(post)

    if not post:

        # response.status_code= status.HTTP_404_NOT_FOUND
        # return {"message": f"Post with id {id} not found"}

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")

    return {"post_detail": post}


from fastapi import HTTPException, status, Response
import logging

from fastapi import APIRouter, HTTPException, status, Response

router = APIRouter()

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    """
    Deletes a post by its ID.
    Returns 204 if successful, 404 if not found.
    """
    try:
        cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (str(id),))
        deleted_post = cursor.fetchone()
        conn.commit()

        if not deleted_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with ID {id} not found"
            )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except HTTPException:
        raise  # Let FastAPI handle your custom exceptions

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.put("/posts/{id}")
def update_post(id: int, post: Updatepost):  # Change UpdatePost to Updatepost here
    """
    Updates a post by its ID.
    Returns 200 if successful, 404 if not found.
    """
    try:
        # Attempt to update the post in the database
        cursor.execute(
            """UPDATE posts SET title = %s, content = %s WHERE id = %s RETURNING *""",
            (post.title, post.content, id)
        )
        updated_post = cursor.fetchone()
        conn.commit()

        # Check if a post was returned (i.e., if the ID was found)
        if updated_post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with ID {id} does not exist"
            )

        # Return the updated post details
        return {"data": updated_post}

    except HTTPException as e:
        # Re-raise HTTP exceptions (like 404)
        raise e
    except Exception as e:
        # If any other error occurs, raise a 500 error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )