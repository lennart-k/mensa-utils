from collections import defaultdict
from datetime import date, timedelta

from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render

from mensautils.base.models import Canteen


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
        'mensa_data': canteen_data,
        # TODO: last refresh
    })
