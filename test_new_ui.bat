@echo off
echo 🎨 Testing New Enhanced UI
echo ==========================

echo.
echo 📋 This will test the new enhanced UI features:
echo 1. Start backend server
echo 2. Test the enhanced UI with pie chart
echo 3. Verify clean data without garbage values
echo 4. Check all UI enhancements
echo.

echo 🔧 Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\Users\rohit\OneDrive\Desktop\Personal\RAG_LLM && python backend/app.py"

echo ⏳ Waiting for backend to start...
timeout /t 8 /nobreak > nul

echo.
echo 🧪 Running New UI Test...
python test_new_ui.py

echo.
echo 📊 Opening frontend to see the new UI...
start http://localhost:3000

echo.
echo ✅ Test complete!
echo 📝 Check the results above to see if the new UI works
echo 🎨 The frontend should now show the enhanced professional UI
echo    with two-column layout, sidebar, and clean visualizations
echo.
pause
