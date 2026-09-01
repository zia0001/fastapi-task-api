from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from database import (
    create_table,
    seed_tasks,
    get_all_tasks,
    get_task_by_id,
    create_task as db_create_task,
    delete_task as db_delete_task,
    update_task as db_update_task,
)



app = FastAPI(
    title="Task API",
    description="Simple CRUD API for managing tasks.",
    version="1.0"
)

create_table()

seed_tasks()



class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None
    



# Root endpoint: Returns basic information about the Task API
@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


# Health check endpoint: Confirms that the API server is running
@app.get("/health")
def health():
    return {
        "status": "ok"
    }
    

# Get all tasks: Returns all tasks in the database as a list of dictionaries
@app.get("/tasks")
def get_tasks():
    return get_all_tasks()


# Get single task: Returns a task by ID, or 404 if not found
@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    task = get_task_by_id(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return task
    

# Create task: Adds a new task with validation and returns status code 201
@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):

    if task.title.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Title is required"
        )

    return db_create_task(task.title)


# Update task: Updates title and/or completion status of an existing task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: TaskUpdate):

    if updated_task.title is not None:

        if updated_task.title.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Title is required"
            )

    task = db_update_task(
        task_id,
        updated_task.title,
        updated_task.done
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return task
    
# Delete task: Removes a task by ID and returns status code 204
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):

    deleted = db_delete_task(task_id)

    if deleted == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return Response(status_code=204)