@echo off
echo 📊 Testing Both Visualization Modes
echo ===================================

echo.
echo 📋 This will test both visualization modes:
echo 1. Start backend server
echo 2. Test compact mode (sidebar)
echo 3. Test full mode (visualization tab)
echo 4. Verify data sharing between modes
echo.

echo 🔧 Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\Users\rohit\OneDrive\Desktop\Personal\RAG_LLM && python backend/app.py"

echo ⏳ Waiting for backend to start...
timeout /t 8 /nobreak > nul

echo.
echo 🧪 Running Both Modes Test...
python test_both_modes.py

echo.
echo 📊 Opening frontend to see both modes...
start http://localhost:3000

echo.
echo ✅ Test complete!
echo 📝 Check the results above and test both modes:
echo 🎨 1. Check sidebar - graph should be visible in compact mode
echo 🎨 2. Check visualization tab - graph should be visible in full mode
echo 🔄 Both modes should show the same data
echo.
pause
