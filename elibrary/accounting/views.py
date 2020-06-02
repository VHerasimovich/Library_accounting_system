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
    return render(request, 'test_profile_details.html')


@login_required
def detailed_library_unit_info(request, unit_type):
    all_articles = all_science_books = all_fiction_books = None
    if unit_type == 1:
        all_articles = Article.objects.all()
    elif unit_type == 2:
        all_science_books = ScienceBook.objects.all()
    elif unit_type == 3:
        all_fiction_books = FictionBook.objects.all()

    return render(request, 'detailed_info_view.html', {'all_articles': all_articles,
                                                       'all_science_books': all_science_books,
                                                       'all_fiction_books': all_fiction_books})
