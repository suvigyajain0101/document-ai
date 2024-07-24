import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
from transformers import pipeline
from pydantic import BaseModel
import textwrap

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

# Define the maximum number of tokens for the model
MAX_TOKENS = 1024

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def chunk_text(text, max_length):
    """
    Break text into chunks that are smaller than max_length.
    """
    return textwrap.wrap(text, width=max_length)

class FilenameRequest(BaseModel):
    filename: str

class PromptRequest(BaseModel):
    prompt: str
    filename: str

@app.post("/upload")
async def upload_file(request: FilenameRequest):
    filename = request.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Extract text from the PDF
    text = extract_text_from_pdf(file_path)
    
    # Chunk the text into manageable sizes
    chunks = chunk_text(text, MAX_TOKENS)
    
    return JSONResponse(content={'num_chunks': len(chunks)})

@app.post("/generate")
async def generate_text(request: PromptRequest):
    prompt = request.prompt
    filename = request.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Extract text from the PDF
    document_text = extract_text_from_pdf(file_path)
    
    # Chunk the document text to fit the model's maximum token limit
    chunks = chunk_text(document_text, MAX_TOKENS - len(prompt))
    
    responses = []
    
    for chunk in chunks:
        combined_text = f"{chunk}\n\nUser Prompt: {prompt}"
        # Generate a response using the chunk of text
        response = generator(combined_text, max_new_tokens=100)
        responses.append(response[0]['generated_text'])
    
    # Combine all generated responses
    combined_response = " ".join(responses)
    
    return JSONResponse(content={'generated_text': combined_response})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
