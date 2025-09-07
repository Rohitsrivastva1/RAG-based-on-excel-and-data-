@echo off
echo 📊 Testing Full Width Visualization
echo ===================================

echo.
echo 📋 This will test full width visualization:
echo 1. Start backend server
echo 2. Test bar chart generation
echo 3. Verify full width in visualization tab
echo 4. Check responsive layout
echo.

echo 🔧 Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\Users\rohit\OneDrive\Desktop\Personal\RAG_LLM && python backend/app.py"

echo ⏳ Waiting for backend to start...
timeout /t 8 /nobreak > nul

echo.
echo 🧪 Running Full Width Test...
python test_full_width.py

echo.
echo 📊 Opening frontend to see full width...
start http://localhost:3000

echo.
echo ✅ Test complete!
echo 📝 Check the results above and test full width:
echo 🎨 1. Check visualization tab - should be full width
echo 📏 2. Check height - should be 500px (not shrunk)
echo 📱 3. Check responsive layout
echo 🔄 4. Both compact and full modes should work
echo.
pause
