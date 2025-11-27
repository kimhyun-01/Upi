from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Allowed API Keys
ALLOWED_KEYS = {
    "123": "Free User",
    "456": "Premium",
    "admin987": "Admin"
}

def check_api_key(req):
    api_key = req.headers.get("x-api-key") or req.args.get("key")
    if not api_key:
        return False, "Missing API key"
    if api_key not in ALLOWED_KEYS:
        return False, "Invalid API key"
    return True, "OK"

@app.route("/api/upi", methods=["GET"])
def upi_lookup():
    # API Key Check
    valid, msg = check_api_key(request)
    if not valid:
        return jsonify({"error": msg}), 403

    upi_id = request.args.get("upi_id")
    if not upi_id:
        return jsonify({"error": "Missing parameter: upi_id"}), 400

    # STEP 1 → NEW WORKING UPI VERIFY API
    verify_url = f"https://api.vpa.verification.plus/?vpa={upi_id}"

    try:
        resp = requests.get(verify_url, timeout=10).json()
    except:
        return jsonify({"error": "UPI API request failed"}), 500

    if resp.get("status") != "success":
        return jsonify({"upi_valid": False, "message": "Invalid UPI ID"}), 200

    upi_name = resp.get("name")
    ifsc = resp.get("ifsc")

    # STEP 2 → Get Bank Address using Razorpay IFSC API
    bank_details = {}
    if ifsc:
        try:
            bank_details = requests.get(f"https://ifsc.razorpay.com/{ifsc}", timeout=10).json()
        except:
            bank_details = {"error": "Could not fetch bank details"}

    return jsonify({
        "success": True,
        "input_upi": upi_id,
        "upi_valid": True,
        "upi_name": upi_name,
        "ifsc": ifsc,
        "bank_details": bank_details
    }), 200


if __name__ == "__main__":
    app.run()
