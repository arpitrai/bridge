from django import forms

CHOICES = (
(0, 'a'),
(1, 'b'),
(2, 'c'),
)

class MyForm(forms.Form):
    letters = forms.MultipleChoiceField(
            choices=CHOICES, 
            label="x", 
            required=True) 
