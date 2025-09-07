import django_filters
from .models import Vacancy


class VacancyFilter(django_filters.FilterSet):
    min_salary = django_filters.NumberFilter(field_name="salary", lookup_expr="gte")
    max_salary = django_filters.NumberFilter(field_name="salary", lookup_expr="lte")
    city = django_filters.CharFilter(field_name="city", lookup_expr="icontains")
    country = django_filters.CharFilter(field_name="country", lookup_expr="icontains")
    work_type = django_filters.CharFilter(field_name="work_type", lookup_expr="exact")
    is_remote = django_filters.BooleanFilter(field_name="is_remote")

    class Meta:
        model = Vacancy
        fields = ["city", "country", "work_type", "is_remote"]