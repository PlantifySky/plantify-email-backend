# Plantify Backend API

This is the backend API for the Plantify website, handling email sending functionality for the contact form.

## Setup Instructions

1. Install dependencies:
   ```
   pip install flask flask-cors python-dotenv
   ```

2. Create an environment file:
   - Copy `.env.example` to `.env`
   - Fill in your actual email credentials

3. Run the server:
   ```
   python app.py
   ```

4. The server will run at http://localhost:5000

## Security Notes

- Never commit your actual `.env` file with real credentials
- For Gmail accounts, use an App Password instead of your regular password
- Make sure to set up proper CORS restrictions in production

## Available Endpoints

- `GET /api/test` - Test if the server and environment variables are working
- `POST /api/contact` - Submit contact form data for email sending
