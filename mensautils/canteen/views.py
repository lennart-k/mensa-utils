from collections import OrderedDict
from datetime import date, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Avg, Count
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from mensautils.canteen.forms import RateForm, SubmitServingForm
from mensautils.canteen.models import Canteen, Serving, Rating, InofficialDeprecation, \
    Dish
from mensautils.canteen.statistics import get_most_frequent_dishes, \
    get_most_favored_dishes


def index(request: HttpRequest) -> HttpResponse:
    today = date.today()
    tomorrow = today + timedelta(days=1)
    servings = Serving.objects.filter(date__gte=today, date__lte=tomorrow).select_related(
        'dish', 'canteen').annotate(
        ratings__rating__avg=Avg('ratings__rating'),
        ratings__count=Count('ratings'),
        deprecation_reports__count=Count('deprecation_reports')).order_by(
        'date', 'canteen__name', 'officially_deprecated', 'deprecation_reports__count',
        'dish__name')

    canteen_data = OrderedDict()
    canteen_data[today] = OrderedDict()
    canteen_data[tomorrow] = OrderedDict()

    # fetch canteens explicitly to prevent canteens from not being displayed
    # when there is no data for a day
    canteens = Canteen.objects.order_by('name')
    for canteen in canteens:
        canteen_data[today][canteen] = []
        canteen_data[tomorrow][canteen] = []

    for serving in servings:
        if serving.canteen not in canteen_data[serving.date].keys():
            canteen_data[serving.date][serving.canteen] = []

        canteen_data[serving.date][serving.canteen].append(serving)
    return render(request, 'mensautils/mensa.html', {
        'days': (today, tomorrow),
        'today': today,
        'mensa_data': canteen_data,
        'last_updated': Serving.objects.aggregate(
            Max('last_updated'))['last_updated__max'],
    })


def stats(request: HttpRequest) -> HttpResponse:
    most_frequent_dishes = get_most_frequent_dishes()
    most_favored_dishes = get_most_favored_dishes()
    return render(
        request, 'mensautils/statistics.html', {
            'most_frequent_dishes': most_frequent_dishes,
            'most_favored_dishes': most_favored_dishes,
        })


@login_required
def rate_serving(request: HttpRequest, serving_pk: int) -> HttpResponse:
    serving = get_object_or_404(Serving, pk=serving_pk)

    # check that serving is from today
    if serving.date != date.today():
        messages.warning(
            request, 'Du kannst dieses Gericht heute nicht bewerten.')
        return redirect(reverse('mensautils.canteen:index'))

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


@login_required
def submit_serving(request: HttpRequest, canteen_pk: int) -> HttpResponse:
    canteen = get_object_or_404(Canteen, pk=canteen_pk)

    form = SubmitServingForm()
    if request.method == 'POST':
        form = SubmitServingForm(request.POST)
        if form.is_valid():
            dish = Dish.fuzzy_find_or_create(form.cleaned_data.get('name'),
                                             form.cleaned_data.get('vegetarian'))
            price = form.cleaned_data.get('price')
            price_staff = form.cleaned_data.get('price_staff')
            today = date.today()

            # ensure that serving does not exist yet
            if Serving.objects.filter(
                    dish=dish, canteen=canteen, date=today, price=price,
                    price_staff=price_staff).count() > 0:
                messages.warning(
                    request, 'Das Gericht wurde bereits vorgeschlagen.')
                return redirect(reverse('mensautils.canteen:index'))

            # save submit
            Serving.objects.create(
                dish=dish, canteen=canteen, date=today, price=price,
                price_staff=price_staff, official=False)
            messages.success(
                request, 'Das Gericht wurde erfolgreich gespeichert.')
            return redirect(reverse('mensautils.canteen:index'))

    return render(
        request, 'mensautils/submit_serving.html', {
            'canteen': canteen,
            'form': form,
        })


@login_required
def report_deprecation(request: HttpRequest, serving_pk: int) -> HttpResponse:
    serving = get_object_or_404(Serving, pk=serving_pk)

    # check that serving is from today
    if serving.date != date.today():
        messages.warning(
            request, 'Der Eintrag ist nicht von heute. Daher kann er nicht als '
                     'falsch markiert werden.')
        return redirect(reverse('mensautils.canteen:index'))

    # check if user has reported this serving already
    if InofficialDeprecation.objects.filter(
            serving=serving, reporter=request.user).count() > 0:
        messages.warning(
            request, 'Du hast dieses Gericht bereits als falsch gemeldet.')
        return redirect(reverse('mensautils.canteen:index'))

    form = RateForm()
    if request.method == 'POST':
        # save rating
        InofficialDeprecation.objects.create(reporter=request.user, serving=serving)
        messages.success(
            request, 'Die Meldung wurde erfolgreich gespeichert. Sobald mindestens '
                     '{} Nutzer das Gericht gemeldet haben, wird es als veraltert '
                     'angesehen.'.format(settings.MIN_REPORTS))
        return redirect(reverse('mensautils.canteen:index'))

    return render(
        request, 'mensautils/report_deprecation.html', {
            'serving': serving,
        })
