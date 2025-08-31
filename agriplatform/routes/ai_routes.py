from flask import Flask, render_template, Blueprint, request, jsonify
from agriplatform.utils.translator import t
from flask_wtf.csrf import CSRFProtect
from flask_login import login_required
import openai

ai_bp = Blueprint('ai', __name__)
#openai.api_key = os.getenv("OPENAI_API_KEY")

@ai_bp.route('/ai-assistant')
def ai_assistant():
    return render_template('ai_assistant.html', t=t)

@ai_bp.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').lower().strip()

    # District to crops mapping (simplified but realistic)
    district_crops = {
        "blantyre": ["maize", "beans", "sweet potatoes", "groundnuts"],
        "lilongwe": ["maize", "soybeans", "groundnuts", "sunflower"],
        "mzimba": ["maize", "tobacco", "beans", "potatoes"],
        "thyolo": ["tea", "maize", "beans", "vegetables"],
        "mangochi": ["rice", "maize", "cassava", "groundnuts"],
        "nsanje": ["sorghum", "maize", "millet", "cotton"],
        "zomba": ["maize", "beans", "cassava", "vegetables"],
        "kasungu": ["maize", "tobacco", "soybeans", "groundnuts"],
        "chikwawa": ["sugarcane", "maize", "cotton", "sorghum"],
        "karonga": ["rice", "maize", "cassava", "bananas"]
    }

    # Keyword categories
    crop_keywords = ["crop", "maize", "cassava", "groundnuts", "beans", "rice", "sweet potatoes", "sorghum", "millet", "tobacco", "tea"]
    weather_keywords = ["weather", "rain", "temperature", "forecast", "climate"]
    register_keywords = ["register", "sign up", "create account", "join"]
    greeting_keywords = ["hello", "hey", "hi", "greetings", "muli bwanji", "moni"]
    pest_keywords = ["pest", "armyworm", "weevil", "aphid", "caterpillar", "locust", "disease"]
    fertilizer_keywords = ["fertilizer", "manure", "compost", "urea", "npk", "fertiliser"]
    market_keywords = ["market", "price", "sell", "buy"]
    irrigation_keywords = ["irrigation", "watering", "sprinkler", "drip"]
    soil_keywords = ["soil", "ph", "fertility", "topsoil", "erosion"]
    livestock_keywords = ["livestock", "goat", "cow", "cattle", "chicken", "pig", "sheep"]
    thanks_keywords = ["thanks", "thank you", "zikomo"]

    # Match logic
    if any(word in user_input for word in crop_keywords):
        reply = "Malawi farmers grow maize, beans, groundnuts, cassava, rice, and more. Tell me your district for tailored advice."
    elif any(word in user_input for word in weather_keywords):
        reply = "You can check the weather by selecting your district during registration, or I can share general seasonal tips."
    elif any(word in user_input for word in register_keywords):
        reply = "To register, go to the 'Register' page and fill in your details. It's quick and free!"
    elif any(word in user_input for word in greeting_keywords):
        reply = "Hello there! 👋 How can I help you with your farming today?"
    elif user_input in district_crops:
        crops = ", ".join(district_crops[user_input])
        reply = f"In {user_input.title()}, farmers often grow: {crops}."
    elif any(word in user_input for word in pest_keywords):
        reply = "Pests like armyworms and aphids can damage crops. Inspect your field regularly and use early treatment to prevent losses."
    elif any(word in user_input for word in fertilizer_keywords):
        reply = "Fertilizers like NPK and Urea boost crop yield, while compost improves soil in the long run."
    elif any(word in user_input for word in market_keywords):
        reply = "Market prices change daily. Visit your nearest market or check our Market section for updates."
    elif any(word in user_input for word in irrigation_keywords):
        reply = "Drip irrigation saves water, and sprinklers cover large areas. Water early in the morning or evening."
    elif any(word in user_input for word in soil_keywords):
        reply = "Healthy soil is the foundation of good farming. Test pH, add organic matter, and prevent erosion."
    elif any(word in user_input for word in livestock_keywords):
        reply = "Livestock farming is profitable. Keep shelters clean, vaccinate, and feed animals well."
    elif "hope" in user_input:
        reply = "He is the CEO of AgriConnect and the proud creator of me. 😉"
    elif any(word in user_input for word in thanks_keywords):
        reply = "You're welcome! Happy farming! 🌱"
    else:
        reply = "I'm still learning! Try asking about crops, weather, pests, soil, livestock, or your district."

    return jsonify({"reply": reply})


