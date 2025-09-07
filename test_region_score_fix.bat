@echo off
echo 🚀 Testing Region Score Pie Chart Fix
echo =====================================

echo.
echo 📋 This will test the fix for region score pie charts:
echo 1. Start backend server
echo 2. Test with the exact failing question
echo 3. Verify clean data without garbage values
echo.

echo 🔧 Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\Users\rohit\OneDrive\Desktop\Personal\RAG_LLM && python backend/app.py"

echo ⏳ Waiting for backend to start...
timeout /t 8 /nobreak > nul

echo.
echo 🧪 Running Final Region Score Pie Chart Fix Test...
python test_final_region_score_fix.py

echo.
echo 📊 Opening test HTML file...
start test_pie_chart_frontend.html

echo.
echo ✅ Test complete!
echo 📝 Check the results above to see if the fix worked
echo 📊 The pie chart should now show clean data [1.79, 0.44, 0.36]
echo    without garbage values like [statistics, to, columns, range, rows, nWest, nEast, nNorth]
echo.
pause
