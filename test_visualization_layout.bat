@echo off
echo 📊 Testing New Visualization Layout
echo ==================================

echo.
echo 📋 This will test the new visualization layout:
echo 1. Start backend server
echo 2. Test the new layout with pie chart
echo 3. Verify visualization appears in sidebar below Quick Actions
echo 4. Check clean data without garbage values
echo.

echo 🔧 Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\Users\rohit\OneDrive\Desktop\Personal\RAG_LLM && python backend/app.py"

echo ⏳ Waiting for backend to start...
timeout /t 8 /nobreak > nul

echo.
echo 🧪 Running Visualization Layout Test...
python test_visualization_layout.py

echo.
echo 📊 Opening frontend to see the new layout...
start http://localhost:3000

echo.
echo ✅ Test complete!
echo 📝 Check the results above to see if the new layout works
echo 🎨 The visualization should now appear in the sidebar below Quick Actions
echo    with a compact, professional design
echo.
pause
