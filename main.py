from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import SessionLocal, ToDo

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ToDoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class ToDoResponse(ToDoCreate):
    id: int

    class Config:
        orm_mode = True

# GET /todos - Retrieve all to-do items
@app.get("/todos", response_model=List[ToDoResponse])
def get_todos(db: Session = Depends(get_db)):
    return db.query(ToDo).all()

# POST /todos - Create a new to-do item
@app.post("/todos", response_model=ToDoResponse)
def create_todo(todo: ToDoCreate, db: Session = Depends(get_db)):
    new_todo = ToDo(
        title=todo.title, 
        description=todo.description, 
        completed=todo.completed
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

# GET /todos/{todo_id} - Retrieve a to-do item by ID
@app.get("/todos/{todo_id}", response_model=ToDoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="ToDo not found")
    return todo

# PUT /todos/{todo_id} - Update a to-do item by ID
@app.put("/todos/{todo_id}", response_model=ToDoResponse)
def update_todo(todo_id: int, todo: ToDoCreate, db: Session = Depends(get_db)):
    existing_todo = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if not existing_todo:
        raise HTTPException(status_code=404, detail="ToDo not found")
    
    existing_todo.title = todo.title
    existing_todo.description = todo.description
    existing_todo.completed = todo.completed
    
    db.commit()
    db.refresh(existing_todo)
    return existing_todo

# DELETE /todos/{todo_id} - Delete a to-do item by ID
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="ToDo not found")
    
    db.delete(todo)
    db.commit()
    return {"message": "ToDo deleted successfully"}
