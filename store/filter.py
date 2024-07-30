import django_filters
from django import forms
from store.models import Categorie, Product, ProductTaille, Taille


class PriceFilter(django_filters.Filter):
    def filter(self, qs, value):
        print(f"Filtering with value: {value}")  
        if value in (None, ''):
            return qs
        elif value == 'lt100':
            return qs.filter(price__lt=100)
        elif value == 'bt100_200':
            return qs.filter(price__range=(100, 200))
        elif value == 'gt200':
            return qs.filter(price__gt=200)
        return qs


class ProductFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(queryset=Categorie.objects.all(), empty_label="All", field_name='categorie')
    genre = django_filters.ChoiceFilter(choices=[('homme', "HOMME"), ('femme', "FEMME")], empty_label="All")
    size = django_filters.ModelMultipleChoiceFilter(queryset=Taille.objects.all(), field_name='tailles__taille', label='Size', widget=forms.CheckboxSelectMultiple())
    
    price = PriceFilter(field_name='price', label='Price range')

    class Meta:
        model = Product
        fields = ['category', 'genre', 'price', 'size']