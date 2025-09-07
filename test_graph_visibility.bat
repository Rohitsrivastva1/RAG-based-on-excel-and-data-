@echo off
echo 📊 Testing Graph Visibility
echo ==========================

echo.
echo 📋 This will test the graph visibility fixes:
echo 1. Start backend server
echo 2. Test graph visibility in sidebar
echo 3. Check compact mode rendering
echo 4. Verify Plotly charts are visible
echo.

echo 🔧 Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\Users\rohit\OneDrive\Desktop\Personal\RAG_LLM && python backend/app.py"

echo ⏳ Waiting for backend to start...
timeout /t 8 /nobreak > nul

echo.
echo 🧪 Running Graph Visibility Test...
python test_graph_visibility.py

echo.
echo 📊 Opening frontend to see the graph visibility...
start http://localhost:3000

echo.
echo ✅ Test complete!
echo 📝 Check the results above to see if the graph is now visible
echo 🎨 The graph should now be visible in the sidebar visualization section
echo    with proper compact mode rendering
echo.
pause
