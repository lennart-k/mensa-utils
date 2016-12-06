from django.contrib import admin

from mensautils.canteen.models import Dish, Canteen, Serving, Rating, \
    InofficialDeprecation, ServingVerification, Notification, CanteenUserConfig

admin.site.register(Dish)
admin.site.register(Canteen)
admin.site.register(CanteenUserConfig)
admin.site.register(InofficialDeprecation)
admin.site.register(Notification)
admin.site.register(Serving)
admin.site.register(ServingVerification)
admin.site.register(Rating)
