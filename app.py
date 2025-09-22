from flask import Flask, request, jsonify, render_template, url_for
import qrcode
import io
import base64
from datetime import datetime
import json

app = Flask(__name__)

# In-memory storage (use database in production)
fittings_data = {}

# Railway track fittings list
RAILWAY_FITTINGS = [
    "Rails",
    "Rail Clips", 
    "Rail Fasteners",
    "Fish Plates",
    "Bolts and Nuts",
    "Rail Pads",
    "Sleepers/Ties",
    "Ballast",
    "Spikes",
    "Tie Plates",
    "Rail Anchors",
    "Expansion Joints",
    "Switches/Points",
    "Crossings",
    "Signal Equipment",
    "Insulators"
]

@app.route('/')
def home():
    return render_template('index.html', fittings=RAILWAY_FITTINGS)

@app.route('/api/create-qr', methods=['POST'])
def create_qr():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['manufacturer_name', 'lot_number', 'item_type', 'manufacture_date', 'shipping_date', 'warranty_period']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        lot_number = data['lot_number']
        
        # Check if lot number already exists
        if lot_number in fittings_data:
            return jsonify({'error': 'Lot number already exists'}), 400
        
        # Store data
        fittings_data[lot_number] = {
            'manufacturer_name': data['manufacturer_name'],
            'lot_number': lot_number,
            'item_type': data['item_type'],
            'manufacture_date': data['manufacture_date'],
            'shipping_date': data['shipping_date'],
            'warranty_period': data['warranty_period'],
            'created_at': datetime.now().isoformat()
        }
        
        # Generate QR code URL
        details_url = f"{request.host_url}details/{lot_number}"
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(details_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        img_buffer = io.BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        qr_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'qr_code': f"data:image/png;base64,{qr_base64}",
            'details_url': details_url,
            'lot_number': lot_number
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/details/<lot_number>')
def view_details(lot_number):
    if lot_number not in fittings_data:
        return render_template('error.html', message="Item not found"), 404
    
    item_data = fittings_data[lot_number]
    return render_template('details.html', data=item_data)

@app.route('/api/all-items')
def get_all_items():
    return jsonify(fittings_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)