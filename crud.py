from sqlalchemy.orm import Session
from models import Author, Books


def create_author(db: Session, name: str):
    db_author = Author(name=name)  
    db.add(db_author)
    db.commit()    
    return db_author


def get_author(db: Session, author_id:int):
    return db.query(Author).filter(Author.id == author_id).first()


def get_author_with_books(db: Session, author_id: int):
    author = db.query(Author).filter(Author.id == author_id).first()
    if author:
        author.books = db.query(Books).filter(Books.author_id == author_id).all()
    return author
    

def create_books(db: Session, title: str,  author_id: int):
    db_books = Books(title=title,  author_id=author_id)
    if db_books:
        db.add(db_books)
        db.commit()
    return db_books


# def get_books(db: Session, author_id:int):
#     return db.query(Author).filter(Author.id == author_id).first()

def update_author(db: Session, author_id: int, name:str):
    db_author = Author( author_id=author_id)
    if db_author:
        if name :
            db_author.name=name
    return db_author


def delete_author(db: Session, author_id: int):
    db_authors = Author( author_id=author_id)
    if db_authors:
        db.delete(db_authors)
        db.commit()
    return db_authors