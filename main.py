from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional
from pydantic import BaseModel, Field

app = FastAPI()
security = HTTPBasic()

# Simple user store
USER = {"username": "user", "password": "pass"}

def check_login(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username == USER["username"] and credentials.password == USER["password"]:
        return True
    raise HTTPException(status_code=401, detail="Invalid credentials")

class Particle(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=50)
    body: str = Field(..., min_length=1, max_length=1000)

class ParticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    body: str = Field(..., min_length=1, max_length=1000)

class ParticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=50)
    body: Optional[str] = Field(None, min_length=1, max_length=1000)

# In-memory store
particles: List[Particle] = [
    Particle(id=1, title="Welcome", body="This is your first note!"),
    Particle(id=2, title="FastAPI", body="Build APIs quickly."),
]

@app.post("/login")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username == USER["username"] and credentials.password == USER["password"]:
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/particles", response_model=List[Particle])
def search_particles(q: Optional[str] = None, login: bool = Depends(check_login)):
    if q:
        return [p for p in particles if q.lower() in p.title.lower()]
    return particles

@app.post("/particles", response_model=Particle)
def create_particle(data: ParticleCreate, login: bool = Depends(check_login)):
    new_id = max((p.id for p in particles), default=0) + 1
    new_particle = Particle(id=new_id, title=data.title, body=data.body)
    particles.append(new_particle)
    return new_particle

@app.get("/particles/{particle_id}", response_model=Particle)
def view_particle(particle_id: int, login: bool = Depends(check_login)):
    for p in particles:
        if p.id == particle_id:
            return p
    raise HTTPException(status_code=404, detail="Particle not found")

@app.put("/particles/{particle_id}", response_model=Particle)
def edit_particle(particle_id: int, data: ParticleUpdate, login: bool = Depends(check_login)):
    for p in particles:
        if p.id == particle_id:
            if data.title:
                p.title = data.title
            if data.body:
                p.body = data.body
            return p
    raise HTTPException(status_code=404, detail="Particle not found")
