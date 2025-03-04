from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def send_travel_guide_email(email: str, guide_data: dict) -> bool:
    """
    Send travel guide via email
    
    Args:
        email: Recipient email address
        guide_data: Dictionary containing travel guide information
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        msg = Message(
            subject=f"Your Travel Guide for {guide_data['destination']}",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email]
        )
        
        # Create email body
        msg.body = f"""
Hello!

Here's your personalized travel guide for {guide_data['destination']}!

Trip Details:
- Destination: {guide_data['destination']}
- Dates: {guide_data['start_date']} to {guide_data['end_date']}
- Duration: {guide_data['number_of_days']} days
- Travelers: {guide_data['travelers']}
- Budget: {guide_data['budget']}
- Interests: {guide_data['interests']}

Your Itinerary:
{guide_data['itinerary']}

Have a great trip!

Best regards,
Your Travel Guide Team
        """
        
        mail.send(msg)
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False
