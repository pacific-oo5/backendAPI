import os
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .choices import STATUS_CHOICES, WORK_CHOICES, WORK_TIME_CHOICES
from .models import VacancyResponse, Vacancy, Anketa, VacancyView, VacancyComplaint
from .forms import AnketaForm, VacancyForm

from django.utils.translation import gettext_lazy as _

from dotenv import load_dotenv

load_dotenv()

class MyVacancyListView(generic.ListView):
    model = Vacancy
    template_name = 'userauth/profile.html'

    def get_queryset(self):
        return Vacancy.objects.filter(user=self.request.user)
    

class VacancyListView(generic.ListView):
    model = Vacancy
    template_name = 'main/main.html'
    context_object_name = 'vacancies'
    paginate_by = 10

    def get_queryset(self):
        queryset = Vacancy.objects.filter(is_active=True).order_by('-published_at')
        query = self.request.GET.get('q')
        work_type = self.request.GET.get('work_type')
        work_time = self.request.GET.get('work_time')
        min_salary = self.request.GET.get('min_salary')
        max_salary = self.request.GET.get('max_salary')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(city__icontains=query) |
                Q(country__icontains=query)
            )
        if work_type:
            queryset = queryset.filter(work_type=work_type)
        if work_time:
            queryset = queryset.filter(work_time=work_time)
        if min_salary:
            queryset = queryset.filter(salary__gte=min_salary)
        if max_salary:
            queryset = queryset.filter(salary__lte=max_salary)

        return queryset

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            self.object_list = self.get_queryset()
            page = self.request.GET.get('page', 1)
            paginator = self.get_paginator(self.object_list, self.paginate_by)
            vacancies = paginator.get_page(page)
            html = render_to_string('partials/vacancy_list.html', {'vacancies': vacancies})
            return JsonResponse({
                'html': html,
                'has_next': vacancies.has_next()
            })
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'work_type_selected': self.request.GET.get('work_type', ''),
            'work_time_selected': self.request.GET.get('work_time', ''),
            'search_query': self.request.GET.get('q', ''),
            'min_salary': self.request.GET.get('min_salary', ''),
            'max_salary': self.request.GET.get('max_salary', ''),
            'work_choices': WORK_CHOICES,
            'work_time_choices': WORK_TIME_CHOICES,
        })
        return context

class VacancyDetailView(generic.DetailView):
    model = Vacancy
    template_name = 'vacancy/vacancy_detail.html'
    context_object_name = 'vacancy'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and not user.user_r:  # type: ignore # только соискатель
            context['ankets'] = Anketa.objects.filter(user=user, is_active=True)
            context['has_responded'] = self.object.responses.filter(worker=user).exists() # type: ignore
        else:
            context['ankets'] = []
            context['has_responded'] = False
        return context


