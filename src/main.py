from fastapi import FastAPI, UploadFile, File
from typing import Optional
from pydantic import BaseModel
from model.SpeakerIdentification import test_model, train_model
app = FastAPI()

# class AudioFileUpload(BaseModel):
#     file: list[UploadFile]
#     folder_path: Optional[str] = "model/testing_set/"

class TestSpeaker(BaseModel):
    speaker: Optional[str]


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test")
async def test_speaker(test_speaker: TestSpeaker):
    ansSpeaker = test_model()
    return {"response": ansSpeaker}

@app.get("/train")
async def train_model():
    train_model()
    return {"response": "Model trained"}

# multiple files
@app.post("/upload_test_audio_file/")
async def upload_audio_file(file: UploadFile = File(...), folder_path: Optional[str] = "model/testing_set/"):
    contents = await file.read()
    with open(folder_path + file.filename, "wb") as f:
        f.write(contents)

    return {"message": "File uploaded successfully"}
