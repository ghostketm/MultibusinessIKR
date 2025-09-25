from apps.products.models import Product

"""
Order views for payment processing
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from apps.orders.models import Order, Payment
from apps.orders.payment_processors import get_payment_processor
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView


def initiate_mpesa_payment(request, order_id):
    """Initiate M-Pesa payment for an order"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if not phone_number:
            messages.error(request, 'Phone number is required')
            return redirect('orders:payment', order_id=order_id)

        try:
            processor = get_payment_processor('mpesa')
            response = processor.initiate_payment(order, phone_number)

            # Save payment record
            payment = Payment.objects.create(
                order=order,
                amount=order.total_amount,
                method='mpesa',
                status='pending',
                mpesa_phone=phone_number,
                mpesa_checkout_request_id=response.get('CheckoutRequestID'),
                gateway_response=response
            )

            messages.success(request, 'Payment initiated. Please check your phone for the M-Pesa prompt.')
            return redirect('orders:payment_status', order_id=order_id)

        except Exception as e:
            messages.error(request, f'Payment initiation failed: {str(e)}')
            return redirect('orders:payment', order_id=order_id)

    return render(request, 'orders/payment.html', {'order': order})


def payment_status(request, order_id):
    """Check payment status"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    payment = order.payments.last()

    if payment and payment.method == 'mpesa':
        try:
            processor = get_payment_processor('mpesa')
            response = processor.confirm_payment(payment.mpesa_checkout_request_id)

            # Update payment status based on response
            if response.get('ResponseCode') == '0':
                payment.status = 'success'
                order.payment_status = 'paid'
                order.save()
                payment.save()
                messages.success(request, 'Payment successful!')
            else:
                payment.status = 'failed'
                payment.save()
                messages.error(request, 'Payment failed. Please try again.')

        except Exception as e:
            messages.error(request, f'Error checking payment status: {str(e)}')

    return render(request, 'orders/payment_status.html', {'order': order, 'payment': payment})


@csrf_exempt
@require_POST
def mpesa_callback(request):
    """Handle M-Pesa callback"""
    try:
        data = json.loads(request.body)
        # Process callback data
        checkout_request_id = data.get('CheckoutRequestID')
        result_code = data.get('ResultCode')

        payment = Payment.objects.get(mpesa_checkout_request_id=checkout_request_id)
        order = payment.order

        if result_code == 0:
            payment.status = 'success'
            order.payment_status = 'paid'
            payment.mpesa_response_code = str(result_code)
            payment.gateway_response = data
        else:
            payment.status = 'failed'
            payment.mpesa_response_code = str(result_code)
            payment.gateway_response = data

        payment.save()
        order.save()

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})
    cart_item = cart.get(str(product_id), {'quantity': 0})
    cart_item['quantity'] += quantity
    cart_item['price'] = str(product.price) # Store price as string to avoid serialization issues
    cart_item['name'] = product.name
    cart_item['image'] = product.featured_image.url if product.featured_image else (product.images.first().image.url if product.images.first() else None)

    cart[str(product_id)] = cart_item
    request.session['cart'] = cart
    request.session.modified = True

    messages.success(request, f'{quantity} x {product.name} added to cart.')
    return redirect(request.META.get('HTTP_REFERER', reverse('products:detail', kwargs={'slug': product.slug})))


class OrderListView(LoginRequiredMixin, ListView):
    """Display a list of orders for the current user."""
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')