from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional


app = FastAPI(
    title="Task API",
    description="Simple CRUD API for managing tasks.",
    version="1.0"
)



class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None
    
tasks = [
    {
        "id": 1,
        "title": "Study FastAPI",
        "done": False
    },
    {
        "id": 2,
        "title": "Buy groceries",
        "done": True
    },
    {
        "id": 3,
        "title": "Complete assignment",
        "done": False
    }
]



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
    

# Get all tasks: Returns the complete list of tasks
@app.get("/tasks")
def get_tasks():
    return tasks


# Get single task: Returns a task by ID, or 404 if not found
@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )
    

# Create task: Adds a new task with validation and returns status code 201
@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):

    if task.title.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Title is required"
        )

    new_task = {
        "id": len(tasks) + 1,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)

    return new_task


# Update task: Updates title and/or completion status of an existing task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: TaskUpdate):

    for task in tasks:

        if task["id"] == task_id:

            if updated_task.title is not None:

                if updated_task.title.strip() == "":
                    raise HTTPException(
                        status_code=400,
                        detail="Title is required"
                    )

                task["title"] = updated_task.title

            if updated_task.done is not None:
                task["done"] = updated_task.done

            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )
    
    
# Delete task: Removes a task by ID and returns status code 204
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):

    for task in tasks:

        if task["id"] == task_id:
            tasks.remove(task)
            return Response(status_code=204)

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )