from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'important']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'Write a title'}),
            'description': forms.Textarea(attrs={'class':
                                                 'form-control',
                                                 'placeholder':
                                                 'Write a description'}),
            'important': forms.CheckboxInput(attrs={'class':
                                                    'form-check-input m-auto'})
        }


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()
