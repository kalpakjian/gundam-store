"""
store/views.py
Django views for gundam_store project.
"""

import os
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Category, ProductImage, Cart, CartItem, Order, OrderItem
from accounts.models import UserProfile
from django.db import transaction

# 設置日誌
logger = logging.getLogger(__name__)

# 購物車輔助函數
def get_or_create_cart(request):
    """獲取或創建購物車，統一處理登入/匿名用戶邏輯"""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            defaults={'session_key': session_key}
        )
    else:
        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            defaults={'user': None}
        )
    logger.debug(f"Cart: {cart}, Created: {created}")
    return cart

# 首頁
def home(request):
    # 獲取特色產品（隨機三個有折扣的產品）
    featured_products = Product.objects.filter(discount_price__isnull=False).order_by('-created_at')[:3]
    
    # 獲取最新的五個產品（不排除特價產品）
    latest_products = Product.objects.order_by('-created_at')[:5]
    
    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
    }
    return render(request, 'store/home.html', context)

# 產品列表
def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'store/product_list.html', context)

# 產品詳情
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    images = product.images.all().order_by('order')
    logger.debug(f'Product {product.name}: cover_image={product.cover_image}, cloudinary_url={product.cloudinary_url}')
    logger.debug(f'Images: {[(img.image, img.cloudinary_url, img.description) for img in images]}')
    context = {
        'product': product,
        'images': images,
    }
    return render(request, 'store/product_detail.html', context)

# 分類列表
def category_list(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'store/category_list.html', context)

# 分類詳情
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = category.products.all()
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'store/category_detail.html', context)

# 產品搜尋
def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    ) if query else Product.objects.all()
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'store/search_results.html', context)

# 圖片分享
def share_images(request):
    products = Product.objects.filter(cloudinary_url__isnull=False)
    product_images = ProductImage.objects.filter(cloudinary_url__isnull=False)
    context = {
        'products': products,
        'product_images': product_images,
    }
    return render(request, 'store/share_images.html', context)

# 上傳圖片
def upload_image(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        image_file = request.FILES.get('image')
        description = request.POST.get('description', '')
        if not product_id:
            messages.error(request, '請選擇產品！')
        elif not image_file:
            messages.error(request, '請選擇圖片檔案！')
        elif not image_file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            messages.error(request, '僅支援 JPG 或 PNG 格式！')
        elif image_file.size > 10 * 1024 * 1024:  # 10MB
            messages.error(request, '檔案大小不得超過 10MB！')
        else:
            try:
                product = get_object_or_404(Product, id=product_id)
                product_image = ProductImage.objects.create(
                    product=product,
                    image=image_file,
                    description=description
                )
                logger.info(f'Saved local image for product {product.name}: {product_image.image.url}')
                messages.success(request, '圖片上傳成功！')
                return redirect('store:share_images')
            except Exception as e:
                logger.error(f'Image upload failed: {str(e)}')
                messages.error(request, f'上傳失敗：{str(e)}')
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'store/upload_image.html', context)

# 購物車
def cart(request):
    cart = get_or_create_cart(request)

    context = {
        'cart': cart,
    }
    return render(request, 'store/cart.html', context)

# 添加到購物車
def add_to_cart(request, product_id):
    if request.method != 'POST':
        messages.error(request, '無效的請求方式。')
        return redirect('store:product_detail', pk=product_id)

    product = get_object_or_404(Product, pk=product_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        messages.error(request, '請輸入有效的數量！')
        return redirect('store:product_detail', pk=product_id)
    if quantity < 1:
        messages.error(request, '數量必須大於 0！')
        return redirect('store:product_detail', pk=product_id)
    if product.stock < quantity:
        messages.error(request, f'庫存不足，僅剩 {product.stock} 件！')
        return redirect('store:product_detail', pk=product_id)

    cart = get_or_create_cart(request)

    # 查找或創建購物車項目
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    if not item_created:
        cart_item.quantity += quantity
        cart_item.save()
    logger.debug(f"CartItem: {cart_item}, Created: {item_created}")

    messages.success(request, f'已將 {product.name} 添加到購物車！')
    return redirect('store:cart')

# 更新購物車
def update_cart(request):
    if request.method != 'POST':
        messages.error(request, '無效的請求方式。')
        return redirect('store:cart')

    cart = get_or_create_cart(request)

    for item in cart.items.all():
        quantity_key = f'quantity_{item.id}'
        if quantity_key in request.POST:
            try:
                new_quantity = int(request.POST[quantity_key])
                if new_quantity < 1:
                    item.delete()
                    messages.success(request, f'已移除 {item.product.name}！')
                elif item.product.stock < new_quantity:
                    messages.error(request, f'{item.product.name} 庫存不足，僅剩 {item.product.stock} 件！')
                else:
                    item.quantity = new_quantity
                    item.save()
                    messages.success(request, f'已更新 {item.product.name} 數量！')
            except ValueError:
                messages.error(request, f'請為 {item.product.name} 輸入有效的數量。')
    
    return redirect('store:cart')

def remove_from_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, pk=item_id)
        product_name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f'已移除 {product_name}！')
    return redirect('store:cart')

