from users.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
import random,re,string, uuid
from django.conf import settings
from django.utils.timezone import now
from .enums import *
from django.forms.models import model_to_dict
from collections import defaultdict
from pprint import pprint
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .sms import send_sms

current_year = now().year

def generate_random_string(length, char_type='string', case='lower'):
    if not isinstance(length, int) or length <= 0:
        raise ValueError("Length must be a positive integer.")
    if char_type not in ['string', 'int']:
        raise ValueError("char_type must be either 'string' or 'int'.")
    if char_type == 'int':
        characters = string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    if length > 8:
        generated_string = str(uuid.uuid4()).replace('-', '')[:length]
    else:
        characters = string.ascii_letters + string.digits
        generated_string = ''.join(random.choice(characters) for _ in range(length))
    if case == 'lower':
        return generated_string.lower()
    elif case == 'upper':
        return generated_string.upper()
    elif case == 'capitalize':
        return generated_string.capitalize()
    else:
        return generated_string.lower()

def param_name(Register,device):
    s = f"{device}_{Register}"
    s = s.lower()
    s = re.sub(r'\s+', '_', s)
    return s

def send_notif( subject, message, recipient_users, type =['email'], notif_level='info'):
    if not recipient_users: return
    if not isinstance(recipient_users, list): recipient_users = [recipient_users]

    for user in recipient_users:
        try:
            if 'email' in type:
                html_content = render_to_string('email.html', {
                    'title': subject,
                    'message': message,
                    'notif_level': notif_level,
                    'timestamp': timezone.now(),
                    'smarty_name': settings.DEFAULT_FROM_EMAIL
                })
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True, html_message=html_content)
            if 'sms' in type:
                send_sms(recipient=user.phone_number, message=message)
        except Exception as e:
            print(f"Failed to send notif: {e}")
