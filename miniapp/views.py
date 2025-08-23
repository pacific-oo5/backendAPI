import os

from django.contrib.auth import get_user_model
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.views import generic
from django.template.loader import render_to_string
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api.choices import WORK_CHOICES, WORK_TIME_CHOICES
from api.models import Vacancy, Anketa, VacancyResponse

from django.http import JsonResponse, HttpResponseForbidden

from dotenv import load_dotenv

from miniapp.utils import check_telegram_auth

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