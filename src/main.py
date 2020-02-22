from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'])


@app.get("/welcome")
def root():
    print('got request')
    return {"message": "Hello World"}