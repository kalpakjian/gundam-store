# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import logging
from .forms import UserRegisterForm, UserProfileForm
from .models import UserProfile

# 設置日誌
logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        logger.debug(f"Login attempt: username={username}")
        user = authenticate(request, username=username, password=password)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if user is not None:
                if user.is_active:
                    login(request, user)
                    logger.info(f"User {username} logged in successfully")
                    return JsonResponse({'success': True, 'message': '登入成功！'})
                else:
                    logger.warning(f"User {username} is inactive")
                    return JsonResponse({'success': False, 'errors': ['此帳號未激活，請聯繫管理員。']}, status=400)
            else:
                logger.warning(f"Invalid login attempt: username={username}")
                return JsonResponse({'success': False, 'errors': ['無效的用戶名或密碼。']}, status=400)
        else:
            if user is not None:
                if user.is_active:
                    login(request, user)
                    logger.info(f"User {username} logged in successfully (non-AJAX)")
                    return redirect('store:home')
                else:
                    logger.warning(f"User {username} is inactive (non-AJAX)")
                    messages.error(request, '此帳號未激活，請聯繫管理員。')
            else:
                logger.warning(f"Invalid login attempt: username={username} (non-AJAX)")
                messages.error(request, '無效的用戶名或密碼。')
            return render(request, 'accounts/login_modal.html')
    return render(request, 'accounts/login_modal.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get('username')
                message = f'帳戶 {username} 已創建，請登入。'
                logger.info(f"User {username} registered successfully")
                return JsonResponse({'success': True, 'message': message})
            else:
                errors = []
                for field, field_errors in form.errors.items():
                    for error in field_errors:
                        errors.append(f"{field}: {error}")
                logger.warning(f"Registration failed: errors={errors}")
                return JsonResponse({'success': False, 'errors': errors}, status=400)
        else:
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'帳戶 {username} 已創建，請登入。')
                logger.info(f"User {username} registered successfully (non-AJAX)")
                return redirect('accounts:login')
            else:
                logger.warning(f"Registration failed (non-AJAX)")
                return render(request, 'accounts/register_modal.html', {'form': form})
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register_modal.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        username = request.user.username if request.user.is_authenticated else 'Anonymous'
        logout(request)
        logger.info(f"User {username} logged out")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': '已登出！'})
        return redirect('store:home')
    return redirect('store:home')

@login_required
def update_profile(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, '個人資料已更新。')
            logger.info(f"User {request.user.username} updated profile")
            return redirect('store:profile')
        else:
            messages.error(request, '更新失敗，請檢查輸入資料。')
            logger.warning(f"Profile update failed for user {request.user.username}")
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'accounts/update_profile.html', {'form': form})