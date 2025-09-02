import hashlib, hmac
import json
from django.contrib.auth import get_user_model
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.shortcuts import render, get_object_or_404
from django.views import generic, View
from django.template.loader import render_to_string
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from api.choices import WORK_CHOICES, WORK_TIME_CHOICES
from api.models import Vacancy, Anketa, VacancyResponse

from django.http import JsonResponse, HttpResponse

from dotenv import load_dotenv

from miniapp.utils import get_tg_id
from userauth.models import TelegramProfile

load_dotenv()

User = get_user_model()

class MiniAppVacancyPageView(generic.ListView):
    model = Vacancy
    template_name = "miniapp/base.html"
    context_object_name = "vacancies"
    paginate_by = 10

    def get_queryset(self):
        queryset = Vacancy.objects.filter(is_active=True).select_related('user').order_by("-published_at")
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(city__icontains=query) |
                Q(country__icontains=query) |
                Q(requirements__icontains=query)
            )
        return queryset

    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            self.object_list = self.get_queryset()
            page = request.GET.get("page", 1)
            paginator = self.get_paginator(self.object_list, self.paginate_by)
            try:
                vacancies = paginator.page(page)
            except PageNotAnInteger:
                vacancies = paginator.page(1)
            except EmptyPage:
                vacancies = paginator.page(paginator.num_pages)

            html = render_to_string("miniapp/partials/vacancy_list.html", {"vacancies": vacancies})
            return JsonResponse({
                "html": html,
                "has_next": vacancies.has_next()
            })
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tg_id = self.request.GET.get('tg_id')  # tg_id приходит из mini app
        telegram_profile = TelegramProfile.objects.filter(telegram_id=tg_id).first() if tg_id else None
        auth_user = bool(telegram_profile)

        context.update({
            "auth_user": auth_user,
            "telegram_profile": telegram_profile,
        })
        return context

class MiniAppVacancyDetailView(generic.DetailView):
    model = Vacancy
    template_name = 'miniapp/partials/vacancy_detail.html'
    context_object_name = 'vacancy'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tg_id = self.request.GET.get('tg_id')
        telegram_user = None

        if tg_id:
            telegram_user = TelegramProfile.objects.filter(telegram_id=tg_id).first()
            context['telegram_user'] = telegram_user

            if telegram_user:
                user_r = telegram_user.user.user_r  # True = работодатель, False = соискатель
                context['user_r'] = user_r

                if not user_r:  # только для соискателей
                    context['anketa_list'] = Anketa.objects.filter(
                        user=telegram_user.user, is_active=True
                    )

                    response = VacancyResponse.objects.filter(
                        worker=telegram_user.user, vacancy=self.object
                    ).select_related("anketa").first()

                    if response:
                        context['responded'] = True
                        context['selected_anketa_id'] = response.anketa.id if response.anketa else None
                    else:
                        context['responded'] = False

            context['is_favorite'] = (
                self.object.favorite_by.filter(pk=telegram_user.user.pk).exists()
                if telegram_user else False
            )

        return context

class MiniAppFilterView(generic.ListView):
    model = Vacancy
    template_name = "miniapp/filter.html"
    context_object_name = "vacancies"
    paginate_by = 10

    def get_queryset(self):
        queryset = Vacancy.objects.filter(is_active=True).select_related('user').order_by("-published_at")

        # Поиск по тексту
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(city__icontains=query) |
                Q(country__icontains=query) |
                Q(requirements__icontains=query)
            )

        # Фильтр по типу работы
        work_type = self.request.GET.get("work_type")
        if work_type:
            queryset = queryset.filter(work_type=work_type)

        # Фильтр по времени работы
        work_time = self.request.GET.get("work_time")
        if work_time:
            queryset = queryset.filter(work_time=work_time)

        # Фильтр по зарплате
        min_salary = self.request.GET.get("min_salary")
        if min_salary:
            queryset = queryset.filter(salary__gte=int(min_salary))

        max_salary = self.request.GET.get("max_salary")
        if max_salary:
            queryset = queryset.filter(salary__lte=int(max_salary))

        # Фильтр по удаленной работе
        is_remote = self.request.GET.get("is_remote")
        if is_remote:
            queryset = queryset.filter(is_remote=(is_remote == 'true'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'work_type_selected': self.request.GET.get('work_type', ''),
            'work_time_selected': self.request.GET.get('work_time', ''),
            'search_query': self.request.GET.get('q', ''),
            'min_salary': self.request.GET.get('min_salary', ''),
            'max_salary': self.request.GET.get('max_salary', ''),
            'is_remote_selected': self.request.GET.get('is_remote', ''),
            'work_choices': WORK_CHOICES,
            'work_time_choices': WORK_TIME_CHOICES,
        })
        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            self.object_list = self.get_queryset()
            page = request.GET.get("page", 1)
            paginator = self.get_paginator(self.object_list, self.paginate_by)

            try:
                vacancies = paginator.page(page)
            except PageNotAnInteger:
                vacancies = paginator.page(1)
            except EmptyPage:
                vacancies = paginator.page(paginator.num_pages)

            html = render_to_string("miniapp/partials/vacancy_list.html", {"vacancies": vacancies})
            return JsonResponse({
                "html": html,
                "has_next": vacancies.has_next()
            })
        return super().get(request, *args, **kwargs)


