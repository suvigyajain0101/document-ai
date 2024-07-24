import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
from transformers import pipeline
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory where files are saved
UPLOAD_FOLDER = 'uploads'

# Load the smaller language model
model_name = "distilgpt2"
generator = pipeline('text-generation', model=model_name)

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

class FilenameRequest(BaseModel):
    filename: str

class PromptRequest(BaseModel):
    prompt: str

@app.post("/upload")
async def upload_file(request: FilenameRequest):
    filename = request.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    text = extract_text_from_pdf(file_path)
    return JSONResponse(content={'text': text})

@app.post("/generate")
async def generate_text(request: PromptRequest):
    prompt = request.prompt
    response = generator(prompt, max_length=100, num_return_sequences=1)
    generated_text = response[0]['generated_text']
    return JSONResponse(content={'generated_text': generated_text})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
