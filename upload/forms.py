from django import forms


class UploadFileForm(forms.Form):
    format = forms.CharField(max_length=4)
    image = forms.FileField()
