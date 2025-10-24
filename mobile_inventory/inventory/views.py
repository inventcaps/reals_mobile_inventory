from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.http import JsonResponse
import psycopg2
from decimal import Decimal

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


@login_required(login_url="login")
def monthly_report(request):
    """Render monthly business report page"""
    return render(request, "monthly_report.html")


@login_required(login_url="login")
def monthly_report_data(request):
    """Fetch monthly business report data from Supabase"""
    try:
        # Connect to Supabase PostgreSQL
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='Reals_db_123',
            host='db.rczsumkmhoxjaycvggzt.supabase.co',
            port='5432',
            sslmode='require'
        )
        cursor = conn.cursor()
        
        # Query for monthly revenue and expenses
        monthly_query = """
            WITH monthly_sales AS (
                SELECT 
                    TO_CHAR(date, 'Month YYYY') as month,
                    DATE_TRUNC('month', date) as month_date,
                    COALESCE(SUM(amount), 0) as revenue
                FROM sales
                GROUP BY DATE_TRUNC('month', date), TO_CHAR(date, 'Month YYYY')
            ),
            monthly_expenses AS (
                SELECT 
                    DATE_TRUNC('month', date) as month_date,
                    COALESCE(SUM(amount), 0) as expenses
                FROM expenses
                GROUP BY DATE_TRUNC('month', date)
            )
            SELECT 
                ms.month,
                ms.revenue,
                COALESCE(me.expenses, 0) as expenses,
                (ms.revenue - COALESCE(me.expenses, 0)) as profit,
                LAG(ms.revenue) OVER (ORDER BY ms.month_date) as prev_revenue,
                LAG(ms.revenue - COALESCE(me.expenses, 0)) OVER (ORDER BY ms.month_date) as prev_profit
            FROM monthly_sales ms
            LEFT JOIN monthly_expenses me ON ms.month_date = me.month_date
            ORDER BY ms.month_date DESC
            LIMIT 12
        """
        cursor.execute(monthly_query)
        monthly_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Process data
        result = []
        total_revenue = 0
        total_profit = 0
        
        for row in monthly_data:
            month, revenue, expenses, profit, prev_revenue, prev_profit = row
            revenue = float(revenue)
            expenses = float(expenses)
            profit = float(profit)
            
            total_revenue += revenue
            total_profit += profit
            
            # Calculate changes
            revenue_change = None
            profit_change = None
            if prev_revenue is not None:
                revenue_change = revenue - float(prev_revenue)
            if prev_profit is not None:
                profit_change = profit - float(prev_profit)
            
            result.append({
                'month': month.strip(),
                'revenue': revenue,
                'expenses': expenses,
                'profit': profit,
                'revenue_change': revenue_change,
                'profit_change': profit_change
            })
        
        # Calculate averages
        count = len(result)
        avg_profit = total_profit / count if count > 0 else 0
        
        return JsonResponse({
            'summary': {
                'total_revenue': total_revenue,
                'total_profit': total_profit,
                'avg_profit': avg_profit
            },
            'monthly_data': result
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
