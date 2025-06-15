from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import VacancyResponse, Vacancy
from .serializers import VacancySerializer, RespondedUserSerializer, VacancyResponseSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class VacancyListView(generics.ListAPIView):
    queryset = Vacancy.objects.filter(is_active=True)
    serializer_class = VacancySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = {
        'salary': ['gte', 'lte'],
        'work_type': ['exact'],
        'work_time': ['exact'],
    }
    search_fields = ('name', 'location')


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


class RespondToVacancyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        try:
            vacancy = Vacancy.objects.get(id=pk)
        except Vacancy.DoesNotExist:
            return Response({'detail': 'Vacancy not found'}, status=404)

        obj, created = VacancyResponse.objects.get_or_create(worker=user, vacancy=vacancy)
        if not created:
            return Response({'detail': 'Already responded'}, status=400)

        return Response({'detail': 'Successfully responded'}, status=201)


class AddToFavoritesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, vacancy_id):
        user = request.user
        try:
            vacancy = Vacancy.objects.get(id=vacancy_id)
        except Vacancy.DoesNotExist:
            return Response({'detail': 'Vacancy not found'}, status=404)

        response, _ = VacancyResponse.objects.get_or_create(worker=user, vacancy=vacancy)
        response.is_favorite = True
        response.save()

        return Response({'detail': 'Added to favorites'}, status=200)


class RespondedUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, vacancy_id):
        try:
            vacancy = Vacancy.objects.get(id=vacancy_id)
        except Vacancy.DoesNotExist:
            return Response({'detail': 'Vacancy not found'}, status=404)

        if vacancy.user != request.user:
            return Response({'detail': 'Нет доступа'}, status=403)

        responses = VacancyResponse.objects.filter(vacancy=vacancy).select_related('worker')
        serializer = VacancyResponseSerializer(responses, many=True)
        return Response(serializer.data)


class MyVacancyListView(generics.ListAPIView):
    serializer_class = VacancySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Vacancy.objects.filter(user=self.request.user)
# class VacancyViewSet(viewsets.ModelViewSet):
#     queryset = Vacancy.objects.filter(is_active=True)
#     serializer_class = VacancySerializer
#     filterset_class = VacancyFilter
#     filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
#     search_fields = ['name', 'description', 'location']


class AcceptOrRejectResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, vacancy_id, worker_id):
        try:
            response = VacancyResponse.objects.select_related('vacancy').get(vacancy_id=vacancy_id, worker_id=worker_id)
        except VacancyResponse.DoesNotExist:
            return Response({'detail': 'Response not found'}, status=404)

        if response.vacancy.user != request.user:
            return Response({'detail': 'Нет доступа'}, status=403)

        status_value = request.data.get('status')  # "accepted" или "rejected"
        if status_value not in ['accepted', 'rejected', 'pending']:
            return Response({'detail': 'Недопустимый статус'}, status=400)

        response.status = status_value
        response.save()

        return Response({'detail': f'Response {status_value}'}, status=200)


class UserResponsesView(generics.ListAPIView):
    serializer_class = VacancyResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VacancyResponse.objects.filter(worker=self.request.user)

class FavoriteVacancyListView(generics.ListAPIView):
    serializer_class = VacancySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Vacancy.objects.filter(responses__worker=self.request.user, responses__is_favorite=True).distinct()
