from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember = request.POST.get("remember")  # kukunin natin yung checkbox

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if remember:
                # Session lasts 2 weeks (1209600 sec)
                request.session.set_expiry(1209600)
            else:
                # Session ends when browser closes
                request.session.set_expiry(0)

            return redirect("dashboard")
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})
    
    return render(request, "login.html")



def logout_view(request):
    logout(request)
    return redirect("login")


from .models import ProductInventory, RawMaterialInventory, Sales, Expenses, HistoryLog

@login_required(login_url="login")
def dashboard(request):
    context = {
        "product_count": ProductInventory.objects.count(),
        "raw_count": RawMaterialInventory.objects.count(),
        "sales_count": Sales.objects.count(),
        "expense_count": Expenses.objects.count(),
        "log_count": HistoryLog.objects.count(),
    }
    return render(request, "dashboard.html", context)

@login_required(login_url="login")
def product_stock(request):
    products = ProductInventory.objects.select_related("product").all()
    return render(request, "product_stock.html", {"products": products})


@login_required(login_url="login")
def raw_stock(request):
    raws = RawMaterialInventory.objects.select_related("material").all()
    return render(request, "raw_stock.html", {"raws": raws})


@login_required(login_url="login")
def history_log_view(request):
    logs_qs = HistoryLog.objects.select_related("admin", "log_type").order_by("-log_date")
    paginator = Paginator(logs_qs, 20)
    page_number = request.GET.get("page")
    logs_page = paginator.get_page(page_number)
    return render(request, "history_log.html", {"logs": logs_page})


@login_required(login_url="login")
def sales_list(request):
    sales_qs = Sales.objects.all().order_by('-date')
    paginator = Paginator(sales_qs, 20)
    page_number = request.GET.get("page")
    sales_page = paginator.get_page(page_number)
    return render(request, "sales_list.html", {"sales": sales_page})


@login_required(login_url="login")
def expenses_list(request):
    expenses_qs = Expenses.objects.all().order_by('-date')
    paginator = Paginator(expenses_qs, 20)
    page_number = request.GET.get("page")
    expenses_page = paginator.get_page(page_number)
    return render(request, "expenses_list.html", {"expenses": expenses_page})
