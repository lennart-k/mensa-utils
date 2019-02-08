from rest_framework import serializers

from mensautils.canteen.models import Canteen, Serving


class CanteenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Canteen
        fields = ('id', 'name')


class ServingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serving
        fields = ('date', 'dish', 'vegetarian', 'vegan', 'price', 'price_staff', 'canteen')

    dish = serializers.CharField(source='dish.name')
    vegetarian = serializers.BooleanField(source='dish.vegetarian')
    vegan = serializers.BooleanField(source='dish.vegan')
