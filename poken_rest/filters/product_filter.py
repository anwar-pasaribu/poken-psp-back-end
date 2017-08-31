import django_filters
from rest_framework import generics
from django_filters import rest_framework as filters
from poken_rest.models import Product


class ProductFilter(filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    category_name = django_filters.CharFilter(lookup_expr='icontains', name='category__name')

    class Meta:
        model = Product
        fields = ['name', 'description', 'category_name']