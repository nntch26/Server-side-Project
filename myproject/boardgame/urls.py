
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.indexView.as_view(), name="index"),
    path("Reservation_form/", views.ReservationFormView.as_view(), name="Reservation_form"),
    path("Cashier/", views.CashierView.as_view(), name="cashier"),

    # path("product/", views.ProductView.as_view(), name="product"),
    # path("product/<int:cat_id>/", views.ProductView.as_view(), name="product_filter"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
