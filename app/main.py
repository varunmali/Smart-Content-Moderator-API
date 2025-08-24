from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Smart Content Moderator API is running."}
