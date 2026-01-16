from flask import Flask, render_template, request, jsonify
import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

genai.configure(api_key=api_key)

app = Flask(__name__)

# --- Helper: clean Gemini output ---
def clean_response(text: str) -> str:
    if not text:
        return ""
    # Remove Markdown bold markers
    text = text.replace("**", "")
    # Normalize multiple newlines
    text = re.sub(r'\n{2,}', '\n', text)
    # Convert bullets to dashes if needed
    text = text.replace("•", "-")
    return text.strip()

# --- Generate medicine info ---
def generate_medicine_info(medicine_name, strength=""):
    prompt = f"""
You are a professional medical information assistant.
Provide structured, educational information about the medicine. 
Do NOT give prescriptions or diagnosis.

Medicine name: {medicine_name}
Strength (if any): {strength}

Return the answer in bullet points or under subheadings, including:
- Composition
- Uses / Conditions treated
- Side effects
- Age restrictions (children / adults)
- When to take
- Approximate pricing in India
- Safety disclaimer

Always mention if the medicine is suitable for children or the recommended age group. 
Format the output clearly, using plain text bullets and new lines. Avoid bold or markdown.
"""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return clean_response(response.text)
    except Exception as e:
        return f"Error generating medicine info: {str(e)}"

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_medicine_info", methods=["POST"])
def get_medicine_info():
    data = request.get_json()
    medicine_name = data.get("medicine_name", "").strip()
    strength = data.get("strength", "").strip()

    if not medicine_name:
        return jsonify({"medicine_info": "Please enter a medicine name."})

    medicine_info = generate_medicine_info(medicine_name, strength)
    return jsonify({"medicine_info": medicine_info})

# --- Run ---
if __name__ == "__main__":
    app.run(debug=True)
   


