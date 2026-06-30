@echo off
echo Starting Resume-AI...

echo [1/3] Starting n8n on port 5678...
start "Resume-AI n8n" cmd /k "n8n start"

timeout /t 5 /nobreak >nul

echo [2/3] Starting Flask API on port 5051...
start "Resume-AI Flask" cmd /k "cd /d ${PROJECT_ROOT}\resume-ai\api && python app.py"

timeout /t 3 /nobreak >nul

echo [3/3] Starting Baileys WhatsApp on port 3001...
start "Resume-AI Baileys" cmd /k "cd /d ${PROJECT_ROOT}\resume-ai\whatsapp && node index.js"

echo.
echo Resume-AI started. Scan QR code in the Baileys window.
echo n8n UI: http://localhost:5678
