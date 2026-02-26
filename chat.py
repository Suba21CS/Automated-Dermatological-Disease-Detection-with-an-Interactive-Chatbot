from flask import Blueprint, request, jsonify, render_template
import requests
import urllib.parse
import logging

# Define Blueprint
chat_bp = Blueprint("chat", __name__)

# Correct base URL for FDA API
FDA_API_BASE_URL = "https://api.fda.gov/drug/label.json?limit=10&search=indications_and_usage:{}"

# Mapping skin diseases to FDA-compatible terms
DISEASE_SEARCH_MAPPING = {
    "ekzama": "eczema",
    "enfeksiyonel": "skin infection",
    "akne": "acne",
    "pigment": "skin pigmentation",
    "benign": "benign skin lesion",
    "malign": "melanoma"  # changed from 'skin cancer'
}

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Route to render the chatbot UI
@chat_bp.route("/chat_ui")
def chat_ui():
    return render_template("chat.html")  # make sure chat.html exists


# Food guideline generator based on medicine name
def generate_food_guidelines(medicine_name):
    lower_name = medicine_name.lower()

    if "hydrocortisone" in lower_name or "ps-2896" in lower_name:
        return "Avoid excessive salty and processed foods. Eat potassium-rich foods like bananas and leafy greens."
    elif "isotretinoin" in lower_name:
        return "Avoid alcohol and vitamin A supplements while taking this medication."
    elif "aspirin" in lower_name:
        return "Avoid alcohol and NSAIDs. Take with food to prevent stomach upset."
    elif "metformin" in lower_name:
        return "Avoid excessive alcohol. Take with meals to reduce stomach discomfort."
    else:
        return "No specific food restrictions. Maintain a balanced diet."


# Route to handle medication lookup
@chat_bp.route("/get_medications", methods=["POST"])
def get_medications():
    try:
        # Get JSON data from request
        data = request.get_json()
        user_input = data.get("disease", "").strip().lower()

        if not user_input:
            return jsonify({"error": "Disease name is required"}), 400

        # Map to FDA term
        disease = DISEASE_SEARCH_MAPPING.get(user_input, user_input)
        encoded_disease = urllib.parse.quote(disease)

        # Make API request
        response = requests.get(FDA_API_BASE_URL.format(encoded_disease))

        if response.status_code == 404:
            logging.warning(f"No results found for disease: {disease}")
            return jsonify({
                "message": f"Sorry, no medications were found for '{user_input.title()}'. Please try a different or more specific medical term."
            }), 200
        elif response.status_code != 200:
            logging.error(f"FDA API request failed with status code {response.status_code}")
            return jsonify({"error": f"Failed to fetch data from FDA API. Status code: {response.status_code}"}), 500

        fda_data = response.json()
        medications = fda_data.get("results", [])

        if not medications:
            logging.info(f"No medications found for disease: {user_input}")
            return jsonify({
                "message": f"No specific medications found for '{user_input.title()}'. Try a different keyword."
            }), 200

        # Select medication with brand or generic name
        med = next((m for m in medications if "openfda" in m and (
            "brand_name" in m["openfda"] or "generic_name" in m["openfda"]
        )), medications[0])

        openfda_data = med.get("openfda", {})
        brand_name = (
            openfda_data.get("brand_name", [None])[0] or
            openfda_data.get("generic_name", [None])[0] or
            med.get("id", "Unknown")
        )

        usage = med.get("indications_and_usage", ["No usage details available"])
        warnings = med.get("warnings", ["No warnings available"])

        usage_info = usage[0] if usage else "No usage details available"
        warnings_info = warnings[0] if warnings else "No warnings available"

        food_guidelines = generate_food_guidelines(brand_name)

        single_med = {
            "brand_name": brand_name,
            "usage": usage_info if len(usage_info) > 50 else "No detailed usage found.",
            "warnings": warnings_info if len(warnings_info) > 50 else "No major warnings.",
            "food_guidelines": food_guidelines
        }

        return jsonify({"medication": single_med})

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {str(e)}")
        return jsonify({"error": f"Request error: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"Internal Server Error: {str(e)}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500
