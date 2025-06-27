from .models import UploadedFile, Message, Department
# base/forms.py
from django import forms
from django.contrib.auth import authenticate

class CustomLoginForm(forms.Form):
    code = forms.CharField(label="Code")
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        code = self.cleaned_data.get('code')
        password = self.cleaned_data.get('password')

        if code and password:
            self.user = authenticate(self.request, username=code, password=password)
            if self.user is None:
                raise forms.ValidationError("Invalid code or password")
        return self.cleaned_data

    def get_user(self):
        return self.user



class MessageForm(forms.ModelForm):
    to_department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select Department",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Message
        fields = ['to_department', 'content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Type your message...'
            }),
        }
        labels = {
            'content': '',
        }

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']
