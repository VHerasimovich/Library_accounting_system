from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import CitiesList, StreetsList


class ProfileInfo(forms.Form):
    email = forms.EmailField(max_length=200, help_text='Required')
    phone_number = forms.IntegerField(max_value=99999, min_value=00000)
    # select city from the DB
    pick_city = forms.ModelChoiceField(CitiesList.objects.all(), required=False)
    # or add new city name in DB manually
    add_city = forms.CharField(max_length=200,
                               required=False,
                               # city name consist of only letters, '-' and space symbols
                               validators=[RegexValidator(regex='^[-\sA-Za-z]*$',
                                                          message='City name contains invalid symbols!',
                                                          code='invalid')])
    # select street from the DB
    pick_street = forms.ModelChoiceField(StreetsList.objects.all(), required=False)
    # or add new street name in DB manually
    add_street = forms.CharField(max_length=200,
                                 required=False,
                                 # city name consist of only letters, numbers, '-' and space symbols
                                 validators=[RegexValidator(regex='^[-\sA-Za-z0-9]*$',
                                                            message='Street name contains invalid symbols!',
                                                            code='invalid')])
    user_building_number = forms.IntegerField(max_value=999, min_value=000, label='Building number')
    user_apartment_number = forms.IntegerField(max_value=999, min_value=000, label='Apartment number')

    class Meta:
        model = User
        fields = ('email', 'phone_number',
                  'pick_city', 'add_city',
                  'pick_street', 'add_street',
                  'user_building_number', 'user_apartment_number'
                  )


class SignupForm(UserCreationForm, ProfileInfo):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number',
                  'pick_city', 'add_city',
                  'pick_street', 'add_street',
                  'user_building_number', 'user_apartment_number',
                  'password1', 'password2')


class ProfileInfoEdit(ProfileInfo):
    # remove some fields
    pick_city = None
    pick_street = None

    class Meta:
        model = User
        fields = ('email', 'phone_number',
                  'add_city',
                  'add_street',
                  'user_building_number', 'user_apartment_number'
                  )
