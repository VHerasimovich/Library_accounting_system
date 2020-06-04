from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')    # extra field in the form
    phone_number = forms.IntegerField(max_value=99999, min_value=00000)
    user_city = forms.CharField(max_length=200)
    user_street = forms.CharField(max_length=200)
    user_building_number = forms.IntegerField(max_value=999, min_value=000)
    user_apartment_number = forms.IntegerField(max_value=999, min_value=000)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number',
                  'user_city', 'user_street', 'user_building_number',
                  'user_apartment_number', 'password1', 'password2')