def verify_telegram_webapp(data: dict, bot_token: str):
    """
    Проверяем подпись Telegram WebApp.
    """
    check_string = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()) if k != 'hash')
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hmac_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(hmac_hash, data.get('hash', ''))


class ProfilePageView(View):
    template_name = "miniapp/profile.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class SettingsPageView(View):
    template_name = "miniapp/settings.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class MiniAppProfileDataView(View):
    def get(self, request, *args, **kwargs):
        tg_id = request.GET.get("tg_id")
        page = int(request.GET.get("page", 1))
        items_per_page = 10  # Добавляем пагинацию
        responses = None

        if not tg_id:
            return JsonResponse({"status": "error", "message": "tg_id не передан"})

        try:
            profile = TelegramProfile.objects.select_related("user").get(telegram_id=tg_id)
        except TelegramProfile.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Профиль не найден"})

        user = profile.user
        data = {
            "status": "ok",
            "connected": True,
            "site_user": {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            },
            "telegram": {
                "id": profile.telegram_id,
                "username": profile.username,
            }
        }

        # --- Данные для вкладок ---
        items_html = ""
        has_next = False

        if user.user_r:  # работодатель
            # Пагинация для вакансий
            vacancies = Vacancy.objects.filter(user_id=user.id, is_active=True)
            paginator = Paginator(vacancies, items_per_page)
            responses = VacancyResponse.objects.filter(vacancy__user=user).select_related('vacancy', 'anketa', 'worker').order_by('-responded_at')
            try:
                page_obj = paginator.page(page)
                vacancies_page = page_obj.object_list
                has_next = page_obj.has_next()
            except EmptyPage:
                vacancies_page = []
                has_next = False

            items_html = render_to_string(
                "miniapp/partials/profile_vacancy_list.html",
                {"vacancies": vacancies_page}
            )

        else:  # соискатель
            # Пагинация для анкет
            responses = VacancyResponse.objects.filter(worker=user).select_related('vacancy', 'anketa').order_by('-responded_at')
            ankets = Anketa.objects.filter(user=user, is_active=True)
            paginator = Paginator(ankets, items_per_page)

            try:
                page_obj = paginator.page(page)
                ankets_page = page_obj.object_list
                has_next = page_obj.has_next()
            except EmptyPage:
                ankets_page = []
                has_next = False

            items_html = render_to_string(
                "miniapp/partials/anketa_list.html",
                {"ankets": ankets_page}
            )

        data.update({
            "user_r": user.user_r,
            "html": items_html,
            "has_next": has_next,
            "current_page": page,
            "responses": [
                {
                    "id": r.id,
                    "vacancy_id": r.vacancy.id,
                    "vacancy_title": r.vacancy.title,
                    "anketa_id": r.anketa.id if r.anketa else None,
                    "worker_id": r.worker.id if r.worker else None,
                    "responded_at": r.responded_at.strftime("%Y-%m-%d %H:%M"),
                }
                for r in responses
            ]
        })

        return JsonResponse(data)


def _get_user_by_tg(request):
    tg_id = get_tg_id(request)
    if not tg_id:
        return None, JsonResponse({"success": False, "error": "tg_id отсутствует"}, status=400)
    try:
        prof = TelegramProfile.objects.select_related('user').get(telegram_id=tg_id)
        if not prof.user:
            return None, JsonResponse({"success": False, "error": "Telegram профиль не связан с пользователем"}, status=403)
        return prof.user, None
    except TelegramProfile.DoesNotExist:
        return None, JsonResponse({"success": False, "error": "Профиль Telegram не найден"}, status=404)

