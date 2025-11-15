from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
import psycopg2
from decimal import Decimal
import logging

# Set up logging
logger = logging.getLogger(__name__)

@require_http_methods(["GET", "POST"])
@csrf_protect
def login_view(request):
    """
    Enhanced login view with security features:
    - Input validation
    - Logging of login attempts
    - Session management with "Remember Me"
    - CSRF protection
    """
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        remember = request.POST.get("remember")
        
        # Input validation
        if not username or not password:
            logger.warning(f"Login attempt with missing credentials from IP: {get_client_ip(request)}")
            return render(request, "login.html", {
                "error": "Username and password are required"
            })
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is active
            if not user.is_active:
                logger.warning(f"Login attempt by inactive user: {username} from IP: {get_client_ip(request)}")
                return render(request, "login.html", {
                    "error": "Your account is inactive. Please contact administrator."
                })
            
            # Login successful
            login(request, user)
            
            # Set session expiry based on "Remember Me"
            if remember:
                # Session lasts 2 weeks (1209600 sec)
                request.session.set_expiry(1209600)
            else:
                # Session ends when browser closes
                request.session.set_expiry(0)
            
            # Log successful login
            logger.info(f"Successful login: {username} from IP: {get_client_ip(request)}")
            
            return redirect("dashboard")
        else:
            # Log failed login attempt
            logger.warning(f"Failed login attempt for username: {username} from IP: {get_client_ip(request)}")
            return render(request, "login.html", {
                "error": "Invalid username or password"
            })
    
    return render(request, "login.html")


def get_client_ip(request):
    """
    Get client IP address from request
    Useful for logging and rate limiting
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    Enhanced logout view with logging
    """
    username = request.user.username if request.user.is_authenticated else "Anonymous"
    logout(request)
    logger.info(f"User logged out: {username}")
    return redirect("login")


from .models import ProductInventory, RawMaterialInventory, Sales, Expenses, HistoryLog, StockChanges, Products, RawMaterials, AuthUser

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
def stock_changes(request):
    """Display stock changes with pagination"""
    # Get all stock changes ordered by date (newest first)
    changes_qs = StockChanges.objects.select_related('created_by_admin').order_by('-date')
    
    # Add item names to each change
    changes_list = []
    for change in changes_qs:
        item_name = "Unknown Item"
        if change.item_type == 'product':
            try:
                product = Products.objects.select_related(
                    'product_type', 'variant', 'size', 'size_unit'
                ).get(id=change.item_id)
                item_name = f"{product.product_type.name} - {product.variant.name} ({product.size.size_label} {product.size_unit.unit_name})"
            except Products.DoesNotExist:
                item_name = f"Product ID {change.item_id} (Deleted)"
        elif change.item_type == 'raw_material':
            try:
                material = RawMaterials.objects.select_related('unit').get(id=change.item_id)
                item_name = f"{material.name} ({material.size} {material.unit.unit_name})"
            except RawMaterials.DoesNotExist:
                item_name = f"Raw Material ID {change.item_id} (Deleted)"
        
        changes_list.append({
            'id': change.id,
            'item_name': item_name,
            'item_type': change.item_type,
            'quantity_change': change.quantity_change,
            'category': change.category,
            'date': change.date,
            'created_by': change.created_by_admin.username
        })
    
    # Paginate
    paginator = Paginator(changes_list, 20)
    page_number = request.GET.get('page')
    changes_page = paginator.get_page(page_number)
    
    return render(request, "stock_changes.html", {"changes": changes_page})


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


@login_required(login_url="login")
def user_activity(request):
    """Display list of users with their login/logout activity"""
    from django.contrib.sessions.models import Session
    from django.utils import timezone
    
    # Get all users
    users = AuthUser.objects.all().order_by('username')
    
    # Build user activity data
    user_list = []
    for user in users:
        # Get last login
        last_login = user.last_login
        
        # Check if user is currently logged in by checking active sessions
        is_active = False
        last_logout = None
        
        # Get all sessions
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        for session in active_sessions:
            session_data = session.get_decoded()
            if session_data.get('_auth_user_id') == str(user.id):
                is_active = True
                break
        
        # Determine status
        if not user.is_active:
            status = 'Inactive'
        elif is_active:
            status = 'Active'
        else:
            status = 'Logged Out'
        
        user_list.append({
            'username': user.username,
            'email': user.email,
            'status': status,
            'last_login': last_login,
            'last_logout': last_logout,
            'is_active': user.is_active
        })
    
    return render(request, "user_activity.html", {"users": user_list})
