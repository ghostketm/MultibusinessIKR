"""
Views for the products app
"""
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from .models import Product, Category


class ProductListView(ListView):
    """Display a list of all products."""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(status=Product.Status.ACTIVE)


class ProductDetailView(DetailView):
    """Display a single product."""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'


class CategoryProductListView(ListView):
    """Display a list of products in a category."""
    model = Product
    template_name = 'products/category_product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Product.objects.filter(category=self.category, status=Product.Status.ACTIVE)