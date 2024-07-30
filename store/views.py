from time import timezone
from typing import Any
from urllib import request
from django.db.models.query import QuerySet
from django.forms import modelformset_factory
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from accounts.forms import DeliveryForm
import requests
from accounts.models import Customer, ShippingAddress
from store.models import CartItem, Product, Categorie, ProductFilter, ProductTaille, Cart, Coupons, RelayPoint, Taille
from django.contrib import messages
from store.forms import  RechercheProduitForm, CartItemForm, RelayForm, ProductCategorieForm
from django.views.generic.list import ListView
from django.utils.translation import gettext as _ 
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_GET, require_POST
from django.utils import translation
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_protect
from django.conf import settings

from django.core.paginator import Paginator
import xml.etree.ElementTree as ET
import json
import os
import stripe
stripe.api_key = settings.STRIPE_API_KEY
simtao_api_key = settings.SIMTAO_API_KEY

# Create your views here.

# HomePage
def index(request):
    categories = Categorie.objects.all()
    latest_products = Product.objects.all().order_by('-updated_at')[:6] 
    return render(request, 'store/index.html', context={"categories" : categories , 'latest_products': latest_products})

# # Filtre par categorie
# def products_by_category(request, category_slug):
#     category = get_object_or_404(Categorie, slug=category_slug)
#     products = Product.objects.filter(categorie=category)
#     categories = Categorie.objects.all()  
#     return render(request, 'store/products_by_category.html', context={"products": products, "category": category, "categories": categories})


def category_view(request, category_slug):
    
    # Récupération de la catégorie en fonction du slug
    category = get_object_or_404(Categorie, slug=category_slug)
    
    # Filtrer les produits en fonction de la catégorie et du genre
    products = Product.objects.filter(genre = category_slug)
    
   # Option de pagination des produits
    paginator = Paginator(products, 9) 
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    # Données à rendre sur le template 
    return render(request, 'store/category.html', {
        'products': products, 
        'category_slug': category_slug,
        'category': category
        
    })


    
def products(request):
    filterset = ProductFilter(request.GET, queryset=Product.objects.all())
    products = filterset.qs

    # Filtre par prix
    if 'price' in request.GET:
        price_filter = request.GET.get('price')
        if price_filter == 'lt100':
            products = products.filter(price__lt=100)
        elif price_filter == 'bt100_200':
            products = products.filter(price__range=(100, 200))
        elif price_filter == 'gt200':
            products = products.filter(price__gt=200)

    # Filtre par taille
    if 'size' in request.GET:
        size_filter = request.GET.getlist('size')
        products = products.filter(tailles__taille__in=size_filter)

    categories = Categorie.objects.all()
    category_choices = filterset.qs.values_list('categorie__pk', 'categorie__name').distinct()

    paginator = Paginator(products, 9)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    print('Produits paginés :', products)  #

    # Récupérer toutes les tailles disponibles
    tailles = ProductTaille.objects.values_list('taille__taille', flat=True).distinct()

    return render(request, 'store/products.html', context={
        "products": products,
        "categories": categories,
        "filterset": filterset,
        "category_choices": category_choices,
        "filter": {
            'category': request.GET.get('category'),
            'genre': request.GET.get('genre'),
            'price': request.GET.get('price'),
            'size': request.GET.getlist('size'),
        },
        "tailles": tailles,  # Ajouter les tailles au contexte
    })



# details produits
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product_tailles = ProductTaille.objects.filter(product=product).order_by('taille__taille')

    # Récupérer les IDs des produits consultés depuis la session
    viewed_product_ids = request.session.get('viewedProducts', [])
    
    # Récupérer les instances complètes des produits consultés
    viewed_products = Product.objects.filter(id__in=viewed_product_ids)
    
    # Vérifier si le produit courant n'est pas déjà dans les vus et l'ajouter si nécessaire
    if product.id not in viewed_product_ids:
        viewed_product_ids.append(product.id)
        if len(viewed_product_ids) > 5:
            viewed_product_ids = viewed_product_ids[-5:]  # Garder les 5 derniers vus
    
    # Mettre à jour la session avec les IDs mis à jour
    request.session['viewedProducts'] = viewed_product_ids
    return render(request, 'store/details.html', context={
        "product": product,
        "product_tailles": product_tailles,
        "viewed_products": viewed_products  # Passer les instances complètes des produits consultés
    })
    
@require_GET
def ajax_size_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    available_sizes = ProductTaille.objects.filter(product=product, stock__gt=0).values_list('taille__taille', 'id')
    sizes = [{'id': size[1], 'taille': size[0]} for size in available_sizes]
    data = {
        "sizes": sizes,
        'product_id': product_id,
    }
    return JsonResponse(data, safe=False)

