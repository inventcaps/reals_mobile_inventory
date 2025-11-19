from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from django.http import JsonResponse, FileResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
import psycopg2
from decimal import Decimal
import logging
from datetime import datetime
import os

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
            # Ensure only superusers can access the mobile dashboard
            if not user.is_superuser:
                logger.warning(f"Blocked login for non-superuser: {username} from IP: {get_client_ip(request)}")
                return render(request, "login.html", {
                    "error": "Only administrator accounts are allowed to sign in on mobile."
                })

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


from .models import (
    ProductInventory,
    RawMaterialInventory,
    Sales,
    Expenses,
    HistoryLog,
    StockChanges,
    Products,
    RawMaterials,
    AuthUser,
    Withdrawals,
)

@login_required(login_url="login")
def dashboard(request):
    context = {
        "product_count": ProductInventory.objects.filter(product__is_archived=False).count(),
        "raw_count": RawMaterialInventory.objects.filter(material__is_archived=False).count(),
        "sales_count": Sales.objects.count(),
        "expense_count": Expenses.objects.count(),
        "log_count": HistoryLog.objects.count(),
    }
    return render(request, "dashboard.html", context)

@login_required(login_url="login")
def product_stock(request):
    search_query = request.GET.get('q', '').strip()

    products_qs = (
        ProductInventory.objects
        .select_related("product")
        .filter(product__is_archived=False)
        .order_by("product__id")
    )
    if search_query:
        products_qs = products_qs.filter(
            Q(product__product_type__name__icontains=search_query) |
            Q(product__variant__name__icontains=search_query) |
            Q(product__description__icontains=search_query)
        )
    paginator = Paginator(products_qs, 10)
    page_number = request.GET.get("page")
    products_page = paginator.get_page(page_number)
    return render(request, "product_stock.html", {
        "products": products_page,
        "search_query": search_query,
    })


@login_required(login_url="login")
def raw_stock(request):
    search_query = request.GET.get('q', '').strip()

    raws_qs = (
        RawMaterialInventory.objects
        .select_related("material")
        .filter(material__is_archived=False)
        .order_by('material__name')
    )
    if search_query:
        raws_qs = raws_qs.filter(
            Q(material__name__icontains=search_query)
        )
    paginator = Paginator(raws_qs, 10)
    page_number = request.GET.get("page")
    raws_page = paginator.get_page(page_number)
    return render(request, "raw_stock.html", {
        "raws": raws_page,
        "search_query": search_query,
    })


