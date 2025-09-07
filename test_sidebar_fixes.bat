@echo off
echo 🔧 Testing Sidebar Fixes
echo ========================

echo.
echo 📋 This will test the sidebar fixes:
echo 1. Start backend server
echo 2. Test sidebar text visibility
echo 3. Test dynamic Quick Stats
echo 4. Test Pinned Insights functionality
echo 5. Test Recent Activity with real data
echo 6. Test graph visibility in visualization section
echo.

echo 🔧 Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\Users\rohit\OneDrive\Desktop\Personal\RAG_LLM && python backend/app.py"

echo ⏳ Waiting for backend to start...
timeout /t 8 /nobreak > nul

echo.
echo 🧪 Running Sidebar Fixes Test...
python test_sidebar_fixes.py

echo.
echo 📊 Opening frontend to see the fixed sidebar...
start http://localhost:3000

echo.
echo ✅ Test complete!
echo 📝 Check the results above to see if the sidebar fixes work
echo 🎨 The sidebar should now have:
echo    - Visible text with proper colors
echo    - Dynamic Quick Stats (not dummy data)
echo    - Working Pinned Insights
echo    - Real Recent Activity data
echo    - Reduced whitespace
echo    - Visible graphs in visualization section
echo.
pause
