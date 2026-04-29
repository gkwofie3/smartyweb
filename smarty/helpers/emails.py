import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

def send_email(subject, template_name, recipients, context, attachments=None):
    """
    Sends a multi-part HTML email using the specified template.
    Returns True if successful, False otherwise.
    """
    try:
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        
        from_email = settings.DEFAULT_FROM_EMAIL
        
        # Use an explicit connection with a timeout to be more robust
        connection = get_connection(timeout=10)
        
        msg = EmailMultiAlternatives(
            subject, text_content, from_email, recipients, 
            connection=connection
        )
        msg.attach_alternative(html_content, "text/html")
        
        if attachments:
            for filename, content, mimetype in attachments:
                msg.attach(filename, content, mimetype)
        
        msg.send()
        return True
    except Exception as e:
        logger.error(f"Error sending email [{subject}]: {e}")
        # Log more details if it's a connection issue
        if "Connection unexpectedly closed" in str(e):
            logger.error("SMTP connection was closed prematurely. Check your EMAIL_HOST_PASSWORD (App Password) or if Gmail is throttling the account.")
        return False
