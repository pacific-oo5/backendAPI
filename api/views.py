from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import VacancyResponse, Vacancy, Anketa
from .permissions import IsRecruiter, IsNotRecruiter
from .serializers import VacancySerializer, VacancyResponseSerializer, AnketaSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import viewsets


class VacancyListView(generics.ListAPIView):
    queryset = Vacancy.objects.filter(is_active=True).order_by('-published_at')
    serializer_class = VacancySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = {
        'salary': ['gte', 'lte'],
        'work_type': ['exact'],
        'work_time': ['exact'],
    }
    search_fields = ('name', 'city', 'country')

class VacancyDetailView(generics.RetrieveAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = [permissions.AllowAny]


class VacancyViewSet(viewsets.ModelViewSet):
    serializer_class = VacancySerializer
    permission_classes = [permissions.IsAuthenticated, IsRecruiter]

    def get_queryset(self):
        return Vacancy.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RespondToVacancyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        anketa_id = request.data.get("anketa_id")

        if not anketa_id:
            return Response({'detail': 'Анкета не выбрана.'}, status=400)

        try:
            vacancy = Vacancy.objects.get(id=pk)
        except Vacancy.DoesNotExist:
            return Response({'detail': 'Vacancy not found'}, status=404)

        try:
            anketa = Anketa.objects.get(id=anketa_id, user=user, is_active=True)
        except Anketa.DoesNotExist:
            return Response({'detail': 'Анкета не найдена или не активна.'}, status=404)

        obj, created = VacancyResponse.objects.get_or_create(worker=user, vacancy=vacancy)

        if not created:
            return Response({'detail': 'Уже откликнулись.'}, status=400)

        obj.anketa = anketa
        obj.save()

        return Response({'detail': 'Успешно откликнулись.'}, status=201)


class VacancyResponsesView(generics.ListAPIView):
    serializer_class = VacancyResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        vacancy_id = self.kwargs.get('vacancy_id')
        return VacancyResponse.objects.filter(vacancy__id=vacancy_id, vacancy__user=self.request.user)


class FavoriteVacancyListView(generics.ListAPIView):
    serializer_class = VacancySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vacancy.objects.filter(responses__worker=self.request.user, responses__is_favorite=True).distinct()


class AddToFavoritesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vacancy.objects.filter(user=self.request.user)


# class VacancyViewSet(viewsets.ModelViewSet):
#     queryset = Vacancy.objects.filter(is_active=True)
#     serializer_class = VacancySerializer
#     filterset_class = VacancyFilter
#     filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
#     search_fields = ['name', 'description', 'location']


class AcceptOrRejectResponseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VacancyResponse.objects.filter(worker=self.request.user)


class FavoriteVacancyListView(generics.ListAPIView):
    serializer_class = VacancySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vacancy.objects.filter(responses__worker=self.request.user, responses__is_favorite=True).distinct()


class AnketaViewSet(viewsets.ModelViewSet):
    serializer_class = AnketaSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotRecruiter]

    def get_queryset(self):
        return Anketa.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class PublicAnketaViewSet(viewsets.ViewSet):
    def retrieve(self, request, username=None, pk=None):
        User = get_user_model()
        user = get_object_or_404(User, username=username)
        anketa = get_object_or_404(Anketa, user=user, pk=pk, is_active=True)
        serializer = AnketaSerializer(anketa)
        return Response(serializer.data)


class MyContentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.user_r:
            vacancies = Vacancy.objects.filter(user=user)
            serializer = VacancySerializer(vacancies, many=True)
            return Response({"vacancies": serializer.data})
        else:
            ankets = Anketa.objects.filter(user=user)
            serializer = AnketaSerializer(ankets, many=True)
            return Response({"ankets": serializer.data})


class AcceptOrRejectResponseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, vacancy_id, response_id):
        try:
            response = VacancyResponse.objects.select_related('vacancy').get(id=response_id, vacancy__id=vacancy_id)
        except VacancyResponse.DoesNotExist:
            return Response({'detail': 'Response not found'}, status=404)

        if response.vacancy.user != request.user:
            return Response({'detail': 'Нет доступа'}, status=403)

        status_value = request.data.get('status')  # "accepted" или "rejected"
        if status_value not in ['accepted', 'rejected']:
            return Response({'detail': 'Недопустимый статус'}, status=400)

        response.status = status_value
        response.save()

        return Response({'detail': f'Response {status_value}'}, status=200)