# 結帳
def checkout(request):
    cart = get_or_create_cart(request)

    # 獲取預設地址（僅限登錄用戶）
    default_address = ''
    if request.user.is_authenticated:
        try:
            default_address = request.user.userprofile.address
        except UserProfile.DoesNotExist:
            from accounts.models import UserProfile
            UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        # 檢查購物車是否為空
        if not cart.items.exists():
            messages.error(request, '購物車為空！')
            return render(request, 'store/checkout.html', {'cart': cart, 'default_address': default_address})

        # 檢查庫存
        for item in cart.items.all():
            if item.product.stock < item.quantity:
                messages.error(request, f'{item.product.name} 庫存不足，僅剩 {item.product.stock} 件！')
                return render(request, 'store/checkout.html', {'cart': cart, 'default_address': default_address})

        # 獲取送貨地址
        shipping_address = request.POST.get('shipping_address', '').strip()
        if request.user.is_authenticated and not shipping_address:
            # 登錄用戶：使用 UserProfile.address 作為預設值
            try:
                shipping_address = request.user.userprofile.address
            except UserProfile.DoesNotExist:
                pass

        if not shipping_address:
            messages.error(request, '請輸入送貨地址！')
            return render(request, 'store/checkout.html', {'cart': cart, 'default_address': default_address})

        # 可選：如果登錄用戶提交新地址，更新 UserProfile
        if request.user.is_authenticated and shipping_address != request.user.userprofile.address:
            try:
                request.user.userprofile.address = shipping_address
                request.user.userprofile.save()
                logger.info(f"Updated UserProfile.address for {request.user.username} to {shipping_address}")
            except UserProfile.DoesNotExist:
                from accounts.models import UserProfile
                UserProfile.objects.create(user=request.user, address=shipping_address)

        # 計算總價
        total_price = sum(item.get_subtotal() for item in cart.items.all())

        # 創建訂單（使用事務確保數據一致性）
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key,
                shipping_address=shipping_address,
                total_price=total_price,
                status='pending'
            )

            # 創建訂單項目並更新庫存
            for item in cart.items.all():
                price = item.product.discount_price if item.product.discount_price else item.product.price
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=price
                )
                item.product.stock -= item.quantity
                item.product.save()

            # 清空購物車
            cart.items.all().delete()

        messages.success(request, '訂單已提交！')
        return redirect('store:orders')

    context = {
        'cart': cart,
        'default_address': default_address,
    }
    return render(request, 'store/checkout.html', context)

# 用戶個人資料
@login_required
def profile_view(request):
    # 確保 UserProfile 存在
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        try:
            first_name = request.POST.get('first_name', '').strip()
            email = request.POST.get('email', '').strip()
            address = request.POST.get('address', '').strip()
            avatar = request.FILES.get('avatar')
            
            # 驗證輸入
            if not email:
                messages.error(request, '電子郵件不能為空！')
            elif len(first_name) > 50:
                messages.error(request, '姓名長度不能超過 50 個字元！')
            elif len(address) > 200:
                messages.error(request, '地址長度不能超過 200 個字元！')
            elif avatar and not avatar.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                messages.error(request, '頭像僅支援 JPG 或 PNG 格式！')
            elif avatar and avatar.size > 2 * 1024 * 1024:  # 2MB
                messages.error(request, '頭像檔案大小不得超過 2MB！')
            else:
                # 更新 User 資料
                request.user.first_name = first_name
                request.user.email = email
                request.user.save()
                
                # 更新 UserProfile 資料
                profile.address = address
                if avatar:
                    profile.avatar = avatar
                profile.save()
                
                logger.info(f"User {request.user.username} updated profile: first_name={first_name}, email={email}, address={address}, avatar={avatar}")
                messages.success(request, '個人資料已更新！')
        except Exception as e:
            logger.error(f"Error updating profile for user {request.user.username}: {str(e)}")
            messages.error(request, '更新個人資料失敗，請稍後再試！')
        return redirect('store:profile')
    
    try:
        recent_orders = Order.objects.filter(user=request.user).order_by('-created_at').select_related('user').prefetch_related('items__product')[:5]
        logger.info(f"Retrieved {recent_orders.count()} recent orders for user {request.user.username}")
    except Exception as e:
        logger.error(f"Error retrieving orders for user {request.user.username}: {str(e)}")
        messages.error(request, '無法載入近期訂單，請稍後再試！')
        recent_orders = []

    context = {
        'user': request.user,
        'profile': profile,
        'recent_orders': recent_orders,
    }
    return render(request, 'store/profile.html', context)

# 訂單歷史
@login_required
def order_history(request):
    try:
        orders = Order.objects.filter(user=request.user).order_by('-created_at').select_related('user').prefetch_related('items__product')
        logger.info(f"Retrieved {orders.count()} orders for user {request.user.username}")
        for order in orders:
            logger.debug(f"Order {order.id}: {order.total_price}, {order.status}, {order.created_at}")
    except Exception as e:
        logger.error(f"Error retrieving orders for user {request.user.username}: {str(e)}")
        messages.error(request, "無法載入訂單歷史，請稍後再試。")
        orders = []
    context = {
        'orders': orders,
    }
    return render(request, 'store/orders.html', context)