@login_required(login_url="login")
def best_sellers(request):
    """Display top/low selling products using mobile-friendly widgets"""
    month_param = request.GET.get('month')
    show_all = request.GET.get('show_all') == '1'

    now = timezone.localtime()
    filter_year = now.year
    filter_month = now.month
    filter_label = now.strftime('%B %Y')

    if month_param and '-' in month_param:
        try:
            parsed = datetime.strptime(month_param, "%Y-%m")
            filter_year, filter_month = parsed.year, parsed.month
            filter_label = parsed.strftime('%B %Y')
        except ValueError:
            pass

    withdrawals_qs = Withdrawals.objects.filter(
        item_type='PRODUCT',
        reason='SOLD',
        is_archived=False
    )

    if not show_all:
        withdrawals_qs = withdrawals_qs.filter(date__year=filter_year, date__month=filter_month)
    else:
        filter_label = 'All Time'

    product_sales: dict[int, dict[str, Decimal]] = {}
    for withdrawal in withdrawals_qs:
        stats = product_sales.setdefault(withdrawal.item_id, {
            'total_quantity': Decimal('0'),
            'total_revenue': Decimal('0'),
        })
        quantity = Decimal(withdrawal.quantity or 0)
        stats['total_quantity'] += quantity
        price = withdrawal.custom_price if withdrawal.custom_price is not None else Decimal('0')
        stats['total_revenue'] += price * quantity

    product_ids = list(product_sales.keys())
    products_map = {
        product.id: product
        for product in Products.objects.select_related(
            'product_type', 'variant', 'size', 'size_unit'
        ).filter(id__in=product_ids)
    }

    def describe_product(product_obj):
        if not product_obj:
            return ('Archived Product', 'Record no longer available')
        return (
            f"{product_obj.product_type.name} - {product_obj.variant.name}",
            f"{product_obj.size.size_label} {product_obj.size_unit.unit_name}"
        )

    sold_products = []
    for pid, stats in product_sales.items():
        name, detail = describe_product(products_map.get(pid))
        sold_products.append({
            'product_id': pid,
            'name': name,
            'detail': detail,
            'total_quantity': stats['total_quantity'],
            'total_revenue': stats['total_revenue'],
        })

    best_selling = sorted(sold_products, key=lambda item: item['total_quantity'], reverse=True)[:10]
    low_selling = sorted(sold_products, key=lambda item: item['total_quantity'])[:10]

    if len(low_selling) < 10:
        missing = 10 - len(low_selling)
        zero_products = (
            Products.objects.filter(is_archived=False)
            .exclude(id__in=product_ids)
            .select_related('product_type', 'variant', 'size', 'size_unit')
            .order_by('product_type__name', 'variant__name')[:missing]
        )
        for product in zero_products:
            name, detail = describe_product(product)
            low_selling.append({
                'product_id': product.id,
                'name': name,
                'detail': detail,
                'total_quantity': Decimal('0'),
                'total_revenue': Decimal('0'),
            })

    available_years = sorted({d.year for d in Withdrawals.objects.filter(
        item_type='PRODUCT', reason='SOLD', is_archived=False
    ).dates('date', 'year')})
    month_choices = [
        {'value': f"{m:02d}", 'label': datetime(2000, m, 1).strftime('%B')}
        for m in range(1, 13)
    ]

    context = {
        'best_sellers': best_selling,
        'low_sellers': low_selling,
        'filter_label': filter_label,
        'show_all': show_all,
        'filters': {
            'selected_value': f"{filter_year}-{filter_month:02d}",
            'show_all': show_all,
            'available_years': available_years,
            'month_choices': month_choices,
        }
    }

    return render(request, "best_sellers.html", context)


@login_required(login_url="login")
def history_log_view(request):
    logs_qs = HistoryLog.objects.select_related("admin", "log_type").order_by("-log_date")
    paginator = Paginator(logs_qs, 10)
    page_number = request.GET.get("page")
    logs_page = paginator.get_page(page_number)
    return render(request, "history_log.html", {"logs": logs_page})


@login_required(login_url="login")
def sales_list(request):
    search_query = request.GET.get('q', '').strip()

    sales_qs = Sales.objects.all().order_by('-date')
    if search_query:
        sales_qs = sales_qs.filter(
            Q(category__icontains=search_query) 
            # Q(description__icontains=search_query)
        )
    paginator = Paginator(sales_qs, 10)
    page_number = request.GET.get("page")
    sales_page = paginator.get_page(page_number)
    return render(request, "sales_list.html", {
        "sales": sales_page,
        "search_query": search_query,
    })


