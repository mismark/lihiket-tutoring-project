from django import forms
from .models import Payment, Invoice
from apps.courses.models import Course


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['course', 'amount', 'payment_method']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(status='published')


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['payment', 'billed_to', 'amount', 'due_date']
        widgets = {
            'payment': forms.Select(attrs={'class': 'form-control'}),
            'billed_to': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }