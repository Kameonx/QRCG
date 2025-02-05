from flask import Flask, render_template, request, send_file
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)

# Define the custom filter for base64 encoding
def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')

# Register the custom filter
app.jinja_env.filters['b64encode'] = b64encode_filter

@app.route('/', methods=['GET', 'POST'])
def index():
    qr_image = None
    qr_url = None
    error = None
    
    if request.method == 'POST':
        url = request.form['url']
        if not url:
            error = "Please enter a website URL"
        else:
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
                
                qr_image = img_byte_arr.getvalue()
                qr_url = url
            except Exception as e:
                error = f"Failed to generate QR code: {str(e)}"
    
    return render_template('index.html', qr_image=qr_image, qr_url=qr_url, error=error)

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
