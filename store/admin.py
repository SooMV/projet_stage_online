from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.contrib.redirects.models import Redirect

from django.contrib import admin
from django.db.models import Sum
from .models import Product, Categorie, Taille, ProductTaille, CartItem, Cart, Coupons

admin.site.unregister(Group)
admin.site.unregister(Site)
admin.site.unregister(Redirect) 

class ProductTailleInline(admin.TabularInline):
    model = ProductTaille
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductTailleInline]
    list_display = (
        'name', 'slug', 'price', 'get_stock', 'long_description',
        'short_description', 'thumbnails1', 'thumbnails2',
        'thumbnails3', 'thumbnails4', 'promo', 'percent_promo',
        'product_stripe_id', 'updated_at', 
    )

    def get_stock(self, obj):
        return ProductTaille.objects.filter(product=obj).aggregate(total_stock=Sum('stock'))['total_stock']
    get_stock.short_description = 'Stock'


@admin.register(Taille)

@admin.register(ProductTaille)
class ProductTailleAdmin(admin.ModelAdmin):
    list_display = ('product', 'taille', 'stock')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'ordered', 'ordered_date', 'subtotal')

@admin.register(Coupons)
class CouponsAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'is_active', 'created_at', 'expires_at')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('ordered', 'ordered_date', 'totaux', 'all_quantity', 'get_coupons')

    def get_coupons(self, obj):
        return ", ".join([coupon.code for coupon in obj.coupons.all()])
    get_coupons.short_description = 'Coupons'

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

