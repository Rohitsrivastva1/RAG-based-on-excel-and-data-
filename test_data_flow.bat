@echo off
echo 🔍 Testing Data Flow
echo ====================

echo.
echo 📋 This will test the data flow for visualization:
echo 1. Start backend server
echo 2. Test data flow to visualization component
echo 3. Check console logging for debug info
echo 4. Verify data structure handling
echo.

echo 🔧 Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\Users\rohit\OneDrive\Desktop\Personal\RAG_LLM && python backend/app.py"

echo ⏳ Waiting for backend to start...
timeout /t 8 /nobreak > nul

echo.
echo 🧪 Running Data Flow Test...
python test_data_flow.py

echo.
echo 📊 Opening frontend to see the data flow...
start http://localhost:3000

echo.
echo ✅ Test complete!
echo 📝 Check the results above and browser console for debug info
echo 🎨 The data flow should now work correctly with proper logging
echo    and the graph should be visible in the sidebar
echo.
pause
