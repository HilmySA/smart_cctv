from fastapi import FastAPI
from app.routes.routes import router
from app.middleware.cors import add_cors

app = FastAPI()
add_cors(app)
app.include_router(router)