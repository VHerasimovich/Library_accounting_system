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
from .forms import SignupForm, ProfileInfoEdit, ArticleInfo, FictionBookInfo, ScienceBookInfo
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

    return render(request, 'profile_details.html', {'user_info': user_info,
                                                    'user_address': user_address})


@login_required
def common_library_unit_info(request, unit_type):
    all_articles = all_science_books = all_fiction_books = None
    if unit_type == 'articles':
        all_articles = Article.objects.all()
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
    form = None
    current_unit = None

    if unit_type == 'edit_article':
        current_unit = Article.objects.get(pk=unit_number)
    elif unit_type == 'edit_fiction_book':
        current_unit = FictionBook.objects.get(pk=unit_number)
    elif unit_type == 'edit_science_book':
        current_unit = ScienceBook.objects.get(pk=unit_number)

    all_fields = current_unit._meta.get_fields()
    initial_data = {current_field.name: getattr(current_unit, current_field.name) for current_field in all_fields
                    if current_field.name != 'libraryunit'    # not displayed
                    and current_field.name != 'id'            # not displayed
                    and current_field.name != 'work_author'}  # need to prepare
    # preparing lists with authors names and surnames
    current_authors = current_unit.work_author.all()
    author_name = []
    author_surname = []
    for each_author in current_authors:
        author_name.append(each_author.author_name)
        author_surname.append(each_author.author_surname)

    initial_data.update({'author_name': author_name,
                         'author_surname': author_surname})    # complete initial library unit dict for the form

    if request.method == 'POST':
        if unit_type == 'edit_article':
            form = ArticleInfo(request.POST, initial=initial_data)
        elif unit_type == 'edit_fiction_book':
            form = FictionBookInfo(request.POST, initial=initial_data)
        elif unit_type == 'edit_science_book':
            form = ScienceBookInfo(request.POST, initial=initial_data)

        if form.has_changed():
            if form.is_valid():
                changed_fields = form.changed_data
                for field_to_save in changed_fields:
                    if field_to_save != 'author_name' and field_to_save != 'author_surname':
                        setattr(current_unit, field_to_save, form.cleaned_data.get(field_to_save))
                # parse name from form field
                item = 0
                db_index = 0
                for name in form.cleaned_data.get('author_name').split("\'"):
                    # first is '[', second is name, third is ',' etc.
                    if item % 2:
                        current_authors[db_index].author_name = name
                        db_index += 1
                    item += 1

                # parse surname from form field
                item = 0
                db_index = 0
                for surname in form.cleaned_data.get('author_surname').split("\'"):
                    # first is '[', second is name, third is ',' etc.
                    if item % 2:
                        current_authors[db_index].author_surname = surname
                        db_index += 1
                    item += 1

                # updating authors in the DB
                for author in range(len(current_authors)):
                    Author.objects.filter(author_name=author_name[author]).\
                        filter(author_surname=author_surname[author]).\
                        update(author_name=current_authors[author].author_name)
                    Author.objects.filter(author_name=author_name[author]).\
                        filter(author_surname=author_surname[author]).\
                        update(author_surname=current_authors[author].author_surname)

            current_unit.save()
            current_authors.update()
    else:
        if unit_type == 'edit_article':
            form = ArticleInfo(initial=initial_data)
        elif unit_type == 'edit_fiction_book':
            form = FictionBookInfo(initial=initial_data)
        elif unit_type == 'edit_science_book':
            form = ScienceBookInfo(initial=initial_data)

    unit_type_title = unit_type.replace('_', ' ')    # prepare unit_type argument for the page title
    unit_type_title = unit_type_title.title()
    return render(request, 'library_unit_edit.html', {'form': form,
                                                      'unit_type': unit_type_title})


@login_required()
def library_unit_add(request, unit_type):
    form = unit_model = None
    if request.method == 'POST':
        if unit_type == 'article':
            form = ArticleInfo(request.POST)
            unit_model = Article
        elif unit_type == 'fiction_book':
            form = FictionBookInfo(request.POST)
            unit_model = FictionBook
        elif unit_type == 'science_book':
            form = ScienceBookInfo(request.POST)
            unit_model = ScienceBook

        if form.is_valid():
            unit_fields = {}
            new_unit = unit_model(id=unit_model.objects.all().count())
            for current_field in form.fields:
                # author name, surname parsing and storing
                if current_field == 'author_name':
                    name_string = form.cleaned_data.get('author_name').split(",")
                    surname_string = form.cleaned_data.get('author_surname').split(",")
                    i = 0
                    new_work_authors = []
                    for one_name in name_string:
                        new_author = None
                        new_author = Author(author_name=one_name, author_surname=surname_string[i])
                        new_work_authors.append(new_author)
                        new_author.save()   # need to be reviewed! too many DB access
                        i += 1
                # library unit fields preparing for save
                elif current_field != 'author_name' and current_field != 'author_surname':
                    unit_fields.update({current_field: form.cleaned_data.get(current_field)})
            new_unit = unit_model(**unit_fields)    # save fields except work_author
            new_unit.save()
            new_unit.work_author.add(*new_work_authors)    # save work_author field; *.add since many-to-many

    else:
        if unit_type == 'article':
            form = ArticleInfo()
        elif unit_type == 'fiction_book':
            form = FictionBookInfo()
        elif unit_type == 'science_book':
            form = ScienceBookInfo()

    return render(request, 'library_unit_add.html', {'form': form,
                                                     'unit_type': unit_type})


@login_required()
def library_unit_delete(request, unit_type, unit_number):
    current_unit = None
    if unit_type == 'delete_article':
        current_unit = Article.objects.get(pk=unit_number)
    elif unit_type == 'delete_science_book':
        current_unit = ScienceBook.objects.get(pk=unit_number)
    elif unit_type == 'delete_fiction_book':
        current_unit = FictionBook.objects.get(pk=unit_number)

    if current_unit:
        current_unit.delete()

    return render(request, 'library_unit_delete.html', {'current_unit': current_unit})
