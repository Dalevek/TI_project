# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile, Contact
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from common.decorators import ajax_required
from django.views.decorators.http import require_POST
from actions.utils import create_action
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.admin import models
from actions.models import Action
from  django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



def history_logs(request):

    logs_list = LogEntry.objects.all().order_by('-action_time')
    paginator = Paginator(logs_list, 10)

    page = request.GET.get('page')
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        logs = paginator.page(1)
    except EmptyPage:
        logs = paginator.page(paginator.num_pages)

    return render(request, 'account/logs.html', {'section': 'logs', 'logs': logs})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Uwierzytelnienie zakończyło się sukcesem.')
                else:
                    return HttpResponse('Konto jest zablokowane.')
            else:
                return HttpResponse('Nieprawidłowe dane uwierzytelniające.')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            #Tworzenie nowego ob. uzytkownika, ale jeszcze nie dodanie do bazy.
            new_user = user_form.save(commit=False)
            #Ustawienie hasla
            new_user.set_password(user_form.cleaned_data['password'])
            #Zapisanie obiektu user
            new_user.save()
            profile = Profile.objects.create(user=new_user)
            create_action(new_user, 'utworzył konto')
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})


@login_required
def dashboard(request):
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id', flat=True)
    if following_ids:
        actions = actions.filter(user_id__in=following_ids).select_related('user', 'user__profile').prefetch_related('target')
    actions = actions[0:10]
    return render(request, 'account/dashboard.html', {'section': 'dashboard', 'actions': actions})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Uaktualnenie profilu zakończyło się sukcesem.')
        else:
            messages.error(request, 'Wystąpił błąd podczas uaktualnania profilu.')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'account/edit.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'account/user/list.html', {'section': 'people', 'users': users})

@login_required
def user_detail(request, username):
    user = get_object_or_404(User,
                             username=username,
                             is_active=True)
    return render(request,
                  'account/user/detail.html',
                  {'section': 'people',
                   'user': user})


@ajax_required
@login_required
@require_POST
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                create_action(request.user, 'zaczął obserwować', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
                create_action(request.user, 'przestał obserwować', user)
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            #return JsonResponse({'status': 'ok'})
            pass
    return JsonResponse({'status': 'ok'})
