from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import User, VerificationCode
from smarty.helpers.security import generate_otp
from smarty.helpers.emails import send_email
from smarty.helpers.sms import send_sms
from django.contrib.auth.decorators import login_required
from django.urls import reverse

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'users/register.html', {
                'username': username,
                'email': email,
                'phone': phone
            })
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'users/register.html', {
                'email': email,
                'phone': phone
            })
            
        user = User.objects.create_user(username=username, email=email, password=password)
        user.phone_number = phone
        user.is_active = False # Require verification
        user.save()
        
        # Send Email Verification
        otp = generate_otp()
        VerificationCode.objects.create(user=user, code=otp, code_type='EMAIL')
        send_email(
            "Verify your Smarty Account",
            "emails/verification.html",
            [email],
            {'otp': otp, 'user': user}
        )
        
        # Send SMS if phone provided
        if phone:
            otp_sms = generate_otp()
            VerificationCode.objects.create(user=user, code=otp_sms, code_type='PHONE')
            send_sms(phone, f"Your Smarty verification code is: {otp_sms}")
            
        # Notify Admin
        send_email(
            "New User Registration",
            "emails/admin_alert.html",
            [settings.ADMIN_NOTIFICATION_EMAIL],
            {
                'event': 'Registration',
                'user': user,
                'user_name': username,
                'details': f"New account created for {username} ({email})"
            }
        )
            
        request.session['verify_user_id'] = user.id
        return redirect('verify_account')
        
    return render(request, 'users/register.html')

def verify_account(request):
    user_id = request.session.get('verify_user_id')
    if not user_id:
        return redirect('register')
        
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        email_code = request.POST.get('email_code')
        # phone_code = request.POST.get('phone_code') # Optional dual check
        
        v_email = VerificationCode.objects.filter(user=user, code=email_code, code_type='EMAIL', is_used=False).first()
        if v_email and v_email.is_valid():
            v_email.is_used = True
            v_email.save()
            user.is_email_verified = True
            user.is_active = True
            user.save()
            messages.success(request, "Account verified! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid or expired code.")
            
    return render(request, 'users/verify.html', {'user': user})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            if not user.is_active:
                request.session['verify_user_id'] = user.id
                messages.warning(request, "Please verify your account first.")
                return redirect('verify_account')
            
            if user.two_fa_method != 'NONE':
                # Start 2FA Flow
                otp = generate_otp()
                VerificationCode.objects.create(user=user, code=otp, code_type='2FA')
                
                if user.two_fa_method == 'EMAIL':
                    send_email("Your 2FA Code", "emails/two_fa.html", [user.email], {'otp': otp})
                elif user.two_fa_method == 'SMS' and user.phone_number:
                    send_sms(user.phone_number, f"Your Smarty login code: {otp}")
                    
                request.session['2fa_user_id'] = user.id
                return redirect('two_fa_verify')
            
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
            
    return render(request, 'users/login.html')

def two_fa_verify(request):
    user_id = request.session.get('2fa_user_id')
    if not user_id:
        return redirect('login')
        
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        code = request.POST.get('code')
        v = VerificationCode.objects.filter(user=user, code=code, code_type='2FA', is_used=False).first()
        if v and v.is_valid():
            v.is_used = True
            v.save()
            login(request, user)
            del request.session['2fa_user_id']
            return redirect('home')
        else:
            messages.error(request, "Invalid 2FA code")
            
    return render(request, 'users/two_fa.html')


@login_required
def security_settings(request):
    if request.method == 'POST':
        user = request.user
        user.two_fa_method = request.POST.get('two_fa_method', 'NONE')
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.save()
        messages.success(request, "Security settings updated.")
        return redirect('security_settings')
        
    return render(request, 'users/security.html')

def logout_view(request):
    logout(request)
    return redirect('home')
