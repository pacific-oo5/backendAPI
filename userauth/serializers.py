from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

class CustomRegisterSerializer(RegisterSerializer):
    user_r = serializers.BooleanField(
        required=False,  # Сделать необязательным, если пользователь не отметит
        default=False,  # По умолчанию считаем, что пользователь не рекрутер
        help_text="Отметьте, если вы хотите публиковать вакансии."
    )

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['user_r'] = self.validated_data.get('user_r', '')
        return data
