from ast import arg
from django import forms

from accounts.models import Customer, ShippingAddress
from store.models import CartItem, Product, RelayPoint


class CartItemForm(forms.ModelForm):
    # Case à cocher pour supprimer un ou plusieurs produits
    delete = forms.BooleanField(initial=False, required=False, label="Supprimer")
    quantity = forms.IntegerField(label="Quantité")  # Ajout du champ quantité

    class Meta:
        model = CartItem
        fields = ["quantity", "delete", 'product_taille']

    def save(self, *args, **kwargs):
        if self.cleaned_data["delete"]:
            self.instance.delete()
            # Si tous les articles sont supprimés après la suppression
            if self.instance.user.cart.orders.count() == 0:
                self.instance.user.cart.delete()
            else:
                self.instance.quantity = self.cleaned_data.get('quantity')
                self.instance.save()
                self.instance.user.cart.calc_totaux()
            return True
        
        #  class -> super() appelle automatiquement lélément parent 
        return super().save(*arg, **kwargs)

class RelayForm(forms.ModelForm):
    class Meta:
        model = RelayPoint
        fields = ['name', 'address', 'postcode', 'city', 'country', ]
        
class SearchForm(forms.Form):
    search_item = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search for the product you want...',
            'class': 'block p-2.5 w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm sm:text-base rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
        })
    )
        
class ProductCategorieForm(forms.Form):
    category = forms.CharField()