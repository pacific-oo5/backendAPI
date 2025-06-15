from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

class CustomRegisterSerializer(RegisterSerializer):
    user_r = serializers.BooleanField(required=False)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['user_r'] = self.validated_data.get('user_r', False)
        return data
