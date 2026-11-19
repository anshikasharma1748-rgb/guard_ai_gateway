
import os
import re
import io
import pytesseract

from PIL import Image
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Tesseract OCR location
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

app = FastAPI(title="GuardAI Gateway")

# Frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini configuration
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY missing in .env file")

client = genai.Client(api_key=api_key)


class ChatRequest(BaseModel):
    prompt: str


# Privacy masking
def mask_sensitive_data(text):
    patterns = {
        "Email": r'\b[\w.-]+@[\w.-]+\.\w+\b',
        "Phone": r'(?<!\d)(?:\+91[- ]?)?[6-9]\d{9}(?!\d)',
        "Aadhaar": r'(?<!\d)\d{4}[\s-]?\d{4}[\s-]?\d{4}(?!\d)',
        "Roll Number": r'(?i)(?<=roll no:\s)[A-Z0-9/-]+',
        "Name": r'(?im)(?<=name:\s)[A-Za-z][A-Za-z .\'-]{1,}',
        "Father Name": r'(?im)(?<=father name:\s)[A-Za-z][A-Za-z .\'-]{1,}',
        "Address": r'(?im)(?<=address:\s).+'
    }

    masked_text = text
    detected_risks = []

    for label, pattern in patterns.items():
        if re.search(pattern, masked_text):
            detected_risks.append(label)
            masked_text = re.sub(
                pattern,
                "[REDACTED]",
                masked_text
            )

    return masked_text, detected_risks


# Common Gemini response function
 
def get_ai_response(user_text, image_data=None, mime_type=None):

    contents = ["""
You are GuardAI, a professional and friendly college student assistant.

COMMUNICATION RULES:
1. Always be polite, respectful, professional and friendly.
2. Never use slang or informal words like "Arey dost", "tu", or "tune".
3. Address users respectfully using "aap" in Hindi and Hinglish.
4. Reply in the same language and script used by the user.
5. Give clear, simple and step-by-step guidance.
6. Never repeat the user's question unnecessarily.
7. Never invent facts or missing information.
8. If information is missing, ask the user politely.

FORM FILLING RULES:
1. Identify visible form fields from the uploaded image.
2. Explain each field separately.
3. Tell the student exactly what information belongs in each field.
4. Never guess personal details.
5. Do not fill office-use-only sections meant for college staff.
6. If the image is unclear, explain which part cannot be read.

IMAGE RULES:
1. If an image is attached, inspect the actual image.
2. Never claim that an uploaded image was not provided.
3. Do not pretend to see image details that are unclear.
4. Use both the image and extracted OCR text when available.

PRIVACY RULES:
1. Never invent or expose masked personal information.
2. Do not attempt to guess redacted information.

Write a helpful and professional response.
""", user_text]

    if image_data:
        contents.append(
            types.Part.from_bytes(
                data=image_data,
                mime_type=mime_type
            )
        )

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=contents,
        config=types.GenerateContentConfig(
            max_output_tokens=1000,
            thinking_config=types.ThinkingConfig(
                thinking_level="low"
            )
        )
    )

    if not response.text:
        raise Exception("Gemini returned an empty response")

    return response.text

   



@app.get("/")
def home():
    return {"status": "GuardAI Backend is running"}


@app.get("/health")
def health():
    return {"status": "connected"}


# Chat endpoint
@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        masked_prompt, detected_risks = mask_sensitive_data(
            request.prompt
        )

        ai_answer = get_ai_response(masked_prompt)


        return {
            "masked_prompt": masked_prompt,
            "privacy_audit": {
                "is_safe": len(detected_risks) == 0,
                "detected_risks": detected_risks
            },
            "ai_response": ai_answer
        }

    except Exception as e:
        print("GEMINI ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="AI response could not be generated. Please try again."
        )


# Document upload and OCR endpoint
@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    prompt: str = Form(default="")
):
    try:
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(
                status_code=400,
                detail="Only JPG and PNG images are allowed"
            )

        image_data = await file.read()

        if len(image_data) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Image size must be below 5 MB"
            )

        image = Image.open(io.BytesIO(image_data))
        image.verify()

        image = Image.open(io.BytesIO(image_data))
        extracted_text = pytesseract.image_to_string(image)

       
            

        combined_text = (
            prompt + "\n\nDocument text:\n" + extracted_text
        )

        masked_text, detected_risks = mask_sensitive_data(
            combined_text
        )

        ai_answer = get_ai_response(
            masked_text,
            image_data=image_data,
            mime_type=file.content_type
        )

        return {
            "masked_text": masked_text,
            "privacy_audit": {
                "is_safe": len(detected_risks) == 0,
                "detected_risks": detected_risks
            },
            "ai_response": ai_answer
        }

    except HTTPException:
        raise

    except Exception as e:
        print("UPLOAD ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Document processing failed. Please try again."
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8003
    )
