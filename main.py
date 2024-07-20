import os
from fastapi import FastAPI, HTTPException, File, UploadFile
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import shutil
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uuid

from backend.worker import ask_whether_dirty

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ImageQuestionRequest(BaseModel):
    ref: str


class ImageQuestionResponse(BaseModel):
    answer: str
    is_dirty: bool
    imglink: str


# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)


Base.metadata.create_all(bind=engine)

# Create outdata directory if it doesn't exist
os.makedirs("outdata", exist_ok=True)


@app.post("/save_image/")
async def save_image(file: UploadFile = File(...)):
    print("Saving image")
    # Make a uuid for the file
    file.filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    # Save the file to the outdata directory
    file_location = f"outdata/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save the file name to the database
    db = SessionLocal()
    image = Image(name=file.filename)
    db.add(image)
    db.commit()
    db.refresh(image)
    db.close()

    return {"ref": file.filename}


@app.post("/question-whether-dirty/", response_model=ImageQuestionResponse)
async def generate_video(img: ImageQuestionRequest):
    try:
        # Find the image in the outdata directory
        img_path = f"outdata/{img.ref}"
        if not os.path.exists(img_path):
            raise ValueError("Image not found")
        img_path_abs = os.path.abspath(img_path)
        imq = ask_whether_dirty(img_path_abs)
        return ImageQuestionResponse(answer=imq.result, is_dirty=True, imglink=img.ref)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


app.mount("/outdata", StaticFiles(directory="./outdata", html=True), name="vids")
