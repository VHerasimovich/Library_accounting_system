from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CitiesList, StreetsList


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    phone_number = forms.IntegerField(max_value=99999, min_value=00000)
    pick_city = forms.ModelChoiceField(CitiesList.objects.all(), required=False)    # select city from the DB
    add_city = forms.CharField(max_length=200, required=False)    # or add new city name in DB manually
    pick_street = forms.ModelChoiceField(StreetsList.objects.all(), required=False) # select street from the DB
    add_street = forms.CharField(max_length=200, required=False)    # or add new street name in DB manually
    user_building_number = forms.IntegerField(max_value=999, min_value=000)
    user_apartment_number = forms.IntegerField(max_value=999, min_value=000)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number',
                  'pick_city', 'add_city',
                  'pick_street', 'add_street',
                  'user_building_number', 'user_apartment_number',
                  'password1', 'password2')