# # Filtre de recherche : -100€
# class ProductUnder100View(ListView):
#     model = Product 
#     template_name = 'store/under_100.html'
    
    
#     def get_queryset(self):
#         return Product.objects.filter(price__lt=100)  

# # Filtre de recherche : entre 100€ et 200€
# class ProductsBetween100And200View(ListView):
#     model = Product
#     template_name = 'store/between_100_and_200.html'

#     def get_queryset(self):
#         return Product.objects.filter(price__gte=100, price__lte=200)
    
    

# # Filtre de recherche : + de 200€
# class ProductsAbove200View(ListView):
#     model = Product
#     template_name = 'store/above_200.html'

#     def get_queryset(self):
#         return Product.objects.filter(price__gt=200)

# Filtre de recherche : Produit en promotion -50%  
class Products50PercentOffView(ListView):
    model = Product
    template_name = 'store/50_percent_off.html'

    def get_queryset(self):
        return Product.objects.filter(promo=True, percent_promo=50)
    
# # Filtre de recherche : Produit par taille
# class ProductsBySizeView(ListView):
#     model = Product
#     template_name = 'store/templates/store/products_by_size.html'
#     context_object_name = 'products'

#     def get_queryset(self):
#         size = self.kwargs.get('size')
#         return Product.objects.filter(sizes__contains=size)
    
def add_to_cart(request, slug): 
    user = request.user

    # Vérifie l'authentification du user 
    if not user.is_authenticated:
        messages.add_message(request, messages.ERROR, "Veuillez vous connecter afin d'ajouter des produits au panier.")
        return redirect('login')

    product = get_object_or_404(Product, slug=slug)
    cart, _ = Cart.objects.get_or_create(user=user)
    # Récupère la taille sélectionnée
    product_taille_id = request.POST.get('product_taille_id')
    product_taille = get_object_or_404(ProductTaille, id=product_taille_id)
    print('mon print est : ',product_taille)
    
    order, created = CartItem.objects.get_or_create(
        user=user,
        ordered=False,
        product=product,
        product_taille=product_taille
    )
    
    if created:
        cart.orders.add(order)
        cart.all_quantity += 1
    else:
        order.quantity += 1
        cart.all_quantity += 1
        
    order.calc_subtotal()
    cart.calc_totaux()
    
    return redirect(reverse("product", kwargs={'slug': slug}))

def recherche_produit(request):
    search_item = request.GET.get('search-item')
    product_request = Product.objects.none()  
    
    if search_item:
        product_request = Product.objects.filter(name__icontains=search_item)
    num_results = product_request.count() if search_item else 0
    
    paginator = Paginator(product_request, 9)
    page = request.GET.get('page')
    product_request = paginator.get_page(page)
    
    context = {
        'resultats': product_request, 
        'num_results': num_results, 
        'search_item': search_item
    }
    return render(request, 'store/recherche.html', context)

def cart(request):
    # commande de l'utilisateur en cours  = request.user
    orders = CartItem.objects.filter(user = request.user, ordered = False)
    cart = get_object_or_404(Cart, user=request.user)
    
                      
    for order in orders:
        order.calc_subtotal() 
        cart.calc_totaux()
    

    
    # Création d'un OrderFormSet qui est unensemble de formulaire 
    # basé sur le model Order
    CartItemFormSet = modelformset_factory(CartItem, form=CartItemForm, extra=0)
    
    #  queryset -> les instances de commandes passée par le user
    formset = CartItemFormSet(queryset=orders )
    
        
    context={"forms": formset, 
             "orders": orders, 
             }
    return render(request, 'store/cart.html', context)


    

def ajax_update_quantities(request ):

    cart = request.user.cart
   
    
    data = json.loads(request.body)
    quantity = data.get("quantity")
    order_id = data.get("item_id")
    response_data = {}
    
    for order in cart.orders.all():
        if str(order.pk) == order_id:
            order.quantity = quantity
            order.calc_subtotal()  
            cart.calc_totaux()  # Mettre à jour le total du panier
            order.save()
            response_data = {
            'success': True,
            'data': {
                'quantity': quantity,
                'order_id': order_id,
                'subtotal': order.subtotal,
                'total': cart.totaux,
            }
        }
            break

    print(response_data)

    return JsonResponse(response_data)



def update_quantities(request):
    print(request.method)
    if request.method == 'POST':
    
    # commande de l'utilisateur en cours  = request.user
        orders = CartItem.objects.filter(user = request.user)
        print('my order is ', orders)
        # Création d'un CartItemFormSet qui est un ensemble de formulaire 
        # basé sur le model CartItem
        CartItemFormSet = modelformset_factory(CartItem, form=CartItemForm, extra = 0)
        
        #  queryset -> les instances de commandes passée par le user
        formset = CartItemFormSet(request.POST, queryset =orders)
        
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data.get('delete'):
                    form.instance.delete()
                else:
                    form.save()
            
        # recalcule du total panier
        if orders.count() != 0:
            request.user.cart.calc_totaux()
            print("Votre panier a été mis à jour.")
            # messages.success(request, 'Votre panier a été mis à jour.')
        else:
            print('Erreur lors de la mise à jour du panier.')
            # messages.error(request, 'Erreur lors de la mise à jour du panier.')
        return redirect('cart')
        
    return redirect('cart')


