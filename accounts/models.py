import logging
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 設置日誌
logger = logging.getLogger(__name__)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    address = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'user_profile'  # 自訂資料表名稱
        ordering = ['user__username']  # 預設按用戶名排序
        verbose_name = 'User Profile'  # 管理介面顯示名稱
        verbose_name_plural = 'User Profiles'  # 複數形式
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_user_profile')
        ]  # 確保 user 欄位唯一

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    try:
        if created:
            UserProfile.objects.create(user=instance)
            logger.info(f"Created UserProfile for user: {instance.username}")
        else:
            if hasattr(instance, 'userprofile'):
                instance.userprofile.save()
                logger.debug(f"Updated UserProfile for user: {instance.username}")
            else:
                UserProfile.objects.create(user=instance)
                logger.warning(f"UserProfile was missing for user: {instance.username}, created new one")
    except Exception as e:
        logger.error(f"Error in creating/updating UserProfile for user {instance.username}: {str(e)}")