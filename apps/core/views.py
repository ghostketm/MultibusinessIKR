"""
Core views for the application
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Count
from apps.products.models import Product
from apps.orders.models import Order
from apps.accounts.models import User


class HomeView(TemplateView):
    """Home page view with statistics"""
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add site name to context
        from django.conf import settings
        context['SITE_NAME'] = getattr(settings, 'META_SITE_NAME', 'IKr Platform')

        # Get platform statistics
        context['stats'] = {
            'products_count': Product.objects.filter(status='active').count(),
            'orders_count': Order.objects.count(),
            'customers_count': User.objects.filter(is_staff=False).count(),
        }

        # Get featured products
        context['featured_products'] = Product.objects.filter(
            status='active', featured=True
        )[:6]

        return context


def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    """Custom 500 error handler"""
    return render(request, 'errors/500.html', status=500)