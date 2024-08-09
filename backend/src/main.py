from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os

from uuid import UUID, uuid4

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

MONGODB_CONNECTION_STRING = os.environ["MONGODB_CONNECTION_STRING"]


# MongoDB client setup
client = AsyncIOMotorClient(MONGODB_CONNECTION_STRING, uuidRepresentation="standard")
db = client.todolist  # Replace with your database name
todos = db.todos  # Replace with your collection name

class TodoItem(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    content: str

class TodoItemCreate(BaseModel):
    content: str

@app.post('/todos', response_model=TodoItem)
async def create_todo(item: TodoItemCreate):
    new_todo = TodoItem(content=item.content)

    await todos.insert_one(new_todo.model_dump(by_alias=True))

    return new_todo

@app.get('/todos', response_model=list[TodoItem])
async def get_todos():
    return await todos.find().to_list(length=None)


@app.delete('/todos/{id}')
async def delete_todo(id: UUID):
    result = await todos.delete_one({"_id": id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")

    return {"detail": "Deleted innit?."}