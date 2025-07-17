from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
import logging
from .forms import UserRegisterForm, UserProfileForm
from .models import UserProfile

# 設置日誌
logger = logging.getLogger(__name__)

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if form.is_valid():
                user = form.save()
                # 創建 UserProfile
                UserProfile.objects.get_or_create(user=user)
                # 自動登入
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    logger.info(f"User {username} registered and logged in successfully")
                    return JsonResponse({'success': True, 'message': f'帳戶 {username} 已創建並登入'})
                else:
                    logger.error(f"Authentication failed for user {username} after registration")
                    return JsonResponse({'success': False, 'errors': {'__all__': ['無法自動登入，請稍後再試']}}, status=400)
            else:
                errors = {field: errors for field, errors in form.errors.items()}
                logger.warning(f"Registration failed: errors={errors}")
                return JsonResponse({'success': False, 'errors': errors}, status=400)
        else:
            if form.is_valid():
                user = form.save()
                # 創建 UserProfile
                UserProfile.objects.get_or_create(user=user)
                # 自動登入
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'帳戶 {username} 已創建並登入')
                    logger.info(f"User {username} registered and logged in successfully (non-AJAX)")
                    return redirect('store:home')
                else:
                    messages.error(request, '無法自動登入，請手動登入')
                    logger.error(f"Authentication failed for user {username} after registration (non-AJAX)")
                    return redirect('accounts:login')
            else:
                logger.warning(f"Registration failed (non-AJAX): errors={form.errors}")
                return render(request, 'registration/register.html', {'form': form})
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register_modal.html' if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    logger.info(f"User {username} logged in successfully")
                    return JsonResponse({'success': True, 'message': f'歡迎回來，{username}！'})
                else:
                    logger.warning(f"Login failed for username {username}: invalid credentials")
                    return JsonResponse({'success': False, 'errors': {'__all__': ['用戶名或密碼錯誤']}}, status=400)
            else:
                errors = {field: errors for field, errors in form.errors.items()}
                logger.warning(f"Login failed: errors={errors}")
                return JsonResponse({'success': False, 'errors': errors}, status=400)
        else:
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'歡迎回來，{username}！')
                    logger.info(f"User {username} logged in successfully (non-AJAX)")
                    return redirect('store:home')
                else:
                    messages.error(request, '用戶名或密碼錯誤')
                    logger.warning(f"Login failed for username {username}: invalid credentials (non-AJAX)")
            return render(request, 'registration/login.html', {'form': form})
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login_modal.html' if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else 'registration/login.html', {'form': form})

@login_required
def profile_view(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
        logger.info(f"Created UserProfile for user {request.user.username}")
    
    # 獲取近期訂單
    from store.models import Order
    try:
        recent_orders = Order.objects.filter(user=request.user).order_by('-created_at').select_related('user').prefetch_related('items__product')[:5]
        logger.info(f"Retrieved {recent_orders.count()} recent orders for user {request.user.username}")
    except Exception as e:
        logger.error(f"Error retrieving orders for user {request.user.username}: {str(e)}")
        recent_orders = []
    
    context = {
        'user': request.user,
        'profile': profile,
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def update_profile(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
        logger.info(f"Created UserProfile for user {request.user.username}")

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '個人資料已更新。')
            logger.info(f"User {request.user.username} updated profile")
            return redirect('accounts:profile')
        else:
            messages.error(request, '更新失敗，請檢查輸入資料。')
            logger.warning(f"Profile update failed for user {request.user.username}: errors={form.errors}")
    else:
        form = UserProfileForm(instance=user_profile, user=request.user)
    return render(request, 'accounts/update_profile.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, '您已成功登出。')
    logger.info(f"User {request.user.username if request.user.is_authenticated else 'anonymous'} logged out")
    return redirect('store:home')
