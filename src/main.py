from fastapi import FastAPI, UploadFile, File
from typing import Optional
from pydantic import BaseModel
import boto3 , os
from io import BytesIO
from model.SpeakerIdentification import test_model, train_model
from src.s3 import uplaodtoS3
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


@app.post("/upload")
async def upload(audioFile: UploadFile = File(...), audioPathType: Optional[str]= "testing_set") :
    try:
        # read the file content as bytes
        content = await audioFile.read()
        # create a file object from the bytes content
        file = BytesIO(content)
        print(type(file),audioPathType )
        # upload the file to S3
        # url = uplaodtoS3(request.audioPathType, request.audioFile.filename, file)
        return 'url'
    except Exception as e:
        print(e)
        return "Error uploading file to S3"

# path type can be testing_set or training_set or model according the folderpath will be testing_set/ or training_set/ or trained_models/ and we can upload

    