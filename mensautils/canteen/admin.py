from django.contrib import admin

from mensautils.canteen.models import Dish, Canteen, Serving, Rating, \
    InofficialDeprecation, ServingVerification

admin.site.register(Dish)
admin.site.register(Canteen)
admin.site.register(InofficialDeprecation)
admin.site.register(Serving)
admin.site.register(ServingVerification)
admin.site.register(Rating)
