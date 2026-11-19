# 🛡️ GuardAI Gateway – Privacy-Focused AI Security

## 📌 Project Overview
GuardAI Gateway is a privacy-focused AI security project designed to protect users' sensitive personal information while interacting with AI models like Google Gemini.

It detects sensitive information such as names, phone numbers, email addresses, roll numbers, and other personal details, and automatically masks them before forwarding user queries to the AI model.

## 🎯 Objectives
- Protect sensitive personal information.
- Reduce the risk of exposing personal data to external AI models.
- Provide a secure way to interact with AI systems.
- Promote privacy-aware AI usage.

## ✨ Key Features
- Automatic Personal Identifiable Information (PII) Detection.
- Sensitive Data Masking.
- Google Gemini API Integration.
- Image Upload Support.
- OCR (Optical Character Recognition) using Tesseract.
- Privacy Audit for detecting sensitive information.

## 🛠️ Technologies Used
- Python
- FastAPI
- Google Gemini API
- HTML
- Tesseract OCR
- Pillow
- Regular Expressions (Regex)

## ⚙️ How It Works
1. User enters a query or uploads an image.
2. GuardAI detects sensitive personal information.
3. Identified information is automatically masked.
4. The processed query is forwarded to Google Gemini.
5. The AI response is displayed to the user.

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/anshikasharma1748-rgb/guard_ai_gateway.git
```

Open the project folder:

```bash
cd guard_ai_gateway
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your Gemini API key in a `.env` file.

Run the application:

```bash
uvicorn main:app --reload
```

## 🔐 Privacy & Security
GuardAI Gateway uses automated detection and masking techniques to reduce the exposure of sensitive personal information during AI interactions.

## 👩‍💻 Developer
**Anshika Sharma**

## 📌 Project Status
Developed as a Privacy-Focused AI Security Project.
