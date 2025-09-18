from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def dashboard(request):
    return render(request, "dashboard.html")


from django.shortcuts import render
from .models import ProductInventory, RawMaterialInventory, Sales, Expenses

def dashboard(request):
    context = {
        "product_count": ProductInventory.objects.count(),
        "raw_count": RawMaterialInventory.objects.count(),
        "sales_count": Sales.objects.count(),
        "expense_count": Expenses.objects.count(),
        "log_count": HistoryLog.objects.count(),
    }
    return render(request, "dashboard.html", context)

from django.shortcuts import render
from .models import ProductInventory

def product_stock(request):
    products = ProductInventory.objects.select_related("product").all()
    return render(request, "product_stock.html", {"products": products})


from .models import RawMaterialInventory

def raw_stock(request):
    raws = RawMaterialInventory.objects.select_related("material").all()
    return render(request, "raw_stock.html", {"raws": raws})

from .models import Sales

from django.shortcuts import render
from .models import HistoryLog

def history_log_view(request):
    logs = HistoryLog.objects.select_related("admin", "log_type").order_by("-log_date")
    return render(request, "history_log.html", {"logs": logs})


def sales_list(request):
    sales = Sales.objects.all().order_by('-date')  # pinakabago sa taas
    return render(request, "sales_list.html", {"sales": sales})

from .models import Expenses

def expenses_list(request):
    expenses = Expenses.objects.all().order_by('-date')
    return render(request, "expenses_list.html", {"expenses": expenses})
