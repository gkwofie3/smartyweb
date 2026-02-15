from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from licensing.models import License
from smarty.helpers.emails import send_email

def home(request):
    return render(request, 'web/index.html')

def about(request):
    return render(request, 'web/about.html')

def pricing(request):
    return render(request, 'web/pricing.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Notify Admin
        send_email(
            "New Website Enquiry",
            "emails/admin_alert.html",
            [settings.ADMIN_NOTIFICATION_EMAIL],
            {
                'event': 'Website Enquiry',
                'user_name': name,
                'details': f"Enquiry from {name} ({email})\nSubject: {subject}\nMessage: {message}"
            }
        )
        
        messages.success(request, "Thank you! Your message has been sent to our engineers.")
        return redirect('contact')
        
    return render(request, 'web/contact.html')

def faq(request):
    return render(request, 'web/faq.html')

@login_required
def docs(request):
    # Check if user has at least one active license
    has_license = License.objects.filter(user=request.user, is_active=True).exists()
    if not has_license:
        return render(request, 'licensing/error.html', {
            'message': 'Documentation access is reserved for active licensees. Please activate a device or purchase a tier to proceed.',
            'title': 'Restricted Access'
        })
    return render(request, 'web/docs.html')
