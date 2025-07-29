import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
CORS(app)  

phones_db = {}


PLATFORM_FEES = {
    "PlatformX": {"type": "percentage", "value": 0.10},  
    "PlatformY": {"type": "mixed", "percentage": 0.08, "flat": 2.00},  
    "PlatformZ": {"type": "percentage", "value": 0.12}   
}

CONDITION_MAPPING = {
    "Like New": {
        "PlatformX": "New",
        "PlatformY": "3 Stars (Excellent)",
        "PlatformZ": "New"
    },
    "Good": {
        "PlatformX": "Good",
        "PlatformY": "2 Stars (Good)",
        "PlatformZ": "As New"
    },
    "Fair": {
        "PlatformX": "Scrap",
        "PlatformY": "1 Star (Usable)",
        "PlatformZ": "Good"
    }
}

DESIRED_PROFIT_MARGIN = 0.20  # 20% profit margin

def calculate_selling_price(base_cost, platform_name):
    """
    Calculates the minimum selling price for a phone on a given platform
    to achieve the desired profit margin after platform fees.
    """
    fee_info = PLATFORM_FEES.get(platform_name)
    if not fee_info:
        print(f"Error: Unknown platform '{platform_name}' in calculate_selling_price.")
        return None

    
    target_revenue = base_cost * (1 + DESIRED_PROFIT_MARGIN)

    selling_price = None
    if fee_info["type"] == "percentage":
        fee_percentage = fee_info["value"]
        if (1 - fee_percentage) <= 0:
            print(f"Error: Fee percentage for {platform_name} is too high ({fee_percentage*100}%), cannot calculate selling price.")
            return None
        selling_price = target_revenue / (1 - fee_percentage)
    elif fee_info["type"] == "mixed":
        fee_percentage = fee_info["percentage"]
        flat_fee = fee_info["flat"]
        if (1 - fee_percentage) <= 0:
            print(f"Error: Fee percentage for {platform_name} is too high ({fee_percentage*100}%), cannot calculate selling price.")
            return None
        selling_price = (target_revenue + flat_fee) / (1 - fee_percentage)
    else:
        print(f"Error: Unknown fee type '{fee_info['type']}' for platform '{platform_name}'.")
        return None

    
    if selling_price is not None and selling_price < base_cost:
        print(f"Warning: Calculated selling price ({selling_price:.2f}) for {platform_name} is less than base cost ({base_cost:.2f}).")
        return None

    return round(selling_price, 2)

def get_platform_condition(internal_condition, platform_name):
    """
    Maps an internal phone condition to a platform-specific condition string.
    Returns "Unknown" if no mapping is found.
    """
    return CONDITION_MAPPING.get(internal_condition, {}).get(platform_name, "Unknown")

@app.route('/')
def serve_index():
    """
    Serves the index.html file from the root directory.
    This is typically the entry point for the frontend application.
    """
    return send_from_directory('.', 'index.html')

@app.route('/api/phones', methods=['GET'])
def get_phones():
    """
    Retrieves a list of all phones in the inventory,
    including calculated selling prices and listing statuses for each platform.
    """
    all_phones_data = []
    for phone_id, phone in phones_db.items():
        phone_details = phone.copy() 
        phone_details['id'] = phone_id
        phone_details['platform_listings'] = {}
        phone_details['not_listed_reasons'] = []

        phone_details['is_sold_b2b_or_direct_flag'] = phone_details['sold_b2b_or_direct']

        if phone_details['stock'] <= 0:
            phone_details['is_listed'] = False
            phone_details['not_listed_reasons'].append("Out of Stock")
            
            for platform_name in PLATFORM_FEES.keys():
                phone_details['platform_listings'][platform_name] = {
                    "selling_price": None, 
                    "mapped_condition": get_platform_condition(phone_details['condition'], platform_name),
                    "can_list": False
                }
            all_phones_data.append(phone_details)
            continue 

        if phone_details['sold_b2b_or_direct']:
            phone_details['not_listed_reasons'].append("Sold B2B/Direct")

        is_listable_on_any_platform = False
        
        for platform_name in PLATFORM_FEES.keys():
            selling_price = calculate_selling_price(phone_details['base_cost'], platform_name)
            platform_condition = get_platform_condition(phone_details['condition'], platform_name)

            
            is_profitable = selling_price is not None
            can_list_on_platform = is_profitable

            phone_details['platform_listings'][platform_name] = {
                "selling_price": selling_price,
                "mapped_condition": platform_condition,
                "can_list": can_list_on_platform
            }

            if not is_profitable:
                phone_details['not_listed_reasons'].append(f"Unprofitable on {platform_name}")
            
            if can_list_on_platform:
                is_listable_on_any_platform = True
        
        phone_details['is_listed'] = is_listable_on_any_platform and \
                                      phone_details['stock'] > 0 and \
                                      not phone_details['sold_b2b_or_direct']

        if not is_listable_on_any_platform and not phone_details['not_listed_reasons']:
            phone_details['not_listed_reasons'].append("Unprofitable on all platforms")

        all_phones_data.append(phone_details)

    all_phones_data.sort(key=lambda x: (not x.get('is_listed', False), x['model'].lower()))
    return jsonify(all_phones_data)

