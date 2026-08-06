from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView

from .models import Payment, Invoice
from .forms import PaymentForm, InvoiceForm


@login_required
def payment_list(request):
    if request.user.role == 'student':
        payments = Payment.objects.filter(student=request.user)
    elif request.user.role in ['admin', 'teacher']:
        payments = Payment.objects.all()
    else:
        payments = Payment.objects.none()
    
    return render(request, 'payments/payment_list.html', {
        'payments': payments
    })


@login_required
def payment_detail(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    
    if request.user.role == 'student' and payment.student != request.user:
        messages.error(request, 'Access denied.')
        return redirect('payments:payment_list')
    
    return render(request, 'payments/payment_detail.html', {
        'payment': payment
    })


@login_required
def create_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.student = request.user
            payment.save()
            messages.success(request, 'Payment created successfully.')
            return redirect('payments:payment_detail', pk=payment.pk)
    else:
        form = PaymentForm()
    
    return render(request, 'payments/payment_form.html', {
        'form': form
    })


@login_required
def invoice_list(request):
    if request.user.role == 'student':
        invoices = Invoice.objects.filter(billed_to=request.user)
    elif request.user.role in ['admin', 'teacher']:
        invoices = Invoice.objects.all()
    else:
        invoices = Invoice.objects.none()
    
    return render(request, 'payments/invoice_list.html', {
        'invoices': invoices
    })


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.user.role == 'student' and invoice.billed_to != request.user:
        messages.error(request, 'Access denied.')
        return redirect('payments:invoice_list')
    
    return render(request, 'payments/invoice_detail.html', {
        'invoice': invoice
    })
