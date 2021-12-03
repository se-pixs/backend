from django import forms


class ChangeFormatForm(forms.Form):
    parameters = forms.FileField()

class ConvertToLowPoly(forms.Form):
    parameters = forms.FileField()
