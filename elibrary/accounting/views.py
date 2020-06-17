from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from .forms import SignupForm, ProfileInfoEdit
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
            current_city = city_street_checker(form, model_type=CitiesList, address_part='city')
            current_street = city_street_checker(form, model_type=StreetsList, address_part='street')
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


def city_street_checker(signup_form, model_type, address_part):

    pick_field = 'pick_' + address_part
    add_field = 'add_' + address_part
    field_name = address_part + '_name'
    pick_field_data = signup_form.cleaned_data.get(pick_field)
    add_field_data = signup_form.cleaned_data.get(add_field)
    # city/street name input check
    if pick_field_data and not add_field_data:
        selected_city_street = model_type.objects.get(**{field_name: pick_field_data})
    elif not pick_field_data and add_field_data:
        city_street_form_info = str(add_field_data.capitalize())
        # check if user tries to add existing city/street name
        try:
            selected_city_street = model_type.objects.get(**{field_name: city_street_form_info})
        except:
            new_city = model_type(**{field_name: city_street_form_info})
            new_city.save()
            selected_city_street = model_type.objects.get(**{field_name: city_street_form_info})
    else:
        # if used both 'pick' and 'add' city, 'pick' will be prioritized
        selected_city_street = model_type.objects.get(**{field_name: pick_field_data})

    return selected_city_street


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
def common_library_unit_info(request, unit_type):
    all_articles = all_science_books = all_fiction_books = None
    if unit_type == 'articles':
        all_articles = Article.objects.all()
        all_article_fields = Article._meta.get_fields()
        for field in all_article_fields:
            print(field.name)

    elif unit_type == 'science_books':
        all_science_books = ScienceBook.objects.all()
    elif unit_type == 'fiction_books':
        all_fiction_books = FictionBook.objects.all()

    return render(request, 'common_info_view.html', {'all_articles': all_articles,
                                                     'all_science_books': all_science_books,
                                                     'all_fiction_books': all_fiction_books})


@login_required
def profile_edit(request):
    user_info = LibraryUserInfo.objects.get(library_user=request.user)
    user_address = LibraryUserAddress.objects.get(library_user=user_info)
    initial_data = {'email': request.user.email,
                    'phone_number': user_info.phone_number,
                    'user_building_number': user_address.building_number,
                    'user_apartment_number': user_address.apartment_number}

    if request.method == 'POST':
        form = ProfileInfoEdit(request.POST, initial=initial_data)
        if form.has_changed():
            if form.is_valid():
                changed_fields = form.changed_data
                for current_field in changed_fields:
                    new_field_data = form.cleaned_data.get(current_field)
                    if current_field == 'email':
                        request.user.email = new_field_data
                    elif current_field == 'phone_number':
                        user_info.phone_number = new_field_data
                    elif current_field == 'add_city':
                        current_city = city_street_checker(form, model_type=CitiesList, address_part='city')
                        user_address.city_name = current_city
                    elif current_field == 'add_street':
                        current_street = city_street_checker(form, model_type=StreetsList, address_part='street')
                        user_address.street_name = current_street
                    elif current_field == 'user_building_number':
                        user_address.building_number = new_field_data
                    elif current_field == 'user_apartment_number':
                        user_address.apartment_number = new_field_data
            request.user.save()
            user_info.save()
            user_address.save()
    else:
        form = ProfileInfoEdit(initial=initial_data)

    return render(request, 'edit_profile_info.html', {'form': form})


@login_required()
def library_unit_details(request, unit_type, unit_number):
    current_article = current_science_book = current_fiction_book = None
    if unit_type == 'article_details':
        current_article = Article.objects.get(pk=unit_number)
    elif unit_type == 'science_book_details':
        current_science_book = ScienceBook.objects.get(pk=unit_number)
    elif unit_type == 'fiction_book_details':
        current_fiction_book = FictionBook.objects.get(pk=unit_number)

    return render(request, 'library_unit_details.html', {'current_article': current_article,
                                                         'current_science_book': current_science_book,
                                                         'current_fiction_book': current_fiction_book})


@login_required()
def library_unit_edit(request, unit_type, unit_number):
    return render(request, 'library_unit_edit.html')
