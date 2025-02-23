from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", views.home, name="home"),  # Homepage
    path("login/", views.login_view, name="login"),  # Login
    path("create-account/", views.register_view, name="register"),  # Register
    path("dashboard/", views.dashboard, name="dashboard"),  # Dashboard
    path(
        "grocery-search/", views.grocery_search, name="grocery_search"
    ),  # Grocery Search
    path("logout/", LogoutView.as_view(template_name="main/home.html"), name="logout"),
    path("search/<str:keyword>/", views.search_items, name="search_items"),
    path("top-deals/", views.top_deals, name="top_deals"),

]