@csrf_exempt
def miniapp_respond_vacancy(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    telegram_id = request.headers.get("X-Telegram-Id")
    if not telegram_id:
        return JsonResponse({"error": "No Telegram ID"}, status=400)

    profile = TelegramProfile.objects.filter(telegram_id=telegram_id).select_related("user").first()
    if not profile or not profile.user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user = profile.user
    if user.user_r:
        return JsonResponse({"error": "Только соискатели могут откликаться."}, status=403)

    vacancy = get_object_or_404(Vacancy, pk=pk)
    anketa_id = json.loads(request.body).get('anketa_id')
    anketa = Anketa.objects.filter(user=user, id=anketa_id, is_active=True).first()
    if not anketa:
        return JsonResponse({"error": "Анкета не найдена или не активна"}, status=400)

    if VacancyResponse.objects.filter(worker=user, vacancy=vacancy).exists():
        return JsonResponse({"error": "Вы уже откликались."}, status=400)

    VacancyResponse.objects.create(
        worker=user,
        vacancy=vacancy,
        anketa=anketa
    )
    return JsonResponse({"success": True, "message": "Отклик отправлен!"})


@csrf_exempt
def miniapp_toggle_favorite(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    telegram_id = request.headers.get("X-Telegram-Id")
    if not telegram_id:
        return JsonResponse({"error": "No Telegram ID"}, status=400)

    profile = TelegramProfile.objects.filter(telegram_id=telegram_id).select_related("user").first()
    if not profile or not profile.user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user = profile.user
    vacancy = get_object_or_404(Vacancy, pk=pk)

    if user in vacancy.favorite_by.all():
        vacancy.favorite_by.remove(user)
        return JsonResponse({"success": True, "favorite": False, "message": "Вакансия удалена из избранного"})
    else:
        vacancy.favorite_by.add(user)
        return JsonResponse({"success": True, "favorite": True, "message": "Вакансия добавлена в избранное"})


class MiniAppProfileResponsesView(View):
    def get(self, request, *args, **kwargs):
        tg_id = request.GET.get("tg_id")
        if not tg_id:
            return JsonResponse({"status": "error", "message": "tg_id не передан"})

        try:
            profile = TelegramProfile.objects.select_related("user").get(telegram_id=tg_id)
        except TelegramProfile.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Профиль не найден"})

        user = profile.user

        if user.user_r:  # работодатель
            responses = VacancyResponse.objects.filter(
                vacancy__user=user
            ).select_related("vacancy", "anketa", "worker").order_by("-responded_at")
        else:  # соискатель
            responses = VacancyResponse.objects.filter(
                worker=user
            ).select_related("vacancy", "anketa").order_by("-responded_at")

        data = {
            "status": "ok",
            "responses": [
                {
                    "id": r.id,
                    "title": getattr(r.vacancy, "title", None) or getattr(r.anketa, "title", None),
                    "status": r.status,
                    "date": r.responded_at.isoformat(),
                    "message": getattr(r, "message", None),
                }
                for r in responses
            ]
        }
        return JsonResponse(data)


@csrf_exempt
def user_anketas(request):
    tg_id = request.GET.get("tg_id")
    if not tg_id:
        return JsonResponse({"error": "tg_id не передан"}, status=400)

    profile = TelegramProfile.objects.filter(telegram_id=tg_id).select_related("user").first()
    if not profile or not profile.user:
        return JsonResponse({"error": "Пользователь не найден"}, status=404)

    ankets = Anketa.objects.filter(user=profile.user, is_active=True)
    anketa_list = [{"id": a.id, "title": a.title} for a in ankets]

    return JsonResponse({"anketas": anketa_list})

@csrf_exempt
def has_responded(request, pk):
    tg_id = request.GET.get("tg_id")
    if not tg_id:
        return JsonResponse({"error": "tg_id не передан"}, status=400)

    profile = TelegramProfile.objects.filter(telegram_id=tg_id).select_related("user").first()
    if not profile or not profile.user:
        return JsonResponse({"error": "Пользователь не найден"}, status=404)

    vacancy = Vacancy.objects.filter(pk=pk).first()
    if not vacancy:
        return JsonResponse({"error": "Вакансия не найдена"}, status=404)

    response = VacancyResponse.objects.filter(worker=profile.user, vacancy=vacancy).first()
    if response:
        return JsonResponse({"responded": True, "anketa": response.anketa.id})
    return JsonResponse({"responded": False, "anketa": None})


class FavoriteVacanciesView(View):
    template_name = "miniapp/favorite_vacancies.html"

    def get(self, request, *args, **kwargs):
        tg_id = get_tg_id(request)

        if not tg_id:
            # Рендерим шаблон с JavaScript, который сам обработает загрузку
            return render(request, self.template_name, {
                'has_tg_id': False
            })

        try:
            profile = TelegramProfile.objects.select_related('user').get(telegram_id=tg_id)
            user = profile.user
            vacancies = Vacancy.objects.filter(favorite_by=user, is_active=True).order_by("-published_at")

            return render(request, self.template_name, {
                'has_tg_id': True,
                'vacancies': vacancies,
                'telegram_profile': profile,
                'tg_id': tg_id
            })

        except TelegramProfile.DoesNotExist:
            return render(request, self.template_name, {
                'has_tg_id': True,
                'error': 'Профиль не найден. Сначала подключите аккаунт через сайт.'
            })


class MiniAppFavoriteVacanciesDataView(View):
    def get(self, request, *args, **kwargs):
        tg_id = get_tg_id(request)

        if not tg_id:
            return JsonResponse({
                "status": "error",
                "message": "Telegram ID не получен"
            })

        try:
            profile = TelegramProfile.objects.select_related("user").get(telegram_id=tg_id)
            user = profile.user

            favorites = Vacancy.objects.filter(favorite_by=user, is_active=True).order_by("-published_at")

            html = render_to_string(
                "miniapp/partials/vacancy_list.html",
                {"vacancies": favorites}
            )

            return JsonResponse({
                "status": "ok",
                "html": html,
                "count": favorites.count(),
            })

        except TelegramProfile.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Профиль не найден. Сначала подключите аккаунт через сайт."
            })


