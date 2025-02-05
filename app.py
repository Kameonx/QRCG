from flask import Flask, render_template, request, send_file
import qrcode
from io import BytesIO
import base64
from user_agents import parse
import os
from flask import send_from_directory

app = Flask(__name__)

# Define the custom filter for base64 encoding
def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')

# Register the custom filter
app.jinja_env.filters['b64encode'] = b64encode_filter

# Directory to save photos on mobile
PHOTOS_DIR = os.path.join(os.path.expanduser('~'), 'Photos')

if not os.path.exists(PHOTOS_DIR):
    os.makedirs(PHOTOS_DIR)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if not url:
            return render_template('index.html', error="Please enter a website URL")

        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=20,
                border=2,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img_byte_arr = BytesIO()
            img.save(img_byte_arr)
            img_byte_arr.seek(0)  # Move the cursor to the beginning of the BytesIO stream
            
            # Get user agent
            user_agent = parse(request.headers.get('User-Agent'))
            if user_agent.is_mobile:
                # Save to Photos directory on mobile
                img_path = os.path.join(PHOTOS_DIR, 'QR_Code.png')
                with open(img_path, 'wb') as f:
                    f.write(img_byte_arr.getvalue())
                return render_template('index.html', qr_url=url, saved=True)
            else:
                # For PC, provide download link
                return render_template('index.html', qr_image=img_byte_arr.getvalue(), qr_url=url)
            
        except Exception as e:
            return render_template('index.html', error=f"Failed to generate QR code: {str(e)}")

    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    if not url:
        return "No URL provided", 400

    try:
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_byte_arr = BytesIO()
        img.save(img_byte_arr)
        img_byte_arr.seek(0)  # Move the cursor to the beginning of the BytesIO stream
        
        return send_file(
            img_byte_arr,
            as_attachment=True,
            download_name="QR_Code.png",
            mimetype='image/png'
        )
        
    except Exception as e:
        return str(e), 500

@app.route('/saved', methods=['GET'])
def saved():
    return send_from_directory(PHOTOS_DIR, 'QR_Code.png')

if __name__ == '__main__':
    app.run(debug=True)
