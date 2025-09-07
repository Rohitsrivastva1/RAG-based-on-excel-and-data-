@echo off
echo 🔧 Testing UI Fixes
echo ===================

echo.
echo 📋 This will test the UI fixes:
echo 1. Start backend server
echo 2. Test the fixed UI with pie chart
echo 3. Verify no compilation errors
echo 4. Check clean data without garbage values
echo.

echo 🔧 Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\Users\rohit\OneDrive\Desktop\Personal\RAG_LLM && python backend/app.py"

echo ⏳ Waiting for backend to start...
timeout /t 8 /nobreak > nul

echo.
echo 🧪 Running UI Fixes Test...
python test_ui_fixes.py

echo.
echo 📊 Opening frontend to see the fixed UI...
start http://localhost:3000

echo.
echo ✅ Test complete!
echo 📝 Check the results above to see if the UI fixes work
echo 🎨 The frontend should now compile and run without errors
echo    with the enhanced professional UI
echo.
pause
