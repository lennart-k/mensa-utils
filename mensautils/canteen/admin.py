from django.contrib import admin

from mensautils.canteen.models import Dish, Canteen, Serving

admin.site.register(Dish)
admin.site.register(Canteen)
admin.site.register(Serving)
