import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

def send_email(subject, template_name, recipients, context, attachments=None):
    try:
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        
        from_email = settings.DEFAULT_FROM_EMAIL
        msg = EmailMultiAlternatives(subject, text_content, from_email, recipients)
        msg.attach_alternative(html_content, "text/html")
        
        if attachments:
            for filename, content, mimetype in attachments:
                msg.attach(filename, content, mimetype)
        
        msg.send()
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False
