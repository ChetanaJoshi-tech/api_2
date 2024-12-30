from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import crud, schemas, models
from typing import List
import redis
import json
from fastapi.encoders import jsonable_encoder
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Tables created successfully!"}        

@app.post("/author/", response_model=schemas.Author)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    new_user = crud.create_author(db=db, name=author.name)
    # redis_client.set(f"author:{new_user.name}",json.dumps(new_user))

    return new_user

@app.get("/author/{author_id}", response_model=schemas.Author)
def get_author(author_id: int, db: Session = Depends(get_db)):
    
    author_cache = f"author:{author_id}"    
    cached_data = redis_client.get(author_cache)
    
    if cached_data:
        # Deserialize cached data into a Pydantic Author model
        print("using cache")
        try:
            cached_dict = json.loads(cached_data)
            if isinstance(cached_dict, dict): 
                return schemas.Author.parse_obj(cached_dict)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail="Error decoding cached data")
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Fetch from DB
    db_author = crud.get_author(db=db, author_id=author_id)
    
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    # Convert db_author (SQLAlchemy model) to dictionary that Pydantic can handle
    author_dict = {
        "id": db_author.id,
        "name": db_author.name,
        "books": [book.title for book in db_author.books]  # Assuming db_author.books is a relationship with book objects
    }
    
    # Cache the result
    redis_client.set(author_cache, json.dumps(author_dict, default=str), ex=60)  # Cache expiration set to 60 seconds
    
    return schemas.Author.parse_obj(author_dict)




@app.get("/author/{author_id}/books", response_model=schemas.AuthorWithBooks)
def get_author_and_books(author_id: int, books_id:int, db: Session = Depends(get_db)):
    cache_key = f"get_author_with_books:{author_id}:{books_id or 'all'}"

    cached_data = redis_client.get(cache_key)
    if cached_data:
        print('using cache')
        # Deserialize cached data and return it
        try:
            deserialized_data = json.loads(cached_data)
            return schemas.AuthorWithBooks.parse_obj(deserialized_data)
        except (json.JSONDecodeError, ValueError) as e:
            # Log error and fall back to database query if cache is corrupted
            print(f"Redis cache error: {e}")

   
    db_author = crud.get_author_with_books(db=db, author_id=author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")

    # Serialize data and store it in Redis
    serialized_data = jsonable_encoder(db_author)
    redis_client.set(cache_key, json.dumps(serialized_data), 60)  

    return db_author


     
@app.post("/books/", response_model=schemas.Books)
def create_books(book: schemas.BooksCreate, db: Session = Depends(get_db)):
    return crud.create_books(db=db, title=book.title, author_id=book.author_id)

@app.put("/author/{author_id}", response_model=schemas.Author)
def update_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    return crud.update_author(db=db, author_id=author.author_id, name=author.name)


@app.delete("/author/{author_id}", response_model=schemas.Author)
def delete_author(author: schemas.BooksCreate, db: Session = Depends(get_db)):
    db_author = crud.delete_author(db=db, author_id=author.author_id)
    return db_author