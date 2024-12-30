from pydantic import BaseModel
from typing import List

class BooksBase(BaseModel):
    title: str
    author_id: int

class BooksCreate(BooksBase):
    pass
   
class Books(BooksBase):
    id: int
    author_id: int

    class Config:
        orm_mode = True
        author_id: int

class AuthorBase(BaseModel):
    name: str
    
class AuthorCreate(AuthorBase):
    pass

class Author(BaseModel):
    id: int
    name: str
    books: List[str]  

    class Config:
        orm_mode = True 

class AuthorWithBooks(BaseModel):
    id: int
    name: str
    books: List[Books]

    class Config:
        orm_mode = True

        