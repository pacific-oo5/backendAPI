from .models import Vacancy, Anketa
from django import forms


class VacancyForm(forms.ModelForm):
    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        
    class Meta:
        model = Vacancy
        fields = [
            'title',
            'description',
            'about_me',
            'work_type',
            'work_time',
            'salary',
            'country',
            'city',
            'is_remote',
            'requirements',
            'responsibilities',
            'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'about_me': forms.Textarea(attrs={'rows': 3}),
            'requirements': forms.Textarea(attrs={'rows': 3}),
            'responsibilities': forms.Textarea(attrs={'rows': 3}),
            'is_remote': forms.CheckboxInput(),
            'is_active': forms.CheckboxInput(),
        }


class AnketaForm(forms.ModelForm):
    class Meta:
        model = Anketa
        fields = ['title', 'about_me', 'experience', 'country', 'city', 'phone_number', 'is_active']
        widgets = {
            'about_me': forms.Textarea(attrs={'rows': 3}),
            'experience': forms.Textarea(attrs={'rows': 3}),
        }