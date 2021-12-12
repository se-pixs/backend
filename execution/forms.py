from django import forms


class ChangeFormatForm(forms.Form):
    parameters = forms.FileField()

class ConvertToLowPolyForm(forms.Form):
    parameters = forms.FileField()

class IGPanoSplitForm(forms.Form):
    parameters = forms.FileField()
