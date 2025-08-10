from django.shortcuts import get_object_or_404, render
from api.models import Vacancy


def vacancy_detail(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id, is_active=True)
    return render(request, 'vacancy/vacancy_detail.html', {'vacancy': vacancy})

# views.py
def employers(request):
    return render(request, 'main/employers.html')

def applicants(request):
    return render(request, 'main/applicants.html')