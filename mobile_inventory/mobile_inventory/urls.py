from django.contrib import admin
from django.urls import path
from inventory import views
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # stock
    path('products/stock/', views.product_stock, name="product_stock"),
    path('raw/stock/', views.raw_stock, name="raw_stock"),

    # sales & expenses
    path('sales/', views.sales_list, name="sales_list"),
    path('expenses/', views.expenses_list, name="expenses_list"),
]

