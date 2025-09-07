@echo off
echo 📊 Testing TRUE Full Width Visualization
echo ========================================

echo.
echo 📋 This will test the TRUE full width fix:
echo 1. Start backend server
echo 2. Test bar chart generation
echo 3. Verify TRUE edge-to-edge layout
echo 4. Check no padding or margin constraints
echo.

echo 🔧 Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\Users\rohit\OneDrive\Desktop\Personal\RAG_LLM && python backend/app.py"

echo ⏳ Waiting for backend to start...
timeout /t 8 /nobreak > nul

echo.
echo 🧪 Running TRUE Full Width Test...
python test_true_full_width.py

echo.
echo 📊 Opening frontend to see TRUE full width...
start http://localhost:3000

echo.
echo ✅ Test complete!
echo 📝 Check the results above and test TRUE full width:
echo 🎨 1. Check visualization tab - should be edge-to-edge
echo 📏 2. Check no Card wrapper constraints
echo 📱 3. Check no padding or margin
echo 🔄 4. Should be TRUE full width from edge to edge
echo.
pause
