# Google AI Studio API Key Working Test
# Install first:
# pip install google-generativeai

import google.generativeai as genai

# 🔑 Paste your Google AI Studio API Key here
API_KEY = "AIzaSyCAWvXTxwk_Dqm1rVSrXO8fHMRfT9pjPxE"

try:
    # Configure API
    genai.configure(api_key=API_KEY)

    # Load model
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Send test prompt
    response = model.generate_content("Hello, are you working?")

    print("✅ API Key is Working!")
    print("Response:", response.text)

except Exception as e:
    print("❌ API Key Not Working!")
    print("Error:", e)