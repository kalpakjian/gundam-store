from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=False, label='電子郵件')  # 使 email 可選
    password1 = forms.CharField(widget=forms.PasswordInput, label='密碼')
    password2 = forms.CharField(widget=forms.PasswordInput, label='確認密碼')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('此電子郵件已被使用。')
        return email

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required=False, label='電子郵件')
    
    class Meta:
        model = UserProfile
        fields = ['avatar', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2 * 1024 * 1024:  # 限制 2MB
                raise forms.ValidationError('頭像檔案大小不得超過 2MB。')
            if not avatar.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                raise forms.ValidationError('僅支援 PNG 或 JPEG 格式的頭像。')
        return avatar

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # 檢查電子郵件格式
            if '@' not in email or '.' not in email.split('@')[-1]:
                raise forms.ValidationError('請輸入有效的電子郵件地址。')
            # 檢查是否已被其他用戶使用
            if self.user and User.objects.filter(email=email).exclude(id=self.user.id).exists():
                raise forms.ValidationError('此電子郵件已被其他用戶使用。')
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            # 更新用戶的電子郵件
            if self.user:
                self.user.email = self.cleaned_data.get('email', '')
                self.user.save()
        return profile
