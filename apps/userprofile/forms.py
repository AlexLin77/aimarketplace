from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

GENDER_CHOICES = [
  ('male', 'Male'),
  ('female', 'Female')
]

REGION_CHOICES = [
  ('northwest', 'Northwest'),
  ('west', 'West'),
  ('southwest', 'Southwest'),
  ('midwest', 'Midwest'),
  ('south', 'South'),
  ('southeast', 'Southeast'),
  ('east', 'East'),
  ('northeast', 'Northeast')
]


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    age = forms.IntegerField(min_value=1, max_value=100, label='age', required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, label='gender', required=True)
    region = forms.ChoiceField(choices=REGION_CHOICES, label='region', required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'age', 'gender', 'region', 'password1']
    
    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.age = self.cleaned_data['age']
        user.gender = self.cleaned_data['gender']
        user.region = self.cleaned_data['region']
        if commit:
            user.save()
        return user