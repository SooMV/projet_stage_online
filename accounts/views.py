from django.forms import model_to_dict
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model, login, logout , authenticate
from django.contrib.auth.decorators import login_required

from django.contrib import messages

from django.contrib.auth import update_session_auth_hash
from accounts.forms import UserRegistrationForm, UserLoginForm, DeliveryForm, PasswordResetForm
from accounts.models import Customer, ShippingAddress
from store.models import CartItem
from mail.views import send_welcome_email
import logging

logger = logging.getLogger(__name__)
User = get_user_model()




def signup(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            if not form.cleaned_data['accept_terms']:
                messages.add_message(request, messages.ERROR, "Vous devez accepter les conditions d'utilisation et la politique de confidentialité pour créer un compte.")
                return render(request, 'accounts/signup.html', {'form': form})
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            captcha_response = form.cleaned_data.get('captcha')

            if User.objects.filter(email=email).exists():
                messages.add_message(request, messages.ERROR, "Ce compte existe déjà.")
            elif captcha_response:
                user = User.objects.create_user(email=email, password=password)
                print(user.email)
                login(request, user)
                # envoi d'un mail à la création du compte
                send_welcome_email(user.email)
                logger.info(f"New user {user.email} signed up and logged in.")
                return redirect('index')
            else:
                messages.add_message(request, messages.ERROR, "Le test reCAPTCHA a échoué. Veuillez réessayer.")
        else:
            messages.add_message(request, messages.ERROR, "Les informations fournies sont invalides.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/signup.html', {'form': form})



def login_user(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, "Le compte n'existe pas ou les informations de connexion sont incorrectes")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})
     

def logout_user(request):
    logout(request)
    return redirect('index')


@login_required
def profile_view(request):
    user = Customer.objects.all()
    context = {
        "user": user,
    }
    return render(request, 'templates/user_admin.html', context)

@login_required(login_url="../login/")
def index(request):
   
    return render(request, 'accounts/index.html')


@login_required
def my_orders(request):
    user = request.user
    orders = CartItem.objects.filter(user = user, ordered = True)
    print(orders)
    return render(request,'accounts/my_order.html', context={ "orders" : orders})


@login_required(login_url="../login/")
def set_password(request):
    user = request.user

    if request.method == 'POST':
        password_form = PasswordResetForm(user, request.POST)

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Votre mot de passe a été réinitialisé avec succès.")
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire de réinitialisation du mot de passe.")
    else:
        password_form = PasswordResetForm(user)

    context = {
        'password_form': password_form
    }
    return render(request, 'accounts/reset_password.html', context)

@login_required(login_url="../login/")
def set_address(request, user_id):
    user = get_object_or_404(Customer, id=user_id)
    addresses = user.addresses.all()  # Récupère toutes les adresses de l'utilisateur
    
    if request.method == 'POST':
        if 'address_id' in request.POST:  # Vérifie si un ID d'adresse est soumis (modification)
            address_id = request.POST['address_id']
            address = get_object_or_404(ShippingAddress, id=address_id)
            form = DeliveryForm(request.POST, instance=address)
        else:  # Sinon, crée une nouvelle adresse (ajout)
            form = DeliveryForm(request.POST)
        
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = user
            new_address.save()

            messages.success(request, "Votre adresse de livraison a été enregistrée avec succès.")
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire de livraison.")
    else:
        form = DeliveryForm()

    context = {
        'delivery_form': form,
        'addresses': addresses,
        'user_id': user_id
    }
    return render(request, 'accounts/set_address.html', context)

class AddressListView(ListView):
    template_name = 'accounts/address_list.html'
    context_object_name = 'addresses'
    
    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

class AddressUpdateView(UpdateView):
    model = ShippingAddress
    form_class = DeliveryForm
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('address-list')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(ShippingAddress, pk=pk)

class AddressDeleteView(DeleteView):
    model = ShippingAddress
    template_name = 'accounts/address_confirm_delete.html'
    success_url = reverse_lazy('address-list')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(ShippingAddress, pk=pk)
    
class DeliveryFormView(View):
    form_class = DeliveryForm
    template_name = 'accounts/set_address.html'

    def get(self, request):
        form = self.form_class(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts/index.html')  # Rediriger vers la page d'accueil ou une autre page
        return render(request, self.template_name, {'form': form})
    
@login_required
def delete_account(request):
    if request.method == 'POST':
        # Vérifiez que l'utilisateur a confirmé la suppression de son compte
        if 'confirm_delete' in request.POST:
            # Supprimez l'utilisateur de la base de données
            request.user.delete()
            # Redirigez l'utilisateur vers la page d'accueil
            return redirect('index')
    else:
        # Affichez une page de confirmation de suppression de compte
        return render(request, 'accounts/delete_account.html')
    
def politique_confidentilite(request):
    return render(request,'accounts/politique_confidentilite.html')
    
def mentions_legales(request):
    return render(request,'accounts/mentions_legales.html')
