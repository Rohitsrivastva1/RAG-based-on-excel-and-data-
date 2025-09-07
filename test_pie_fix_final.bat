@echo off
echo 🚀 Testing Final Pie Chart Fix
echo ==============================

echo.
echo 📋 This will test the complete pie chart fix:
echo 1. Start backend server
echo 2. Test with the exact failing question
echo 3. Verify real counts are used instead of junk tokens
echo.

echo 🔧 Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\Users\rohit\OneDrive\Desktop\Personal\RAG_LLM && python backend/app.py"

echo ⏳ Waiting for backend to start...
timeout /t 8 /nobreak > nul

echo.
echo 🧪 Running Complete Pie Chart Fix Test...
python test_complete_pie_fix.py

echo.
echo 📊 Opening test HTML file...
start test_pie_chart_frontend.html

echo.
echo ✅ Test complete!
echo 📝 Check the results above to see if the fix worked
echo 📊 The pie chart should now show real counts [3964, 3055, 2968, 2500, 2144]
echo    instead of junk tokens [range, statistics, 22, 23, 24, to, 19, columns, rows]
echo.
pause
