from fastapi import FastAPI, UploadFile, File
from typing import Optional
import os
from pydantic import BaseModel
from model.SpeakerIdentification import test_model, train_model
app = FastAPI()



@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test")
async def test_speaker(test_speaker: str):
    ansSpeaker = test_model()

    ansSpeaker = ansSpeaker.split("/")[-1]
    correct = False
    if ansSpeaker == test_speaker:
        correct = True
    return {"response": ansSpeaker, "correct": correct}
   


@app.get("/train")
async def train_model():
    train_model()
    return {"response": "Model trained"}

# multiple files
@app.post("/upload_test_audio_file/")
async def upload_audio_file(file: UploadFile = File(...), folder_path: Optional[str] = "model/testing_set/"):
    contents = await file.read()
    with open(folder_path + 'sample.wav', "wb") as f:
        f.write(contents)
    
    if folder_path == "model/training_set/":
        with open(folder_path + file.filename, "wb") as f:
            f.write(contents)
        
        with open("model/training_set_addition.txt", "a") as f:
            f.write(file.filename + "\n")
    print(os.listdir(folder_path))

    return {"message": "File uploaded successfully", 'files': os.listdir(folder_path) }
