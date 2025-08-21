from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

class CustomRegisterForm(UserCreationForm):
    user_r = forms.BooleanField(required=False, label=_('Я работодатель'))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'user_r')
        widjets = {
            'email': forms.EmailInput(attrs={'placeholder': 'title@example.com'}),
        }

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email', 'id': 'id_username'}))
        
    class Meta:
        model = CustomUser
        fields = ['email', 'password']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'id': 'password-input',
            'placeholder': _('Введите пароль')
        })
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email'
        })
        

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Старый пароль'),
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Новый пароль'),
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Повторите новый пароль'),
        })