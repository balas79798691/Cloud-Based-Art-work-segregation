from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
import shutil
from datetime import datetime


app = FastAPI(title="CloudCanvas")


# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Folder for uploaded artwork
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Make uploaded images accessible
app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_FOLDER),
    name="uploads"
)


# -------------------------
# Database
# -------------------------

def create_database():

    connection = sqlite3.connect("database.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artworks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            category TEXT NOT NULL,
            image_url TEXT NOT NULL,
            uploaded_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


create_database()


# -------------------------
# Upload Artwork
# -------------------------

@app.post("/upload")
async def upload_artwork(
    file: UploadFile = File(...),
    category: str = Form(...)
):

    filename = file.filename

    # Simple image validation
    allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

    extension = os.path.splitext(filename)[1].lower()

    if extension not in allowed_extensions:
        return {
            "error": "Only image files are allowed."
        }

    # Prevent filename conflicts
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    new_filename = f"{timestamp}_{filename}"

    file_path = os.path.join(
        UPLOAD_FOLDER,
        new_filename
    )

    # Save image
    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # Save metadata
    connection = sqlite3.connect("database.db")

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO artworks
        (filename, category, image_url, uploaded_at)
        VALUES (?, ?, ?, ?)
    """, (
        filename,
        category,
        f"/uploads/{new_filename}",
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()

    return {
        "message": "Artwork uploaded successfully",
        "filename": filename,
        "category": category
    }


# -------------------------
# Get Artwork
# -------------------------

@app.get("/artworks")
def get_artworks():

    connection = sqlite3.connect("database.db")

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM artworks
        ORDER BY id DESC
    """)

    artworks = cursor.fetchall()

    connection.close()

    return [dict(artwork) for artwork in artworks]


# -------------------------
# Home
# -------------------------

@app.get("/")
def home():

    return {
        "message": "Welcome to CloudCanvas API"
    }