from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables with explicit debug output
print("Loading environment variables...")
load_dotenv()

# Set environment variables directly as fallback if they're not loaded from .env
if not os.environ.get('EMAIL_HOST'):
    print("Environment variables not found in .env file, setting them directly...")
    os.environ['EMAIL_HOST'] = 'smtp.gmail.com'
    os.environ['EMAIL_PORT'] = '587'
    os.environ['EMAIL_USER'] = '***REDACTED***'  # Email is now hidden
    os.environ['EMAIL_PASSWORD'] = '***REDACTED***'  # Password is now hidden
    os.environ['EMAIL_FROM'] = '***REDACTED***'  # Email is now hidden
    os.environ['EMAIL_SECURE'] = 'false'

# Print environment variables status (without revealing sensitive information)
print("Environment variables status:")
print(f"EMAIL_HOST set: {'Yes' if os.environ.get('EMAIL_HOST') else 'No'}")
print(f"EMAIL_PORT set: {'Yes' if os.environ.get('EMAIL_PORT') else 'No'}")
print(f"EMAIL_USER set: {'Yes' if os.environ.get('EMAIL_USER') else 'No'}")
print(f"EMAIL_PASSWORD set: {'Yes' if os.environ.get('EMAIL_PASSWORD') else 'No'}")
print(f"EMAIL_FROM set: {'Yes' if os.environ.get('EMAIL_FROM') else 'No'}")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Simple sanitization function
def sanitize_input(input_str):
    if not input_str:
        return ""
    return input_str.strip().replace("<", "&lt;").replace(">", "&gt;")

@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        print("Received contact form submission")
        # Get JSON data
        data = request.get_json()
        if not data:
            print("Invalid JSON payload received")
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        # Extract and validate fields
        name = data.get('name')
        surname = data.get('surname')
        email = data.get('email')
        message = data.get('message')
        
        print(f"Form data received - Name: {name}, Email: {email}")
        
        # Validate required fields
        if not name or not surname or not email or not message:
            print("Missing required fields in submission")
            return jsonify({"error": "Missing required fields"}), 400
        
        # Email validation
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            print(f"Invalid email format: {email}")
            return jsonify({"error": "Invalid email format"}), 400
            
        # Sanitize inputs
        sanitized_name = sanitize_input(name)
        sanitized_surname = sanitize_input(surname)
        sanitized_email = sanitize_input(email)
        sanitized_message = sanitize_input(message)
        
        # Ensure we have email configuration
        email_host = os.environ.get('EMAIL_HOST')
        email_port = os.environ.get('EMAIL_PORT')
        email_user = os.environ.get('EMAIL_USER')
        email_password = os.environ.get('EMAIL_PASSWORD')
        email_from = os.environ.get('EMAIL_FROM', email_user)
        
        print("Email configuration check:")
        print(f"- EMAIL_HOST: {email_host}")
        print(f"- EMAIL_PORT: {email_port}")
        print(f"- EMAIL_USER: {'***REDACTED***' if email_user else 'Missing'}")
        print(f"- EMAIL_PASSWORD: {'***REDACTED***' if email_password else 'Missing'}")
        
        if not email_host or not email_user or not email_password:
            print("Missing email configuration")
            return jsonify({"error": "Server configuration error"}), 500
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = email_user
        msg['Subject'] = 'New Contact Form Submission from Plantify Website'
        
        # Plain text version
        text = f"""
Name: {sanitized_name} {sanitized_surname}
Email: {sanitized_email}

Message:
{sanitized_message}
"""
        
        # HTML version
        html = f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <h2 style="color: #599c10;">New Contact Form Submission</h2>
  <p><strong>Name:</strong> {sanitized_name} {sanitized_surname}</p>
  <p><strong>Email:</strong> {sanitized_email}</p>
  <div style="margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 4px;">
    <h4 style="margin-top: 0;">Message:</h4>
    <p style="white-space: pre-wrap;">{sanitized_message}</p>
  </div>
  <p style="margin-top: 20px; color: #666; font-size: 12px;">This email was sent from the Plantify website contact form.</p>
</div>
"""
        
        # Attach parts
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        print("Attempting to send email...")
        # Send email
        with smtplib.SMTP(email_host, int(email_port)) as server:
            print("Connected to SMTP server")
            server.starttls()
            print("STARTTLS established")
            server.login(email_user, email_password)
            print("Login successful")
            server.send_message(msg)
            print("Email sent successfully")
        
        return jsonify({"success": True})
        
    except Exception as e:
        error_message = str(e)
        print(f"Error sending email: {error_message}")
        return jsonify({"error": f"Failed to send message: {error_message}"}), 500

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint to verify server is working and environment variables are loaded."""
    env_status = {
        'email_host': bool(os.environ.get('EMAIL_HOST')),
        'email_port': bool(os.environ.get('EMAIL_PORT')),
        'email_user': bool(os.environ.get('EMAIL_USER')),
        'email_password': bool(os.environ.get('EMAIL_PASSWORD')),
        'email_from': bool(os.environ.get('EMAIL_FROM')),
    }
    
    return jsonify({
        'status': 'ok',
        'message': 'API is working',
        'environment_variables': env_status
    })

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
