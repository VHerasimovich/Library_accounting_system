from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django import forms
from .tokens import account_activation_token
from .forms import SignupForm
from .models import *


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False    # non active user, i.e. user without email confirmation can't login
            user.save()
            user_info = LibraryUserInfo(library_user=user,
                                        phone_number=form.cleaned_data.get('phone_number'))
            user_info.save()
            current_city, current_street = city_street_checker(form)
            user_address = LibraryUserAddress(library_user=LibraryUserInfo.objects.get(library_user=user),
                                              city_name=current_city,
                                              street_name=current_street,
                                              building_number=form.cleaned_data.get('user_building_number'),
                                              apartment_number=form.cleaned_data.get('user_apartment_number'))
            user_address.save()
            current_site = get_current_site(request)
            mail_subject = 'Account activation.'
            message = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return HttpResponse('Confirm your email address to finalize registration process, please!')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


def city_street_checker(signup_form):
    # city name input check
    if signup_form.cleaned_data.get('pick_city') and not(signup_form.cleaned_data.get('add_city')):
        selected_city = CitiesList.objects.get(city_name=signup_form.cleaned_data.get('pick_city'))
    elif not(signup_form.cleaned_data.get('pick_city')) and signup_form.cleaned_data.get('add_city'):
        city_form_info = str(signup_form.cleaned_data.get('add_city')).capitalize()
        new_city = CitiesList(city_name=city_form_info)
        new_city.save()
        selected_city = CitiesList.objects.get(city_name=city_form_info)
    else:
        # if used both 'pick' and 'add' city, 'pick' will be prioritized
        selected_city = CitiesList.objects.get(city_name=signup_form.cleaned_data.get('pick_city'))
    # street name input check
    if signup_form.cleaned_data.get('pick_street') and not(signup_form.cleaned_data.get('add_street')):
        selected_street = StreetsList.objects.get(street_name=signup_form.cleaned_data.get('pick_street'))
    elif not(signup_form.cleaned_data.get('pick_street')) and signup_form.cleaned_data.get('add_street'):
        street_form_info = str(signup_form.cleaned_data.get('add_street')).capitalize()
        new_street = StreetsList(street_name=street_form_info)
        new_street.save()
        selected_street = StreetsList.objects.get(street_name=street_form_info)
    else:
        # if used both 'pick' and 'add' street, 'pick' will be prioritized
        selected_street = StreetsList.objects.get(street_name=signup_form.cleaned_data.get('pick_street'))

    return selected_city, selected_street


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('login')
    else:
        return HttpResponse('Invalid activation link!')


@login_required
def profile_detail(request):
    user = request.user
    try:
        user_info = LibraryUserInfo.objects.get(library_user=user)
    except:
        user_info = None
        print("No info for user "+str(user))

    try:
        user_address = LibraryUserAddress.objects.get(library_user=user_info)
    except:
        user_address = None
        print("No address info for user "+str(user_info.library_user))

    if user_address:
        print(user_address.city_name)

    return render(request, 'profile_details.html', {'user_info': user_info,
                                                    'user_address': user_address})


@login_required
def detailed_library_unit_info(request, unit_type):
    all_articles = all_science_books = all_fiction_books = None
    if unit_type == 'articles':
        all_articles = Article.objects.all()
    elif unit_type == 'science_books':
        all_science_books = ScienceBook.objects.all()
    elif unit_type == 'fiction_books':
        all_fiction_books = FictionBook.objects.all()

    return render(request, 'detailed_info_view.html', {'all_articles': all_articles,
                                                       'all_science_books': all_science_books,
                                                       'all_fiction_books': all_fiction_books})
