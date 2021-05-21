from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

GENDER_CHOICES = [
  ('male', 'Male'),
  ('female', 'Female')
]

OCCUPATION_CHOICES = [
  ('administrator', 'Administrator'),
  ('artist', 'Artist'),
  ('doctor', 'Doctor'),
  ('educator', 'Educator'),
  ('engineer', 'Engineer'),
  ('entertainment', 'Entertainment'),
  ('executive', 'Executive'),
  ('healthcare', 'Healthcare'),
  ('homemaker', 'Homemaker'),
  ('lawyer', 'Lawyer'),
  ('librarian', 'Librarian'),
  ('marketing', 'Marketing'),
  ('none', 'None'),
  ('other', 'Other'),
  ('programmer', 'Programmer'),
  ('retired', 'Retired'),
  ('salesman', 'Salesman'),
  ('scientist', 'Scientist'),
  ('student', 'Student'),
  ('technician', 'Technician'),
  ('writer', 'Writer')
]


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    age = forms.IntegerField(min_value=1, max_value=100, label='age', required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, label='gender', required=True)
    occupation = forms.ChoiceField(choices=OCCUPATION_CHOICES, label='occupation', required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'age', 'gender', 'occupation', 'password1']
    
    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.age = self.cleaned_data['age']
        user.gender = self.cleaned_data['gender']
        user.occupation = self.cleaned_data['occupation']
        if commit:
            user.save()
        return user