@login_required(login_url="login")
def expenses_list(request):
    search_query = request.GET.get('q', '').strip()

    expenses_qs = Expenses.objects.all().order_by('-date')
    if search_query:
        expenses_qs = expenses_qs.filter(
            Q(category__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    paginator = Paginator(expenses_qs, 10)
    page_number = request.GET.get("page")
    expenses_page = paginator.get_page(page_number)
    return render(request, "expenses_list.html", {
        "expenses": expenses_page,
        "search_query": search_query,
    })


@login_required(login_url="login")
def stock_changes(request):
    """Display stock changes with pagination"""
    search_query = request.GET.get('q', '').strip()
    changes_qs = StockChanges.objects.select_related('created_by_admin').order_by('-date')

    def build_change_rows(changes):
        """Attach display data (item name, creator) to StockChanges instances."""
        if not changes:
            return []

        product_ids = {c.item_id for c in changes if (c.item_type or '').lower() == 'product'}
        raw_ids = {c.item_id for c in changes if (c.item_type or '').lower() == 'raw_material'}

        product_map = {}
        if product_ids:
            product_qs = (
                Products.objects.select_related('product_type', 'variant', 'size', 'size_unit')
                .filter(id__in=product_ids)
            )
            for product in product_qs:
                size_label = getattr(product.size, 'size_label', 'N/A')
                unit_name = getattr(product.size_unit, 'unit_name', '')
                product_map[product.id] = (
                    f"{product.product_type.name} - {product.variant.name} "
                    f"({size_label} {unit_name})"
                )

        raw_map = {}
        if raw_ids:
            raw_qs = RawMaterials.objects.select_related('unit').filter(id__in=raw_ids)
            for material in raw_qs:
                unit_name = getattr(material.unit, 'unit_name', '')
                raw_map[material.id] = f"{material.name} ({material.size} {unit_name})"

        rows = []
        for change in changes:
            item_type = (change.item_type or '').lower()
            if item_type == 'product':
                item_name = product_map.get(change.item_id, f"Product ID {change.item_id} (Deleted)")
            elif item_type == 'raw_material':
                item_name = raw_map.get(change.item_id, f"Raw Material ID {change.item_id} (Deleted)")
            else:
                item_name = "Unknown Item"

            rows.append({
                'id': change.id,
                'item_name': item_name,
                'item_type': change.item_type,
                'quantity_change': change.quantity_change,
                'category': change.category,
                'date': change.date,
                'created_by': getattr(change.created_by_admin, 'username', 'System')
            })
        return rows

    page_number = request.GET.get('page')

    if search_query:
        # Only build the expensive list when actually searching
        all_changes = list(changes_qs)
        changes_list = build_change_rows(all_changes)
        query = search_query.lower()
        filtered = [
            entry for entry in changes_list
            if query in entry['item_name'].lower()
            or query in (entry['item_type'] or '').lower()
            or query in entry['category'].lower()
            or query in str(entry['quantity_change']).lower()
            or query in entry['created_by'].lower()
        ]
        paginator = Paginator(filtered, 10)
        changes_page = paginator.get_page(page_number)
    else:
        paginator = Paginator(changes_qs, 10)
        changes_page = paginator.get_page(page_number)
        changes_page.object_list = build_change_rows(list(changes_page.object_list))

    return render(request, "stock_changes.html", {
        "changes": changes_page,
        "search_query": search_query,
    })


@login_required(login_url="login")
def monthly_report(request):
    """Render monthly business report page"""
    return render(request, "monthly_report.html")

@login_required(login_url="login")
def monthly_report_data(request):
    """Mirror production monthly report logic using ORM"""
    sales = (
        Sales.objects.annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total_sales=Sum("amount"))
        .order_by("month")
    )

    expenses = (
        Expenses.objects.annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total_expenses=Sum("amount"))
        .order_by("month")
    )

    loss_withdrawals = list(
        Withdrawals.objects
        .filter(
            reason__in=['EXPIRED', 'DAMAGED', 'REPLACEMENT_FOR_RETURNED'],
            is_archived=False
        )
        .annotate(month=TruncMonth("date"))
        .values("month", "item_type", "item_id", "quantity", "custom_price")
    )

    product_ids = {w["item_id"] for w in loss_withdrawals if w["item_type"] == 'PRODUCT'}
    raw_ids = {w["item_id"] for w in loss_withdrawals if w["item_type"] == 'RAW_MATERIAL'}

    product_prices = {}
    if product_ids:
        product_qs = Products.objects.select_related('unit_price').filter(id__in=product_ids)
        for product in product_qs:
            product_prices[product.id] = Decimal(product.unit_price.unit_price)

    raw_prices = {}
    if raw_ids:
        raw_qs = RawMaterials.objects.filter(id__in=raw_ids)
        for material in raw_qs:
            raw_prices[material.id] = Decimal(material.price_per_unit)

    financial_loss_dict = {}
    for withdrawal in loss_withdrawals:
        month = withdrawal["month"]
        if month not in financial_loss_dict:
            financial_loss_dict[month] = Decimal('0.00')

        quantity = Decimal(withdrawal["quantity"]) if withdrawal["quantity"] is not None else Decimal('0.00')
        custom_price = withdrawal.get("custom_price")
        if custom_price is not None:
            price = Decimal(custom_price)
        elif withdrawal["item_type"] == 'PRODUCT':
            price = product_prices.get(withdrawal["item_id"])
        else:
            price = raw_prices.get(withdrawal["item_id"])

        if price is None:
            continue

        loss_amount = quantity * price
        financial_loss_dict[month] += loss_amount

    def normalize_date(dt):
        return dt.date() if hasattr(dt, 'date') else dt

    expenses_dict = {normalize_date(e["month"]): e["total_expenses"] for e in expenses}
    sales_dict = {normalize_date(s["month"]): s["total_sales"] for s in sales}
    normalized_loss = {normalize_date(m): amt for m, amt in financial_loss_dict.items()}

    months = sorted(set(list(sales_dict.keys()) + list(expenses_dict.keys()) + list(normalized_loss.keys())))

    report = []
    prev = None
    for month in months:
        gross_revenue = Decimal(sales_dict.get(month, 0) or 0)
        loss = Decimal(normalized_loss.get(month, 0) or 0)
        revenue = gross_revenue - loss
        expense = Decimal(expenses_dict.get(month, 0) or 0)
        profit = revenue - expense

        revenue_change = profit_change = None
        if prev:
            revenue_change = revenue - prev["revenue"]
            profit_change = profit - prev["profit"]

        entry = {
            "month": month.strftime("%B %Y"),
            "revenue": float(revenue),
            "loss": float(loss),
            "expenses": float(expense),
            "profit": float(profit),
            "revenue_change": float(revenue_change) if revenue_change is not None else None,
            "profit_change": float(profit_change) if profit_change is not None else None,
        }
        report.append(entry)
        prev = {k: (Decimal(v) if isinstance(v, float) else v) for k, v in entry.items() if k in ["revenue", "profit"]}

    total_revenue = sum(r["revenue"] for r in report)
    total_loss = sum(r["loss"] for r in report)
    total_profit = sum(r["profit"] for r in report)
    avg_profit = total_profit / len(report) if report else 0

    return JsonResponse({
        "summary": {
            "total_revenue": total_revenue,
            "total_loss": total_loss,
            "total_profit": total_profit,
            "avg_profit": avg_profit,
        },
        "monthly_data": report
    })


