from flask import Flask, render_template, request, send_file, session, redirect, url_for
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'qr_code_generator_secret_key'  # Required for session

# Define the custom filter for base64 encoding
def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')

# Register the custom filter
app.jinja_env.filters['b64encode'] = b64encode_filter

@app.route('/', methods=['GET', 'POST'])
def index():
    # Check if reset was requested
    reset = request.args.get('reset')
    if reset == 'true':
        if 'qr_image_url' in session:  # Fixed key name
            session.pop('qr_image_url', None)
        return render_template('index.html')
    
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
            
            # Store the image data in the session (optional)
            # session['qr_image_url'] = url
            
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

if __name__ == '__main__':
    app.run(debug=True)