def delete_order(request, name):
    if cart := request.user.cart:
        cart.delete_order(name)
        cart.calc_totaux()
        
        # if cart.all_quantity == 0:
        #     print('test')
            
    if cart.orders.count() == 0:
        cart.delete()
        return redirect('index')

    return redirect('cart')



    
    
@login_required
def update_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    orders = cart.orders.all()
    
    if request.method == "POST":
        code = request.POST.get('code')
        coupon = Coupons.objects.filter(code=code, is_active=True).first()
        
        if coupon:
            if coupon in cart.coupons.all():
                messages.warning(request, "Ce coupon a déjà été utilisé.")
            else:
                cart.coupons.add(coupon)
                cart.calc_totaux()
                cart.save()
                messages.success(request, "Coupon activé !")
        else:
            messages.warning(request, "Ce coupon n'est pas valide !")

        return redirect('cart')

    context = {
        "cart": cart,
    }
    return render(request, 'store/cart.html', context)



@xframe_options_exempt           
def create_checkout_session(request):
    print("TEST")
    cart = request.user.cart

    line_items = []
    for order in cart.orders.all():
        price = order.product.price_promo if order.product.promo else order.product.price
        line_data = {
            'price_data': {
                'unit_amount': int(price*100),
                'currency': 'eur',
                'product_data': {
                    'name':order.product.name,
                    'description':order.product.short_description or "",

                },
            },
            'quantity': order.quantity
        }
          
        line_items.append(line_data)
    

    checkout_data = {
        "line_items":line_items,
        "mode":"payment",
        "shipping_address_collection": {"allowed_countries" :["FR", "US", "CA"]},
        "payment_intent_data" : {"metadata" : {"infos" : 'le client est dispo de 8h à 12h'}}, 
        "success_url":request.build_absolute_uri(reverse('checkout_success')),
        "cancel_url":request.build_absolute_uri(reverse('cart')),
        "shipping_options": [{"shipping_rate" : 'shr_1PNxe205fBSSfTICnOhgg62e'}],
    }

    if request.user.stripe_id:
        checkout_data["customer"] = request.user.stripe_id
    else:
        checkout_data["customer_email"] = request.user.email
        # "always" : option de creation automatoique du compte stripe 
        checkout_data["customer_creation"] = "always"   
        # checkout_data["invoice_creation"] = {
        #     "enabled" : True,
        #     "invoice_data":{
        #         "description" : "test"
        #     }
        # }     
    try :
        checkout_session = stripe.checkout.Session.create(**checkout_data)
    # Gestion des erreurs
    except Exception as e:
        # erreur 500 : erreur coté serveur 
        return JsonResponse({'error' : str(e)}, status=500)    
        
    # Genere la page de redirection stripe
    return redirect(checkout_session.url, code= 303)

# Ecouteur d'evenements stripes
@csrf_exempt 
def stripe_webhook(request):
    print('mon print')
    # contenu de requete
    payload = request.body
    # en-tete de la requete
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    endpoint_secret = 'whsec_5348b85f2f8ff0b8c0f4be38650955382f2447ae1bb7d0ca8c69ca1a8d8af83c'


    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # convertit l'erreur en str
        print('Error verifying webhook signature :{}'.format(str(e)) )
        # print('Error verifying webhook signature :{0} {1}'.format([str(e), sig_header]) )
        # Gère l'erreur et redirige vers l'erreur 400 
        return HttpResponse(status=400)
    # listes des type d'event sur la doc
    # checkout.session.completed : le paiment a étét effectuer 
    print('entrer dans le webhook')
    if event.type == 'checkout.session.completed':
        print('checkout.session.completed')
        # Récupération de l'objet de data.event
        payment_intent = event.data.object
        try:
            # Récupération des infos du webhook et de la class Shopper ->>> voir terminal CLI
            # R2cupere le bon user
            user = get_object_or_404(Customer, email=payment_intent["customer_details"]["email"])
            print('récupération du user', user)
        except KeyError:
            return HttpResponse("invalid user", status=404)
        
       
        # supprime le panier après le paiment
        complete_order(data=payment_intent, user=user)
        save_shipping_address(data = payment_intent, user=user)

        # print(payment_intent)
        # pprint(payment_intent)
        return HttpResponse(status=200)
    
    elif event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        print('paiement',payment_intent)
    
    return HttpResponse(status=200)

