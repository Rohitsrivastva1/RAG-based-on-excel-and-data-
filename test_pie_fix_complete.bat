@echo off
echo 🚀 Testing Pie Chart Fix - Complete System
echo ==========================================

echo.
echo 📋 This will test the complete pie chart fix:
echo 1. Start backend server
echo 2. Test pie chart generation with real counts
echo 3. Verify the fix works end-to-end
echo.

echo 🔧 Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\Users\rohit\OneDrive\Desktop\Personal\RAG_LLM && python backend/app.py"

echo ⏳ Waiting for backend to start...
timeout /t 8 /nobreak > nul

echo.
echo 🧪 Running Pie Chart Fix Tests...
python test_full_system_pie_fix.py

echo.
echo 📊 Opening test HTML file...
start test_pie_chart_frontend.html

echo.
echo ✅ Test complete!
echo 📝 Check the results above to see if the fix worked
echo 📊 The pie chart should now show real counts [2500, 2968, 3964, 3055, 2144]
echo    instead of row counts [8, 6, 6, 6, 4]
echo.
pause
