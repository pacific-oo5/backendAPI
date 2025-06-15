from dj_rest_auth.registration.views import RegisterView
from .serializers import CustomRegisterSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer


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


# class UserListView(generics.ListAPIView):
#     queryset = User.objects.all()