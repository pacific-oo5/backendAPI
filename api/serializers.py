from rest_framework import serializers
from .models import Vacancy, VacancyView, VacancyResponse, Anketa, VacancyComplaint


class VacancySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Vacancy
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("favorite_by", None)


class VacancyResponseSerializer(serializers.ModelSerializer):
    worker = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = VacancyResponse
        fields = "__all__"
        read_only_fields = ["worker", "responded_at"]
