from collections import OrderedDict
from datetime import date, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Avg
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from mensautils.canteen.forms import RateForm
from mensautils.canteen.models import Canteen, Serving, Rating
from mensautils.canteen.statistics import get_most_frequent_dishes


def index(request: HttpRequest) -> HttpResponse:
    today = date.today()
    tomorrow = today + timedelta(days=1)
    servings = Serving.objects.filter(date__gte=today, date__lte=tomorrow).order_by(
        'canteen__name', 'date', 'deprecated', 'dish__name').select_related(
        'dish', 'canteen').annotate(ratings__rating__avg=Avg('ratings__rating'))
    canteen_data = OrderedDict()
    canteen_data[today] = OrderedDict()
    canteen_data[tomorrow] = OrderedDict()
    for serving in servings:
        if serving.canteen.name not in canteen_data[serving.date]:
            canteen_data[serving.date][serving.canteen.name] = []
        canteen_data[serving.date][serving.canteen.name].append(serving)
    return render(request, 'mensautils/mensa.html', {
        'today': today,
        'mensa_data': canteen_data,
        'last_updated': Serving.objects.aggregate(
            Max('last_updated'))['last_updated__max'],
    })


def stats(request: HttpRequest) -> HttpResponse:
    most_frequent_dishes = get_most_frequent_dishes()
    return render(
        request, 'mensautils/statistics.html', {
            'most_frequent_dishes': most_frequent_dishes,
        })


@login_required
def rate_serving(request: HttpRequest, serving_pk: int) -> HttpResponse:
    serving = get_object_or_404(Serving, pk=serving_pk)

    # check if user has rated this serving already
    if Rating.objects.filter(serving=serving, user=request.user).count() > 0:
        messages.warning(
            request, 'Du hast dieses Gericht heute bereits bewertet.')
        return redirect(reverse('mensautils.canteen:index'))

    # check daily rating limit
    if (Rating.objects.filter(user=request.user, serving__date=serving.date).count() >=
            settings.RATING_DAILY_LIMIT):
        messages.warning(
            request, 'Du hast heute bereits die mögliche Anzahl an Gerichten bewertet.')
        return redirect(reverse('mensautils.canteen:index'))

    form = RateForm()
    if request.method == 'POST':
        form = RateForm(request.POST)
        if form.is_valid():
            # save rating
            Rating.objects.create(
                user=request.user, serving=serving,
                rating=form.cleaned_data.get('rating'))
        messages.success(
            request, 'Die Bewertung wurde erfolgreich gespeichert.')
        return redirect(reverse('mensautils.canteen:index'))

    return render(
        request, 'mensautils/rate_serving.html', {
            'serving': serving,
            'form': form,
        })
