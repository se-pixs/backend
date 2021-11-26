from django import forms


class ChangeFormatForm(forms.Form):
    parameters = forms.FileField()
