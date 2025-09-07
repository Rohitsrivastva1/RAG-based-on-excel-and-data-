@echo off
echo 🚀 Starting Pie Chart Test Environment
echo ======================================

echo.
echo 📋 Instructions:
echo 1. Backend will start on http://localhost:8000
echo 2. Frontend will start on http://localhost:3000
echo 3. Open test_pie_chart_frontend.html in browser for direct test
echo 4. Or use the React app and ask: "create pie chart for category vs no of user in each category"
echo.

echo 🔧 Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\Users\rohit\OneDrive\Desktop\Personal\RAG_LLM && python backend/app.py"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo 🌐 Starting Frontend...
start "Frontend" cmd /k "cd /d C:\Users\rohit\OneDrive\Desktop\Personal\RAG_LLM && npm start"

echo ⏳ Waiting for frontend to start...
timeout /t 10 /nobreak > nul

echo.
echo 🧪 Running API Tests...
python test_api_pie_chart.py

echo.
echo ✅ Test environment ready!
echo 📊 Open http://localhost:3000 in your browser
echo 📄 Or open test_pie_chart_frontend.html for direct test
echo.
pause
