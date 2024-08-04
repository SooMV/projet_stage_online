from django.urls import path
from .views import (
    Products50PercentOffView, recherche_produit, cart, products,
    category_view, stripe_webhook, create_checkout_session, checkout_success,
    product_detail, add_to_cart, load_delivery_option, confirm_paiement,
    confirm_home_delivery, confirm_relay_delivery, ajax_update_quantities,
    ajax_size_detail, update_quantities, update_cart, delete_order, choose_relay
)

urlpatterns = [
    
    path('search_product/', recherche_produit, name='search_product'),
    path("cart/", cart, name="cart"),
    path("products/", products, name="products"),
   

    path('categorie/<slug:parent_slug>/<slug:category_slug>/', category_view, name='subcategory'),
    path('categorie/<slug:category_slug>/', category_view, name='category'),
    
    path('cart/create-checkout-session', create_checkout_session, name='create-checkout-session'),
    path("cart/success", checkout_success, name="checkout_success"),

    path("product/<str:slug>/", product_detail, name="product"),
    path("product/<str:slug>/add-to-cart", add_to_cart, name="add-to-cart"),

    path('load_delivery_option/', load_delivery_option, name='load_delivery_option'),
    path('confirm_paiement/', confirm_paiement, name='confirm_paiement'),
    path('confirm_home_delivery/', confirm_home_delivery, name='confirm_home_delivery'),
    path('confirm_relay_delivery/', confirm_relay_delivery, name='confirm_relay_delivery'),

    path('50-percent-off/', Products50PercentOffView.as_view(), name='products_50_percent_off'),
    path("cart/ajax_update_quantities", ajax_update_quantities, name="ajax_update_quantities"),
    path('available-sizes/<int:product_id>/', ajax_size_detail, name='available-sizes'),
    path("cart/update-quantities", update_quantities, name="update-quantities"),
    path('cart/update-cart/', update_cart, name='update_cart'),

    path("cart/<str:name>", delete_order, name="delete_order"),
    path('choose-relay/', choose_relay, name='choose_relay'),
]