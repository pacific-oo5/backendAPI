from rest_framework import generics, permissions
from api.models import Vacancy
from api.serializers import VacancySerializer
from rest_framework.exceptions import PermissionDenied


class VacancyListView(generics.ListAPIView):
    queryset = Vacancy.objects.filter(is_active=True)
    serializer_class = VacancySerializer
    permission_classes = [permissions.AllowAny]


class VacancyCreateView(generics.CreateAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.user_r:
            raise PermissionError("Нет прав для создания вакансии")
        serializer.save(user=self.request.user)


class VacancyDetailView(generics.RetrieveAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = [permissions.AllowAny]


class VacancyUpdateView(generics.UpdateAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.user:
            raise PermissionDenied("Вы можете редактировать только свои вакансии.")
        if not self.request.user.user_r:
            raise PermissionDenied("Вы не можете редактировать вакансии.")
        serializer.save()


class VacancyDeleteView(generics.DestroyAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        if self.request.user != instance.user or not self.request.user.user_r:
            raise PermissionDenied("Вы не можете удалить эту вакансию.")
        instance.delete()
