from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required   
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.views import View
from django.contrib.auth.views import PasswordChangeView
from django.core.paginator import Paginator

from .forms import *
from api.models import Vacancy, Anketa, VacancyResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from dj_rest_auth.registration.views import SocialLoginView


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000/"
    client_class = OAuth2Client

# @ensure_csrf_cookie
# def get_csrf_token(request):
#     return JsonResponse({'detail': 'CSRF cookie set'})    


class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "user_r": user.user_r
        })

class AuthView(View):
    template_name = 'auth/login_register.html'
    
    def get(self, request):
        # Передаем обе формы в контекст
        login_form = CustomLoginForm()
        register_form = CustomRegisterForm()
        return render(request, self.template_name, {
            'login_form': login_form,
            'register_form': register_form
        })

class CustomRegisterView(View):
    template_name = 'auth/login_register.html'    
    
    def post(self, request):
        register_form = CustomRegisterForm(request.POST, request.FILES)
        if register_form.is_valid():
            user = register_form.save(commit=False)
            user.user_r = register_form.cleaned_data.get('user_r', False)
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
        
        # Если форма невалидна, возвращаем страницу с обеими формами
        login_form = CustomLoginForm()
        return render(request, self.template_name, {
            'login_form': login_form,
            'register_form': register_form
        })

class CustomLoginView(LoginView):
    template_name = 'auth/login_register.html'
    authentication_form = CustomLoginForm
    
    def form_valid(self, form):
        """Если форма валидна, выполняем вход и перенаправляем"""
        login(self.request, form.get_user())
        return redirect('home')
    
    def form_invalid(self, form):
        """Если форма невалидна, показываем обе формы"""
        register_form = CustomRegisterForm()
        return render(self.request, self.template_name, {
            'login_form': form,
            'register_form': register_form
        })


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')

@login_required
def select_role_view(request):
    if request.method == 'POST':
        is_employer = request.POST.get('user_r') == 'on'
        user = request.user
        user.user_r = is_employer
        user.save()
        return redirect('home')
    return render(request, 'auth/select_role.html')

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        user = request.user
        vacancies = Vacancy.objects.filter(user=user) if user.user_r else None
        ankets = Anketa.objects.filter(user=user, is_active=True) if not user.user_r else None
        responses = None
        if not user.user_r:
            responses = VacancyResponse.objects.filter(worker=user).select_related('vacancy', 'anketa').order_by('-responded_at')
        if user.user_r:
            # Все отклики на вакансии пользователя
            responses_qs = VacancyResponse.objects.filter(vacancy__user=user).select_related('vacancy', 'anketa', 'worker').order_by('-responded_at')
            paginator = Paginator(responses_qs, 10)  # 10 на страницу
            page_number = request.GET.get('page')
            responses = paginator.get_page(page_number)
            
        password_form = PasswordChangeForm(user)
        return render(request, 'userauth/profile.html', {
            'user': user,
            'vacancies': vacancies,
            'ankets': ankets,
            'responses': responses,
            'password_form': password_form,
            'in_profile': True,
        })

    def post(self, request):
        user = request.user
        if 'name' in request.POST or 'photo' in request.FILES:
            name = request.POST.get('name')
            photo = request.FILES.get('photo')
            if name:
                user.name = name
            if photo:
                user.photo = photo
            user.save()
        elif 'old_password' in request.POST:
            password_form = CustomPasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
        return redirect('profile')


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'userauth/password_change.html'
    success_url = reverse_lazy('profile')