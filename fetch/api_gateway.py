from fastapi import FastAPI, Request
import uvicorn
from agent import process_query
import asyncio

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fluffy-computing-machine-pxv46g79v9wf9r5v-5173.app.github.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    question = data.get("question", "")

    class DummyCtx:
        logger = type("logger", (), {"info": print, "error": print})()

    # Jalankan process_query di event loop
    answer = await process_query(question, DummyCtx())
    return {"answer": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8083)