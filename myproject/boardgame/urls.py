
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.indexView.as_view(), name="index"),
    path("Reservation_form/", views.ReservationFormView.as_view(), name="Reservation_form"),
    path("Cashier/", views.CashierView.as_view(), name="cashier"),
    path("Profile/", views.ProfileView.as_view(), name="profile"),

    # login & register
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),



    # boardgame
    path("boardgame/", views.BoardgameView.as_view(), name="boardgame"),
    path("boardgame/<str:cate_name>", views.BoardgameView.as_view(), name="boardgame-filter"),

    # search
    path("boardgame/seach/", views.BoardgameSearchView.as_view(), name="seach"),
    path("boardgame/filter/", views.BoardgameFilterView.as_view(), name="filter"),


    # dashboard
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard/boardgame", views.DashboardBoardgameView.as_view(), name="des-boardgame"),
    path("dashboard/boardgame/add", views.DashboardBoardgameAddView.as_view(), name="des-boardgame-add"),
    path("dashboard/boardgame/delete/<int:game_id>/", views.DashboardBoardgameDelView.as_view(), name="des-boardgame-del"),
    path("dashboard/boardgame/edit/<int:game_id>/", views.DashboardBoardgameEditView.as_view(), name="des-boardgame-edit"),

    path("dashboard/member", views.DashboardMemberView.as_view(), name="des-member"),
    path("dashboard/member/delete/<int:mem_id>/", views.DashboardMemberDelView.as_view(), name="des-member-del"),


    # path("product/", views.ProductView.as_view(), name="product"),
    # path("product/<int:cat_id>/", views.ProductView.as_view(), name="product_filter"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
