from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from legacy import check_user_inactivity, parse_threshold_from_text

app = Flask(__name__)
CORS(app)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/legacy-check", methods=["POST"])
def legacy_check_api():
    try:
        data = request.get_json(force=True)
        print("📨 Incoming data:", data)

        message = data.get("message", "")
        session_id = data.get("session_id", "")

        addr_match = re.search(r"([a-f0-9]{64})", message, re.IGNORECASE)
        email_match = re.search(r"[\w\.-]+@[\w\.-]+", message)
        threshold = parse_threshold_from_text(message)

        if not addr_match or not email_match:
            return jsonify({
                "response": "❌ Invalid format. Please use: <ICP_ADDRESS> <EMAIL> [threshold]"
            }), 400

        icp_address = addr_match.group(1)
        email = email_match.group(0)

        result = check_user_inactivity(email, icp_address, threshold)
        print("✅ Result from legacy.py:", result.dict())

        return jsonify({"response": result.message})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"response": f"❌ Internal server error: {str(e)}"}), 500

if __name__ == "__main__":
    print("🚀 Starting Legacy HTTP Wrapper on port 8020...")
    app.run(host="0.0.0.0", port=8020, debug=True)