def get_filters(request):
    tg_id = request.GET.get("tg_id")
    profile = TelegramProfile.objects.filter(telegram_id=tg_id).first()
    if not profile:
        return JsonResponse({"error": "not_found"}, status=404)
    return JsonResponse({"filters": profile.filters})


@csrf_exempt
@require_POST
def update_filters(request):
    data = json.loads(request.body)
    tg_id = data.get('tg_id')
    keyword = data.get('keyword')
    action = data.get('action')

    profile = TelegramProfile.objects.filter(telegram_id=tg_id).first()
    if not profile:
        return JsonResponse({'error': 'Profile not found'}, status=404)

    filters = profile.filters or []

    if action == 'add' and keyword not in filters:
        filters.append(keyword)
    elif action == 'remove' and keyword in filters:
        filters.remove(keyword)

    profile.filters = filters
    profile.save()

    return JsonResponse({'filters': filters})


def vacancies_by_keywords(request):
    try:
        tg_id = request.GET.get('tg_id')
        page = int(request.GET.get('page', 1))
        per_page = 20

        if not tg_id:
            return JsonResponse({"html": "<p>Не указан ID пользователя</p>", "has_next": False})

        profile = TelegramProfile.objects.filter(telegram_id=tg_id).first()
        if not profile:
            return JsonResponse({"html": "<p>Профиль не найден</p>", "has_next": False})

        keywords = profile.filters or []
        if not keywords:
            return JsonResponse({"html": "<p>Добавьте ключевые слова для поиска</p>", "has_next": False})

        # Создаем общий запрос для всех ключевых слов
        from django.db.models import Q
        query = Q()
        for kw in keywords:
            query |= Q(title__icontains=kw) | Q(description__icontains=kw)

        # Получаем вакансии с пагинацией
        vacancies = Vacancy.objects.filter(query).distinct().order_by('-published_at')

        total_count = vacancies.count()
        start = (page - 1) * per_page
        end = start + per_page

        paginated_vacancies = vacancies[start:end]
        has_next = end < total_count

        html = render_to_string("miniapp/partials/vacancy_list.html", {
            "vacancies": paginated_vacancies
        })

        return JsonResponse({"html": html, "has_next": has_next})

    except Exception as e:
        return JsonResponse({"html": f"<p>Ошибка: {str(e)}</p>", "has_next": False})


def get_filters(request):
    tg_id = request.GET.get('tg_id')
    profile = TelegramProfile.objects.filter(telegram_id=tg_id).first()
    if not profile:
        return JsonResponse({'error': 'Profile not found'}, status=404)

    return JsonResponse({'filters': profile.filters or []})


def profile_data(request):
    tg_id = request.GET.get('tg_id')
    profile = TelegramProfile.objects.filter(telegram_id=tg_id).first()
    if not profile:
        return JsonResponse({'error': 'Profile not found'}, status=404)

    return JsonResponse({
        'user_r': profile.user.user_r,
        'keywords': profile.filters or []
    })
