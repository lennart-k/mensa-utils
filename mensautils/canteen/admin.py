from django.contrib import admin

from mensautils.canteen.models import Dish, Canteen, Serving, Rating

admin.site.register(Dish)
admin.site.register(Canteen)
admin.site.register(Serving)
admin.site.register(Rating)
