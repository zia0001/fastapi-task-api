from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from auth import AuthRequest
from supabase_client import supabase
from database import (
    create_table,
    seed_tasks,
    get_all_tasks,
    get_task_by_id,
    create_task,
    update_task,
    delete_task,
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
@app.post("/auth/signup", status_code=201)
def signup(auth_data: AuthRequest):
    if not auth_data.email or not auth_data.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    try:
        response = supabase.auth.sign_up({
            "email": auth_data.email,
            "password": auth_data.password
        })

        return {
            "message": "User created successfully",
            "user": {
                "id": response.user.id,
                "email": response.user.email
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    


@app.post("/auth/login")
def login(auth_data: AuthRequest):
    if not auth_data.email or not auth_data.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    try:
        response = supabase.auth.sign_in_with_password({
            "email": auth_data.email,
            "password": auth_data.password
        })

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    

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
def create_task_endpoint(task: TaskCreate):

    if task.title.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Title is required"
        )

    return create_task(task.title)


# Update task: Updates title and/or completion status of an existing task
@app.put("/tasks/{task_id}")
def update_task_endpoint(task_id: int, updated_task: TaskUpdate):

    if updated_task.title is not None:
        if updated_task.title.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Title is required"
            )

    task = update_task(
        task_id,
        title=updated_task.title,
        done=updated_task.done
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return task
    
# Delete task: Removes a task by ID and returns status code 204
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task_endpoint(task_id: int):

    deleted = delete_task(task_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return Response(status_code=204)