import re
from collections import OrderedDict
from datetime import date, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Avg, Count
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from mensautils.canteen.forms import RateForm, SubmitServingForm, NotificationForm
from mensautils.canteen.models import Canteen, Serving, Rating, InofficialDeprecation, \
    Dish, ServingVerification, Notification, CanteenUserConfig
from mensautils.canteen.statistics import get_most_frequent_dishes, \
    get_most_favored_dishes


def index(request: HttpRequest) -> HttpResponse:
    today = date.today()
    first_day = _get_valid_day(today)
    next_day = _get_valid_day(first_day + timedelta(days=1))
    servings = (Serving.objects.filter(date=first_day) |
                Serving.objects.filter(date=next_day))
    servings = servings.select_related(
        'dish', 'canteen').annotate(
        ratings__rating__avg=Avg('ratings__rating'),
        ratings__count=Count('ratings', distinct=True),
        verifications__count=Count('verifications', distinct=True),
        deprecation_reports__count=Count('deprecation_reports', distinct=True)
    ).order_by(
        'date', 'canteen__name', 'officially_deprecated',
        'deprecation_reports__count', 'dish__name')

    canteen_data = OrderedDict()
    canteen_data[first_day] = OrderedDict()
    canteen_data[next_day] = OrderedDict()

    # fetch canteens explicitly to prevent canteens from not being displayed
    # when there is no data for a day
    canteens = Canteen.objects.order_by('name')
    for canteen in canteens:
        canteen_data[first_day][canteen] = []
        canteen_data[next_day][canteen] = []

    for serving in servings:
        if serving.canteen not in canteen_data[serving.date].keys():
            canteen_data[serving.date][serving.canteen] = []

        canteen_data[serving.date][serving.canteen].append(serving)
    return render(request, 'mensautils/mensa.html', {
        'days': (first_day, next_day),
        'today': today,
        'first_day': first_day,
        'mensa_data': canteen_data,
        'last_updated': Serving.objects.aggregate(
            Max('last_updated'))['last_updated__max'],
    })


@login_required
@require_POST
def save_canteen_user_config(request: HttpRequest) -> HttpResponse:
    """Save the order of canteens for the current user."""
    order = request.POST.get('canteen_order')
    hidden = request.POST.get('hidden_canteens')

    # validate for valid order
    pattern = re.compile(r'(\d+(,\d+)*)*')
    if (not isinstance(order, str) or not isinstance(hidden, str)
       or not pattern.match(order) or not pattern.match(hidden) or
       len(order) > 100 or len(hidden) > 100):
        return HttpResponseNotFound('failure')
    conf, created = CanteenUserConfig.objects.get_or_create(user=request.user)
    conf.order = order
    conf.hidden = hidden
    conf.save()
    return HttpResponse('success')


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
            serving = Serving.objects.create(
                dish=dish, canteen=canteen, date=today, price=price,
                price_staff=price_staff, official=False)
            ServingVerification.objects.create(
                user=request.user, reporter=True, serving=serving)
            messages.success(
                request, 'Das Gericht wurde erfolgreich gespeichert.')
            return redirect(reverse('mensautils.canteen:index'))

    return render(
        request, 'mensautils/submit_serving.html', {
            'canteen': canteen,
            'form': form,
        })


@login_required
def verify_serving(request: HttpRequest, serving_pk: int) -> HttpResponse:
    serving = get_object_or_404(Serving, pk=serving_pk)

    # check that serving is from today
    if serving.date != date.today():
        messages.warning(
            request, 'Der Eintrag ist nicht von heute. Daher kann er nicht bestätigt '
                     'werden.')
        return redirect(reverse('mensautils.canteen:index'))

    # check if user has verified this serving already
    if ServingVerification.objects.filter(
            serving=serving, user=request.user).count() > 0:
        messages.warning(
            request, 'Du hast dieses Gericht bereits bestätigt.')
        return redirect(reverse('mensautils.canteen:index'))

    if request.method == 'POST':
        # save rating
        ServingVerification.objects.create(user=request.user, serving=serving)
        messages.success(
            request, 'Die Gericht wurde erfolgreich bestätigt.')
        return redirect(reverse('mensautils.canteen:index'))

    return render(
        request, 'mensautils/verify_serving.html', {
            'serving': serving,
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


@login_required
def notification(request: HttpRequest) -> HttpResponse:
    notifications = request.user.notifications.order_by('pattern')

    return render(
        request, 'mensautils/notifications.html', {
            'notifications': notifications,
        })


@login_required
def add_notification(request: HttpRequest) -> HttpResponse:
    form = NotificationForm()
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            # save rating
            Notification.objects.create(
                user=request.user, pattern=form.cleaned_data.get('pattern'))
            messages.success(
                request, 'Die Benachrichtigung wurde erfolgreich gespeichert.')
            return redirect(reverse('mensautils.canteen:notification'))

    return render(
        request, 'mensautils/add_notification.html', {
            'form': form,
        }
    )


@login_required
def delete_notification(request: HttpRequest, notification_pk: int) -> HttpResponse:
    notification_elem = get_object_or_404(Notification, user=request.user, pk=notification_pk)

    if request.method == 'POST':
        notification_elem.delete()
        messages.success(
            request, 'Die Benachrichtigung wurde erfolgreich entfernt.')
        return redirect(reverse('mensautils.canteen:notification'))

    return render(
        request, 'mensautils/delete_notification.html', {
            'notification': notification_elem,
        })


def _get_valid_day(base_day: date) -> date:
    """Get the next valid day (i.e. skip sunday)"""
    if base_day.weekday() == 6:
        return base_day + timedelta(days=1)
    return base_day
