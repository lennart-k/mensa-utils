from django import forms


class RateForm(forms.Form):
    rating = forms.ChoiceField(choices=[(a, a) for a in  range(1, 6)])
