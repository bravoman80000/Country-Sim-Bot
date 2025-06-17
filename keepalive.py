from fastapi import FastAPI
import threading
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Bot is awake."}

def run():
    uvicorn.run(app, host="0.0.0.0", port=8080)

def keep_alive():
    thread = threading.Thread(target=run)
    thread.start()
