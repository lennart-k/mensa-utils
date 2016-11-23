from datetime import date, timedelta

from django.db.models import Max
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from mensautils.canteen.models import Canteen, Serving
from mensautils.canteen.statistics import get_most_frequent_dishes


def index(request: HttpRequest) -> HttpResponse:
    today = date.today()
    days = [today, today + timedelta(days=1)]
    canteens = Canteen.objects.order_by('name')
    canteen_data = {}
    for day in days:
        canteen_data[day] = {}
        for canteen in canteens:
            canteen_data[day][canteen.name] = canteen.servings.filter(
                date=day)
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
