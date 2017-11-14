from django import forms
from .models import Current_emscall

# Create your forms here
class CurrentCallForm(forms.ModelForm):

    class Meta:
        model = Current_emscall
        fields = ("addr",)