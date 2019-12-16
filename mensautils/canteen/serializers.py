from rest_framework import serializers

from mensautils.canteen.models import Canteen, Serving, OpeningTime


class OpeningTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningTime
        fields = ('weekday', 'start', 'end')


class CanteenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Canteen
        fields = ('id', 'name', 'opening_times')

    opening_times = OpeningTimeSerializer(many=True)


class ServingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serving
        fields = ('date', 'dish', 'vegetarian', 'vegan', 'price', 'price_staff', 'canteen')

    dish = serializers.CharField(source='dish.name')
    vegetarian = serializers.BooleanField(source='dish.vegetarian')
    vegan = serializers.BooleanField(source='dish.vegan')
