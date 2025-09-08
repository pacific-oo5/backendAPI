from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .filters import VacancyFilter
from .models import Vacancy, VacancyResponse
from .serializers import (
    VacancySerializer,
    VacancyResponseSerializer,
)
from .permissions import IsOwnerOrReadOnly, IsVacancyOwnerOrReadOnly


class VacancyPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.filter(is_active=True).select_related("user")
    serializer_class = VacancySerializer
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = VacancyPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = VacancyFilter
    search_fields = ["title", "description", "requirements", "responsibilities"]
    ordering_fields = ["published_at", "salary"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def respond(self, request, pk=None):
        """Откликнуться на вакансию"""
        vacancy = get_object_or_404(Vacancy, pk=pk)
        serializer = VacancyResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(worker=request.user, vacancy=vacancy)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавить/убрать вакансию в избранное"""
        vacancy = get_object_or_404(Vacancy, pk=pk)
        if request.user in vacancy.favorite_by.all():
            vacancy.favorite_by.remove(request.user)
            return Response({"status": "removed"})
        vacancy.favorite_by.add(request.user)
        return Response({"status": "added"})



class VacancyResponseViewSet(viewsets.ReadOnlyModelViewSet):
    """Только просмотр откликов (без создания/редактирования/удаления)"""
    serializer_class = VacancyResponseSerializer
    permission_classes = [IsVacancyOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return VacancyResponse.objects.none()
        return VacancyResponse.objects.select_related("worker", "vacancy").filter(
            models.Q(worker=user) | models.Q(vacancy__user=user)
        )