def complete_order(data, user):
    # Mettre à jour l'ID Stripe de l'utilisateur
    user.stripe_id = data['customer'] or ''
    user.cart.delete()
    user.save()
    print('mon user ', user)

    return HttpResponse(status=200)

def save_shipping_address(data, user):
    try:
        address = data["shipping_details"]["address"]
        name = data["shipping_details"]["name"]
        city = address["city"]
        country = address["country"]
        line1 = address["line1"]
        line2 = address["line2"]
        postal_code = address["postal_code"]
    except KeyError:
        return HttpResponse(status=400)
    ShippingAddress.objects.get_or_create(user=user,
                                        name=name,
                                        city =city,
                                        country=country,
                                        address_1 = line1,
                                        address_2 = line2 or "",
                                        zip_code = postal_code)
    return HttpResponse(status=200)

def checkout_success(request):
 return render(request, 'store/index.html')


# Choix de langues
def change_language(request, lang_code):
    response = redirect('index')  
    print('La langue est :',lang_code)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, 
                        lang_code, 
                        max_age=60*60, 
                        httponly=True,
                        samesite='Lax'
                        )
    return response

@login_required
def load_delivery_option(request):
    option = request.GET.get('option')
    if option == 'relay':
        html = render_to_string('store/partial_relay_point.html')
    elif option == 'home':
        html = render_to_string('store/partial_home_delivery.html', {'delivery_form': DeliveryForm()})
    else:
        html = ''

    return JsonResponse({'html': html})

@login_required
def choose_relay(request):
    user = request.user
    addresses = user.addresses.all()
    viewed_products = request.session.get('viewedProducts', [])
    products = Product.objects.filter(id__in=viewed_products) if viewed_products else []

    if request.method == "POST":
        delivery_form = DeliveryForm(request.POST)
        if delivery_form.is_valid():
            shipping_address = delivery_form.save(commit=False)
            shipping_address.user = user
            shipping_address.save()
            return redirect('confirm_paiement')  
    else:
        delivery_form = DeliveryForm()

    return render(request, 'store/choose_relay.html', context={
        "viewed_products": products, 
        "addresses": addresses, 
        "delivery_form": delivery_form
    })
    
@login_required
def confirm_paiement(request):
    # commande de l'utilisateur en cours  = request.user
    orders = CartItem.objects.filter(user = request.user)
     # Création d'un OrderFormSet qui est unensemble de formulaire 
    # basé sur le model Order
    CartItemFormSet = modelformset_factory(CartItem, form=CartItemForm, extra=0)
    
    #  queryset -> les instances de commandes passée par le user
    formset = CartItemFormSet(queryset=orders )
    return render(request, 'store/confirm_paiement.html',  context={"forms" : formset, "orders" : orders,})


@login_required
def choose_address(request):
    if request.method == 'POST':
        address_form = DeliveryForm(request.POST)
        relay_form = RelayForm(request.POST)

        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()
            order = CartItem.objects.create(user=request.user, shipping_address=address)
            return redirect('confirm_payment', order_id=order.id)
        
        elif relay_form.is_valid():
            relay_point = relay_form.save(commit=False)
            relay_point.user = request.user
            relay_point.save()
            order = CartItem.objects.create(user=request.user, shipping_address=None, relay_point=relay_point)
            return redirect('confirm_payment', order_id=order.id)

    else:
        address_form = DeliveryForm()
        relay_form = RelayForm()

    return render(request, 'choose_address.html', {'address_form': address_form, 'relay_form': relay_form})


@csrf_protect
@login_required
def confirm_home_delivery(request):
    user = request.user
    delivery_form = DeliveryForm(request.POST or None, instance=user)

    if request.method == 'POST':
        if delivery_form.is_valid():
            # Traitez ici les données du formulaire si nécessaire
            return redirect('confirm_paiement')  # Redirection vers la page de confirmation de paiement
        else:
            # Form est invalide, vous pouvez afficher des erreurs ou des messages ici si nécessaire
            pass
    
    # Si ce n'est pas une soumission POST ou si le formulaire n'est pas valide, revenez simplement à la même page
    return render(request, 'choose_relay.html', {'delivery_form': delivery_form})


@login_required
def confirm_relay_delivery(request):
    print(request.method)
    if request.method == 'POST':
        nom = request.POST.get("cb_Nom")
        address = request.POST.get("cb_Adresse")
        postcode = request.POST.get("cb_CP")
        city = request.POST.get("cb_Ville")
        country = request.POST.get("cb_Pays")

        RelayPoint.objects.get_or_create(name = nom,
                                         address = address,
                                         postcode =postcode,
                                         city = city,
                                         user = request.user,
                                         country = country
                                         )
        return redirect('confirm_paiement')
       
    else:
       pass

    return render(request, 'store/choose_relay.html', )