@app.route('/api/phones', methods=['POST'])
def add_phone():
    """
    Adds a new phone to the inventory.
    Requires 'model', 'base_cost', 'condition', and 'stock' in the request body.
    """
    data = request.json
    model = data.get('model')
    base_cost = data.get('base_cost')
    condition = data.get('condition')
    stock = data.get('stock')

    if not all([model, base_cost, condition, stock is not None]):
        return jsonify({"error": "Missing required fields (model, base_cost, condition, stock)"}), 400

    try:
        base_cost = float(base_cost)
        stock = int(stock)
        if base_cost <= 0:
            return jsonify({"error": "Base cost must be greater than 0"}), 400
        if stock < 0:
            return jsonify({"error": "Stock cannot be negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid base_cost or stock format. Must be numbers."}), 400

    # Validate phone condition
    if condition not in CONDITION_MAPPING:
        return jsonify({"error": f"Invalid condition. Must be one of: {', '.join(CONDITION_MAPPING.keys())}"}), 400

    phone_id = str(uuid.uuid4())
    phones_db[phone_id] = {
        "model": model,
        "base_cost": base_cost,
        "condition": condition,
        "stock": stock,
        "sold_b2b_or_direct": False 
    }
    return jsonify({"message": "Phone added successfully", "phone_id": phone_id}), 201

@app.route('/api/phones/<phone_id>', methods=['PUT'])
def update_phone(phone_id):
    """
    Updates an existing phone's stock or sold_b2b_or_direct status.
    """
    data = request.json
    phone = phones_db.get(phone_id)

    if not phone:
        return jsonify({"error": "Phone not found"}), 404

    # Update stock if provided
    if 'stock' in data:
        try:
            new_stock = int(data['stock'])
            if new_stock < 0:
                return jsonify({"error": "Stock cannot be negative."}), 400
            phone['stock'] = new_stock
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid stock format. Must be an integer."}), 400

    # Update sold_b2b_or_direct status if provided
    if 'sold_b2b_or_direct' in data:
        if isinstance(data['sold_b2b_or_direct'], bool):
            phone['sold_b2b_or_direct'] = data['sold_b2b_or_direct']
        else:
            return jsonify({"error": "sold_b2b_or_direct must be a boolean (true/false)"}), 400

    return jsonify({"message": "Phone updated successfully", "phone": phone}), 200

@app.route('/api/login', methods=['POST'])
def login():
    """
    Mock login endpoint for demonstration purposes.
    In a real application, this would involve proper user authentication,
    password hashing, and secure token generation (e.g., JWT).
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Hardcoded credentials for demo
    if username == "admin" and password == "password123":
        return jsonify({"message": "Login successful", "token": "mock_token_123"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

if __name__ == '__main__':
    # Populate the in-memory database with dummy data on startup
    phones_db['phone-001'] = {
        "model": "iPhone 12 Pro",
        "base_cost": 400.00,
        "condition": "Like New",
        "stock": 5,
        "sold_b2b_or_direct": False
    }
    phones_db['phone-002'] = {
        "model": "Samsung Galaxy S21",
        "base_cost": 300.00,
        "condition": "Good",
        "stock": 3,
        "sold_b2b_or_direct": False
    }
    phones_db['phone-003'] = {
        "model": "Google Pixel 5",
        "base_cost": 200.00,
        "condition": "Fair",
        "stock": 1,
        "sold_b2b_or_direct": False
    }
    phones_db['phone-004'] = {
        "model": "OnePlus 9",
        "base_cost": 350.00,
        "condition": "Like New",
        "stock": 0, 
        "sold_b2b_or_direct": False
    }
    phones_db['phone-005'] = {
        "model": "Xiaomi Mi 11",
        "base_cost": 100.00,
        "condition": "Fair",
        "stock": 2,
        "sold_b2b_or_direct": False
    }
    phones_db['phone-006'] = {
        "model": "iPhone SE (2nd Gen)",
        "base_cost": 250.00,
        "condition": "Good",
        "stock": 1,
        "sold_b2b_or_direct": True 
    }
    phones_db['phone-007'] = {
        "model": "Oppo Find X3 Pro",
        "base_cost": 50.00, 
        "condition": "Good",
        "stock": 1,
        "sold_b2b_or_direct": False
    }

    app.run(debug=True, host='127.0.0.1', port=5000)