@login_required(login_url="login")
def user_activity(request):
    """Display list of users with their login/logout activity"""
    from django.contrib.sessions.models import Session
    from django.utils import timezone
    
    # Preload active sessions once to avoid repeated decoding and skip corrupted rows
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    active_user_ids = set()
    for session in active_sessions:
        try:
            session_data = session.get_decoded()
        except Exception as exc:
            logger.warning(f"Skipping corrupted session {session.session_key}: {exc}")
            continue
        user_id = session_data.get('_auth_user_id')
        if user_id:
            try:
                active_user_ids.add(int(user_id))
            except ValueError:
                continue

    # Get all users
    users = AuthUser.objects.all().order_by('username')
    
    # Build user activity data
    user_list = []
    excluded_prefixes = ("deleted_", "inactive_", "rejected_")
    for user in users:
        username_lower = (user.username or "").lower()
        if username_lower.startswith(excluded_prefixes):
            continue
        # Get last login
        last_login = user.last_login
        
        # Determine status
        if not user.is_active:
            status = 'Inactive'
        elif user.id in active_user_ids:
            status = 'Active'
        else:
            status = 'Logged Out'
        
        user_list.append({
            'username': user.username,
            'email': user.email,
            'status': status,
            'last_login': last_login,
            'last_logout': None,
            'is_active': user.is_active
        })
    
    return render(request, "user_activity.html", {"users": user_list})


@require_http_methods(["GET"])
def service_worker(request):
    """Serve service worker from project root scope"""
    sw_path = os.path.join(settings.BASE_DIR, "static", "service-worker.js")
    if not os.path.exists(sw_path):
        return JsonResponse({"error": "Service worker not found"}, status=404)
    response = FileResponse(open(sw_path, "rb"), content_type="application/javascript")
    # prevent caching issues when updating SW
    response['Cache-Control'] = 'no-cache'
    return response
