
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.indexView.as_view(), name="index"),
    path("Reservation_form/", views.ReservationFormView.as_view(), name="Reservation_form"),

    # cashier
    path("Cashier/", views.CashierView.as_view(), name="cashier_table"),
    path("Cashier/pay", views.CashierPayView.as_view(), name="cashier_pay"),
    path("Cashier-list/", views.CashierListView.as_view(), name="cashier_list"),
    path("Cashier/confirm/<int:reservation_id>", views.CashierConfirmView.as_view(), name="cashier_confirm"),
    path("Cashier/cancel/<int:reservation_id>", views.CashierCancelView.as_view(), name="cashier_cancel"),
    path("Cashier/serve/<int:table_id>", views.CashierServeView.as_view(), name="cashier_serve"),

    # profile
    path("Profile/", views.ProfileView.as_view(), name="profile"),
    path("Profile_edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("Password_change/", views.PasswordChangeView.as_view(), name="change_password"),

    # login & register
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),


    # boardgame
    path("boardgame/", views.BoardgameView.as_view(), name="boardgame"),
    path("boardgame/<str:cate_name>", views.BoardgameView.as_view(), name="boardgame-filter"),
    path("boardgame/<int:game_id>/detail", views.BoardgameDetailView.as_view(), name="boardgame-detail"),

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

    path("dashboard/categories", views.DashboardCategoriesView.as_view(), name="des-categories"),
    path("dashboard/categories/add", views.DashboardCategoriesView.as_view(), name="des-categories-add"),
    path("dashboard/categories/delete/<int:cate_id>/", views.DashboardCategoriesDelView.as_view(), name="des-categories-del"),
    path("dashboard/categories/edit/<int:cate_id>/", views.DashboardCategoriesEditView.as_view(), name="des-categories-edit"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
