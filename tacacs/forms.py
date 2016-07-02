from django import forms


class Apply_Config(forms.Form):
    job = forms.CharField(label='Your name', max_length=100)