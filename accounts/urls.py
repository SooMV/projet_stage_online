from django.urls import path
from accounts import views
from accounts.views import AddressDeleteView, AddressListView, AddressUpdateView, delete_account, login_user, mentions_legales, my_orders, politique_confidentilite, set_password, signup, logout_user, index, set_address


urlpatterns = [
    path("profile/addresses/", AddressListView.as_view(), name='address-list'),
    path("profile/address/<int:pk>/update/", AddressUpdateView.as_view(), name='address-update'),
    path("profile/address/<int:pk>/delete/", AddressDeleteView.as_view(), name='address-delete'),
    path("profile/set_address/<int:user_id>", set_address, name='set_address'),
    path('profile/<int:user_id>/set_address/', views.set_address, name='set_address'),
    path("profile/set_password", set_password, name="set_password"),
    path("profile/politique_confidentilite", politique_confidentilite, name="politique_confidentilite"),
    path("profile/mentions_legales", mentions_legales, name="mentions_legales"),
    path("profile/delete_account", delete_account, name="delete_account"),
    path("orders/", my_orders, name="my_orders"),
    path("profile/", index, name="profile"),
    path("signup/", signup, name="signup"),
    path('login/', login_user, name="login"),
    path("logout/", logout_user, name="logout"),
]




