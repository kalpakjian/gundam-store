from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('store/', include('store.urls')),  # store 應用程式路由
    path('', lambda request: redirect('store:home')),  # 根路徑重定向到 store:home
    path('accounts/', include('accounts.urls')),  # accounts 應用程式路由
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 開發環境中提供 media 檔案
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)