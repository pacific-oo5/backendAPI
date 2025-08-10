from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from .models import CustomUser

class CustomRegisterForm(UserCreationForm):
    user_r = forms.BooleanField(required=False, label='Я работодатель')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'user_r')
        widjets = {
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com'}),
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
            'placeholder': 'Введите пароль'
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
            'placeholder': 'Старый пароль',
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Новый пароль',
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите новый пароль',
        })