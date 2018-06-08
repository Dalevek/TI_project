# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from django.shortcuts import get_object_or_404
from .models import Image
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from common.decorators import ajax_required
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from actions.utils import create_action
import redis
from django.conf import settings





#Połącz z baza danych Redis
r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


@login_required()
def image_create(request):
    if request.method == 'POST':
        #Formularz wyslany
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            #Dane formularza sa prawidlowe
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            #Przypisanie uzytkownika do elementu
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'dodał obraz', new_item)
            messages.success(request, 'Obraz został dodany.')
            #Przekierowanie do widoku szczegolowego dla nowo utworzonego elementu
            return redirect(new_item.get_absolute_url())
    else:
        #Utworzenie formuarza na podstawie danych dostarcz. przez apke w zadaniu GET
        form = ImageCreateForm(data=request.GET)

        return render(request, 'images/image/create.html', {'section': 'images', 'form': form})


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    total_views = r.incr('image:{}:views'.format(image.id))
    r.zincrby('image_ranking', image.id, 1)
    return render(request,
                  'images/image/detail.html',
                  {'section': 'images',
                   'image': image,
                   'total_views': total_views})


@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'polubił',image)
            else:
                image.users_like.remove(request.user)
                create_action(request.user, 'przestał lubić', image)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'ok'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        #Jezeli zmienna page nie jest liczba calkowita, wowczas pobierana jest pierwsza strona wynikow
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            #Jezeli zadanie jest w technologii AJAX i zmienna page ma wartosc spoza zakresu wowczas zwraca pusta strone
            return HttpResponse('')
        #Jezeli zmienna page ma wartosc wieksza niz numer ostat. strony wynikow, wtedy pobiera ostatnia strone wynikow
        images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request, 'images/image/list_ajax.html', {'section': 'images', 'images': images})
    return render(request, 'images/image/list.html', {'section': 'images', 'images': images})

@login_required
def image_ranking(request):
    #Pobieranie słownika rankingu obrazów
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)
    image_ranking_ids = [int(id) for id in image_ranking]
    #Pobieranie najczesciej wyswietalnych obrazow
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request, 'images/image/ranking.html', {'section': 'images_ranking', 'most_viewed': most_viewed})

@login_required
def trend(request):

    #Pobieranie słownika rankingu obrazów
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)
    image_ranking_ids = [int(id) for id in image_ranking]

    #Pobieranie najczesciej wyswietalnych obrazow
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))



    images = Image.objects.all()
    total_views = []
    for x in most_viewed:
        total_views.append(int(r.zscore('image_ranking', x.id)))


    return render(request, 'images/image/chart.html', {'section': 'images_chart', 'most_viewed': most_viewed, 'images': images, 'total_views': total_views})

