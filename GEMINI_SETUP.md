# 🚀 Gemini API Setup Guide

## ⚠️ **REQUIRED: API Key Configuration**

Your RAG Analytics system **REQUIRES** either a **Google Gemini API** or **OpenAI API** key to function. The system no longer supports fallback mode and will fail to start without proper API configuration.

## 🔑 **How to Get Your Gemini API Key**

### **Step 1: Get API Key**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy your API key

### **Step 2: Set Environment Variable**
Choose one of these methods:

#### **Method A: Environment Variable (Recommended)**
```bash
# Windows PowerShell
$env:GOOGLE_API_KEY="your_gemini_api_key_here"

# Windows Command Prompt
set GOOGLE_API_KEY=your_gemini_api_key_here

# Linux/Mac
export GOOGLE_API_KEY="your_gemini_api_key_here"
```

#### **Method B: .env File**
Create a `.env` file in your project root:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

#### **Method C: Alternative Variable Names**
The system also supports:
- `GEMINI_API_KEY`
- `GOOGLE_API_KEY` (preferred)

## 🧪 **Test Your Setup**

1. **Start the backend:**
   ```bash
   python enhanced_backend.py
   ```

2. **Check the logs** - you should see:
   ```
   Initialized Gemini LLM
   ```

3. **Test with a question:**
   - Upload a CSV file
   - Ask: "What is the average salary?"
   - You should see `Query Type: pandas_agent` instead of `fallback_default`

## 🎯 **Benefits of Gemini**

- **✅ More Accessible**: Easier to get API key
- **✅ Cost-Effective**: Often cheaper than OpenAI
- **✅ High Quality**: Excellent for data analysis tasks
- **✅ Fast**: Quick response times
- **✅ Reliable**: Google's infrastructure

## 🔄 **API Key Priority**

The system automatically tries:
1. **Gemini API** (if `GOOGLE_API_KEY` is set) - **RECOMMENDED**
2. **OpenAI API** (if `OPENAI_API_KEY` is set)
3. **❌ SYSTEM FAILS** (if no API keys are available)

## 🚨 **Troubleshooting**

### **System fails to start?**
- Check your API key is set correctly
- Verify the key is valid and active
- Check the logs for detailed error messages

### **API Key Invalid?**
- Verify the key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Make sure there are no extra spaces
- Try regenerating the key

### **Need Help?**
- Check the backend logs for detailed error messages
- Ensure `langchain-google-genai` is installed: `pip install langchain-google-genai`

## 🎉 **You're All Set!**

Once configured, your RAG Analytics system will use Gemini for intelligent data analysis, making it much more powerful than the basic fallback mode!
