from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.conf import settings
from store.views import index, stripe_webhook

urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    path("", index, name='index'),

    path('stripe-webhook/', stripe_webhook, name="stripe-webhook"),
    path('store/', include('store.urls')),

    path('accounts/', include('accounts.urls')),
    path('map/', include('map.urls')),
    path('mail/', include('mail.urls')),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
