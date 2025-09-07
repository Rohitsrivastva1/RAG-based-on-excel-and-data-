@echo off
echo 📱 Testing Manifest.json Fix
echo ============================

echo.
echo 📋 This will test the manifest.json fix:
echo 1. Start frontend server
echo 2. Test manifest.json endpoint
echo 3. Verify no 404 errors
echo 4. Check PWA configuration
echo.

echo 🔧 Starting Frontend Server...
start "Frontend Server" cmd /k "cd /d C:\Users\rohit\OneDrive\Desktop\Personal\RAG_LLM && npm start"

echo ⏳ Waiting for frontend to start...
timeout /t 10 /nobreak > nul

echo.
echo 🧪 Running Manifest Fix Test...
python test_manifest_fix.py

echo.
echo 📱 Opening frontend to see clean console...
start http://localhost:3000

echo.
echo ✅ Test complete!
echo 📝 Check the results above and test manifest fix:
echo 🎨 1. Check browser console - no manifest errors
echo 📏 2. Check Network tab - manifest.json loads successfully
echo 📱 3. Check PWA features work properly
echo 🔄 4. No more 404 Not Found errors
echo.
pause
