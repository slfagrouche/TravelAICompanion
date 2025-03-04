# test_travel_guide.py
from flask import Flask
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a simple Flask application for testing
app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

# Initialize Flask-Mail
mail = Mail(app)

def test_email():
    """
    Test function to verify email configuration.
    """
    recipient = input("Enter recipient email address: ")
    
    # Create an application context
    with app.app_context():
        try:
            msg = Message(
                subject="Flask Mail Test",
                recipients=[recipient],
                body="This is a test email from your Flask application. If you're seeing this, your email configuration is working correctly!"
            )
            
            mail.send(msg)
            print(f"\nSuccess! Test email sent to {recipient}")
            print("Email configuration appears to be working correctly!")
            
        except Exception as e:
            print(f"\nError: Failed to send email!")
            print(f"Error details: {str(e)}")
            print("\nPlease check your .env configuration:")
            print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
            print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
            print(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
            print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
            print(f"MAIL_PASSWORD: {'[SET]' if app.config['MAIL_PASSWORD'] else '[NOT SET]'}")
            print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")

if __name__ == "__main__":
    print("Flask Email Configuration Test")
    print("-----------------------------")
    print("This script will test your Flask-Mail configuration by sending a test email.")
    print("Make sure your .env file is properly configured before running this test.")
    
    test_email()