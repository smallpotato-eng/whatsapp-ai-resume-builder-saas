# WhatsApp AI Resume Builder Micro-SaaS

A WhatsApp-based AI resume service workflow with multilingual onboarding, PDPA consent, service selection, template previews, AI-assisted resume data collection, order ticketing, payment proof handling, and feedback collection.

This project demonstrates how an LLM-powered chatbot can be turned into a structured service business workflow, not just a text assistant.

## Demo Flow

1. User starts a WhatsApp conversation.
2. The bot asks the user to choose a language: Bahasa Malaysia, English, or Chinese.
3. The bot shows a PDPA consent message before collecting personal information.
4. User selects a service such as resume writing, resume improvement, ATS optimization, cover letter, or full package.
5. User selects a resume layout and template preview.
6. The AI collects resume information such as name, target role, education, work history, and skills.
7. Once information is complete, the system creates an order ticket.
8. User sends payment proof.
9. Admin receives a Telegram notification.
10. User is asked for feedback.

## Architecture

```mermaid
flowchart LR
    A[WhatsApp User] --> B[Baileys WhatsApp Bridge]
    B --> C[n8n State Machine Workflow]
    C --> D[Flask API]
    D --> E[SQLite Database]
    C --> F[Gemini / Groq LLM]
    F --> C
    C --> G[Template Preview Generator]
    C --> H[Order & Payment Flow]
    H --> I[Telegram Admin Alert]
    C --> B
    B --> J[User Receives Reply / Preview / Instructions]
    
What I Built
WhatsApp integration using Baileys and Express.js
n8n state-machine workflow for multi-step service flow
Flask API for sessions, conversations, orders, feedback, and template previews
SQLite database for persistent user sessions and order records
Multilingual onboarding flow
PDPA consent handling before collecting personal information
Resume service selection and pricing flow
Template preview selection
AI-assisted resume information extraction
Order ticket generation
Payment proof detection
Telegram admin notification
Feedback collection after payment
Key Features
Multilingual support: Bahasa Malaysia, English, and Chinese
Structured onboarding instead of open-ended chat
PDPA consent step for privacy-aware data collection
Service menu with pricing
Resume layout and template preview flow
Persistent session state
AI extraction of resume fields
Order number generation using RES-YYYYMMDD-XXXX
Payment proof handling
Admin notification workflow
Feedback collection
Tech Stack
Python
Flask
SQLite
JavaScript / Node.js
Express.js
Baileys WhatsApp API
n8n
Gemini API
Groq LLM API
Telegram Bot API
HTML resume templates
Why This Project Matters
Most chatbot demos stop at answering questions. This project shows how an AI assistant can support a real paid service workflow: onboarding, consent, product selection, information collection, order creation, payment handling, admin notification, and feedback.
It demonstrates practical LLM workflow design for service automation, customer operations, and micro-SaaS product prototyping.
Security Notice
This repository is a sanitized portfolio version.
The following are intentionally excluded:
Real API keys
WhatsApp sessions
Telegram bot tokens
Customer databases
Uploaded resumes or documents
Payment screenshots
Real payment account details
Private chat logs
Use .env.example to configure your own local credentials.
