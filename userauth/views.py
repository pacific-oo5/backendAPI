from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout, update_session_auth_hash, login
from django.contrib.auth.views import LoginView
from django.views import View
from django.core.paginator import Paginator

from .forms import *
from .models import TelegramProfile, CustomUser
from api.models import Vacancy, Anketa, VacancyResponse

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from dj_rest_auth.registration.views import SocialLoginView


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000/"
    client_class = OAuth2Client

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
        role = request.POST.get('user_r')  # 'employer' или 'seeker'
        user = request.user
        user.user_r = (role == 'employer')  # True если работодатель, False если соискатель
        user.save()
        return redirect('home')

    # для отображения активного состояния в шаблоне
    current_role = 'employer' if request.user.user_r else 'seeker'
    return render(request, 'auth/select_role.html', {'current_role': current_role})

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        user = request.user
        vacancies = Vacancy.objects.filter(user=user) if user.user_r else None
        ankets = Anketa.objects.filter(user=user, is_active=True) if not user.user_r else None
        responses = None
        profile, created = TelegramProfile.objects.get_or_create(user=request.user)
        if not user.user_r:
            responses = VacancyResponse.objects.filter(worker=user).select_related('vacancy', 'anketa').order_by('-responded_at')
        if user.user_r:
            # Все отклики на вакансии пользователя
            responses_qs = VacancyResponse.objects.filter(vacancy__user=user).select_related('vacancy', 'anketa', 'worker').order_by('-responded_at')
            paginator = Paginator(responses_qs, 10)  # 10 на страницу
            page_number = request.GET.get('page')
            responses = paginator.get_page(page_number)

        context = {
            'user': user,
            'vacancies': vacancies,
            'ankets': ankets,
            'responses': responses,
            'in_profile': True,

            "tg_connected": profile.is_connected,
            "tg_token": str(profile.token),
            "tg_name": f"{profile.first_name or ''} {profile.last_name or ''}".strip() or profile.username or "Без имени",
            "tg_username": f"@{profile.username}" if profile.username else "",
        }

        password_form = PasswordChangeForm(user)
        return render(request, 'userauth/profile.html', context)

    def post(self, request):
        user = request.user
        profile, _ = TelegramProfile.objects.get_or_create(user=user)

        if 'reset_telegram' in request.POST:
            profile.reset_connection()

        if 'username' in request.POST:
            user.username = request.POST.get('username')
            user.save()

        if 'title' in request.POST or 'photo' in request.FILES:
            name = request.POST.get('title')
            photo = request.FILES.get('photo')
            if name:
                user.title = name
            if photo:
                user.photo = photo
            user.save()
        elif 'old_password' in request.POST:
            password_form = CustomPasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
        return redirect('userauth:profile')


class PublicProfileView(View):
    template_name = 'userauth/public_profile.html'

    def get(self, request, pk):
        if request.user.is_authenticated and request.user.pk == pk:
            return redirect('userauth:profile')
        user = get_object_or_404(CustomUser, pk=pk)

        vacancies = Vacancy.objects.filter(user=user, is_active=True) if user.user_r else None
        ankets = Anketa.objects.filter(user=user, is_active=True) if not user.user_r else None

        return render(request, self.template_name, {
            'profile_user': user,  # чтобы не путаться с request.user
            'vacancies': vacancies,
            'ankets': ankets,
        })