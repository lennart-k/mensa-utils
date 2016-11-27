from django import forms


class RateForm(forms.Form):
    rating = forms.ChoiceField(choices=[(a, a) for a in  range(1, 6)])


class SubmitServingForm(forms.Form):
    name = forms.CharField(max_length=300)
    vegetarian = forms.BooleanField(required=False)
    price = forms.DecimalField(max_digits=4, decimal_places=2)
    price_staff = forms.DecimalField(max_digits=4, decimal_places=2)


class NotificationForm(forms.Form):
    pattern = forms.CharField(max_length=300)
