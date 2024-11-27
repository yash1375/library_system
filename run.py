from fastapi import FastAPI
from src.Router import LoginRoute
from src.Router import BookRoute
import uvicorn

app = FastAPI()

app.include_router(LoginRoute.loginRoute)

app.include_router(BookRoute.booksRoute)

if __name__ == ("__main__"):
    uvicorn.run(app=app)

