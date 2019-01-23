from rest_framework import serializers

from mensautils.canteen.models import Canteen, Dish, Serving


class CanteenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Canteen
        fields = ('id', 'name')


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ('name', 'vegetarian', 'vegan')


class ServingSerializer(serializers.ModelSerializer):
    dish = DishSerializer(read_only=True)

    class Meta:
        model = Serving
        fields = ('date', 'dish', 'price', 'price_staff', 'canteen')
