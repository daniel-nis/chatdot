import google.generativeai as genai

genai.configure(api_key="AIzaSyB31TTDkSRm-PH7V61JIm7BloppLCy1F7I")
model = genai.GenerativeModel("gemini-2.0-flash-exp")
response = model.generate_content("Explain how AI works in 10 words")

print(response.text)