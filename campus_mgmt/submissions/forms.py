from django import forms
from .models import Submission

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Optional text submission...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'class': 'form-control', 'accept': '.pdf,.doc,.docx,.txt'})
        self.fields['content'].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        content = cleaned_data.get('content')
        
        if not file and not content:
            raise forms.ValidationError("Please provide either a file or text content.")
        
        return cleaned_data