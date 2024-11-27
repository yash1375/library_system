from fastapi import APIRouter , Response , status,UploadFile,File,Form,Depends,HTTPException
from ..Db.db import Connect_mongo
from ..Models.Books import CollectionOfBook , Book 
from ..Dependencies.Dependencies import loginAndPerm
from gridfs import GridFS
from typing import Annotated
from bson.objectid import ObjectId
from typing import Annotated

booksRoute = APIRouter()

def databaseConnect(collection):
    return Connect_mongo().get_collection(collection)


@booksRoute.get("/books/")
def getBooks(response:Response,permission: Annotated[bool, Depends(loginAndPerm)]): # does not required permission here but login checking required
    booksData = databaseConnect("books")
    return CollectionOfBook(books=booksData.find().to_list()).model_dump()

@booksRoute.get("/books/{book_id}")
def getbook(book_id,response:Response,permission: Annotated[bool, Depends(loginAndPerm)]):  # does not required permission here but login checking required
    bookData = databaseConnect("books")
    book = bookData.find_one({"book_id":ObjectId(book_id)},{"_id": False})
    print(book)
    if book is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"book not found"}
    return Book(**book)


@booksRoute.post("/books/",)
async def insertbook(
    response : Response,
    permission: Annotated[bool, Depends(loginAndPerm)],
    title: str = Form(...),
    author: str = Form(...),
    genre: str = Form(...) , 
    file : UploadFile = File(...),):
    # checking role 
    if permission == False:
        raise HTTPException(401,{"message":"Don't have permission"})
    db = databaseConnect("books")
    fs = GridFS(Connect_mongo())
    try:
        # upload data to mongodb gridfs
        bookId = fs.put(file.file,filename=file.filename, content_type=file.content_type)
        book = Book(title=title,author=author,genre=genre,book_id=bookId)
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"File upload failed": str(e)}
    db.insert_one(dict(book))
    return {"message": "Book uploaded successfully", "book_id": str(bookId)}

@booksRoute.delete("/books/{book_id}")
async def deletebook(book_id,resonse:Response,permission: Annotated[bool, Depends(loginAndPerm)]):
    # checking role 
    if permission == False:
        raise HTTPException(401,{"message":"Don't have permission"})
    db = databaseConnect("books")
    fs = GridFS(Connect_mongo())
    try:
        fs.delete(ObjectId(book_id))
        find = db.find_one_and_delete({"book_id":ObjectId(book_id)})
        if not find:
            resonse.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "book not found"}
    except Exception as e:
        resonse.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        print(str(e))
        return {"message": "somethong bad happands"}
    return {"message" : "delete succesful"}

@booksRoute.put("/books/{book_id}")
async def updatebook(book_id,
                     response:Response,
                     permission: Annotated[bool, Depends(loginAndPerm)],
                     title: str = Form(...) ,
                     author: str = Form(...) ,
                     genre: str = Form(...), 
                     file: UploadFile = None):
    if permission == False:
        raise HTTPException(401,{"message":"Don't have permission"})
    db = databaseConnect("books")
    update = {}
    # not good i know 
    if title:
        update["title"] = title
    if author:
        update["author"] = author
    if genre:
        update["genre"] = genre
    find = db.find_one({"book_id":ObjectId(book_id)})
    if not find:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "book not found"}
    if file:
        try:
            # delete and upload new file if given
            fs = GridFS(Connect_mongo())
            fs.delete(ObjectId(book_id))
            bookId = fs.put(file.file,filename=file.filename, content_type=file.content_type)
            update["book_id"] = bookId
        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"File upload failed": str(e)}
    #update data
    db.find_one_and_update(find,{'$set':update})
    return {"message:success"}
