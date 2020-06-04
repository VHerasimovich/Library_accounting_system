from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CitiesList, StreetsList


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')    # extra field in the form
    phone_number = forms.IntegerField(max_value=99999, min_value=00000)
    pick_city = forms.ModelChoiceField(CitiesList.objects.all())
    # add_city = forms.CharField(max_length=200)
    pick_street = forms.ModelChoiceField(StreetsList.objects.all(), required=False)
    # add_street = forms.CharField(max_length=200)
    user_building_number = forms.IntegerField(max_value=999, min_value=000)
    user_apartment_number = forms.IntegerField(max_value=999, min_value=000)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number',
                  'pick_city',    # TODO: 'add_city'
                  'pick_street',    # TODO: 'add_street'
                  'user_building_number', 'user_apartment_number',
                  'password1', 'password2')