@login_required
def respond_to_vacancy(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    
    # Только соискатели (user_r == False)
    if request.user.user_r:
        messages.error(request, _("Только соискатели могут откликаться."))
        return redirect('api:vacancy_detail', pk=pk)

    ankets = Anketa.objects.filter(user=request.user, is_active=True)
    
    if request.method == "POST":
        anketa_id = request.POST.get("anketa")
        anketa = get_object_or_404(Anketa, pk=anketa_id, user=request.user)

        # Проверка на дубликат отклика
        if VacancyResponse.objects.filter(worker=request.user, vacancy=vacancy).exists():
            messages.warning(request, _("Вы уже откликались на эту вакансию."))
            return redirect('api:vacancy_detail', pk=pk)

        VacancyResponse.objects.create(
            worker=request.user,
            vacancy=vacancy,
            anketa=anketa
        )
        messages.success(request, _("Отклик отправлен!"))
        return redirect('api:vacancy_detail', pk=pk)

    return render(request, "vacancy/respond_to_vacancy.html", {
        "vacancy": vacancy,
        "ankets": ankets
    })


@login_required
@require_POST
def vacancy_toggle(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, user=request.user)
    action = request.POST.get("action")
    if action == "deactivate":
        vacancy.is_active = False
    elif action == "activate":
        vacancy.is_active = True
    vacancy.save()
    return redirect('profile')

@login_required
def vacancy_stats(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, user=request.user)
    views_count = VacancyView.objects.filter(vacancy=vacancy).count()
    responses_count = VacancyResponse.objects.filter(vacancy=vacancy).count()
    stats = {
        "views": views_count,
        "responses": responses_count,
        "created": vacancy.published_at,
        "is_active": vacancy.is_active,
    }
    return render(request, "vacancy/vacancy_stats.html", {"vacancy": vacancy, "stats": stats})


@require_POST
@login_required
def vacancy_delete(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, user=request.user)
    vacancy.delete()
    return redirect('userauth:profile')


class VacancyUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Vacancy
    form_class = VacancyForm
    template_name = 'vacancy/edit_vacancy.html'

    def get_queryset(self):
        return Vacancy.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('userauth:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vacancy'] = self.object   # передаём vacancy.id в шаблон
        return context
#! FORMS    

class VacancyCreateView(LoginRequiredMixin, generic.CreateView):
    model = Vacancy
    form_class = VacancyForm
    template_name = 'vacancy/vacancy_create.html'
    success_url = reverse_lazy('userauth:profile')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['in_create'] = True  # Устанавливаем False, так как это не страница профиля
        return context

class AnketaCreateView(LoginRequiredMixin, generic.CreateView):
    model = Anketa
    form_class = AnketaForm
    template_name = 'form/anketa_form.html'
    success_url = reverse_lazy('userauth:profile')  # можно на список анкет

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['in_create'] = True  # Устанавливаем False, так как это не страница профиля
        return context


class AnketaDetailView(LoginRequiredMixin, generic.DetailView):
    model = Anketa
    template_name = "anketa/anketa_detail.html"
    context_object_name = "anketa"

    def get(self, request, *args, **kwargs):
        anketa = self.get_object()

        # Если соискатель — доступ только к своей анкете
        if not request.user.user_r: # type: ignore
            if anketa.user != request.user: # type: ignore
                messages.error(request, _("Вы не можете просматривать чужую анкету."))
                return redirect("userauth:profile")

        # Если работодатель — доступ только к анкетам, откликнувшимся на его вакансии
        else:
            has_access = VacancyResponse.objects.filter(
                anketa=anketa,
                vacancy__user=request.user
            ).exists()
            if not has_access:
                return redirect("home")

        return super().get(request, *args, **kwargs)


class AnketaUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Anketa
    form_class = AnketaForm
    template_name = 'form/anketa_form.html'

    def get_success_url(self):
        return reverse_lazy('api:anketa_detail', kwargs={'pk': self.object.pk}) # type: ignore

    def test_func(self):
        # Только владелец анкеты может её редактировать
        return self.get_object().user == self.request.user # type: ignore
    

@login_required
@require_POST
def response_update_status(request, pk):
    response = get_object_or_404(VacancyResponse, pk=pk, vacancy__user=request.user)
    status = request.POST.get('status')

    if response.status == 'accepted':
        return redirect('profile')

    if status in dict(STATUS_CHOICES):
        response.status = status
        response.save()

    return redirect('userauth:profile')


@require_POST
def vacancy_complaint(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    reason = request.POST.get('reason', '').strip()

    if not reason:
        messages.error(request, _("Укажите причину жалобы."))
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.user.is_authenticated:
        # авторизованный пользователь
        VacancyComplaint.objects.create(
            user=request.user,
            vacancy=vacancy,
            reason=reason
        )
    else:
        # анонимный пользователь
        anon_name = request.POST.get('anon_name', '').strip()
        anon_email = request.POST.get('anon_email', '').strip()
        VacancyComplaint.objects.create(
            vacancy=vacancy,
            reason=reason,
            anon_name=anon_name or "Аноним",
            anon_email=anon_email or None
        )

    messages.success(request, _("Жалоба отправлена."))
    return redirect(request.META.get('HTTP_REFERER', '/'))