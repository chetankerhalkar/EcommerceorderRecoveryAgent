from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .agent import run_recovery, load_status

app = FastAPI(title="Order Recovery Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/start')
def start_agent():
    status = run_recovery()
    return {"status": "started", "result": status}

@app.get('/status')
def get_status():
    status = load_status()
    return status or {"status": "idle"}

