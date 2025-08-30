from .models import Vacancy, Anketa
from django import forms


class VacancyForm(forms.ModelForm):
    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        # Если выбран "Практика", скрыть поле salary
        if self.instance.work_type == 'practice':  # или self.data.get('work_type')
            self.fields['salary'].required = False
            self.fields['salary'].widget.attrs['disabled'] = True

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

    def clean(self):
        cleaned_data = super().clean()
        work_type = cleaned_data.get('work_type')
        salary = cleaned_data.get('salary')

        if work_type == 'practice':
            cleaned_data['salary'] = None  # или 0
        else:
            if not salary:
                self.add_error('salary', 'Укажите зарплату')
        return cleaned_data


class AnketaForm(forms.ModelForm):
    class Meta:
        model = Anketa
        fields = ['title', 'about_me', 'experience', 'country', 'city', 'phone_number']
        widgets = {
            'about_me': forms.Textarea(attrs={'rows': 3}),
            'experience': forms.Textarea(attrs={'rows': 3}),
        }