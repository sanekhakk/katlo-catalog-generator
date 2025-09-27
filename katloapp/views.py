from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.views.decorators.http import require_http_methods

from .models import Business, Product
from .forms import BusinessForm, ProductForm
from .utils import build_whatsapp_link, generate_qr_image_bytes


def public_home(request):
    """Public homepage showing statistics."""
    total_catalogues = Business.objects.filter(public=True).count()
    total_products = Product.objects.filter(business__public=True, active=True).count()
    
    context = {
        'total_catalogues': total_catalogues,
        'total_products': total_products
    }
    return render(request, 'katloapp/public_home.html', context)


def catalog_list(request):
    """A new page to display all public business catalogs."""
    businesses = Business.objects.filter(public=True).order_by('-created_at')
    return render(request, 'katloapp/catalog_list.html', {'businesses': businesses})


def business_login(request):
    """Business login view"""
    if request.user.is_authenticated:
        return redirect('katloapp:dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('katloapp:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please provide both username and password.')
    
    return render(request, 'katloapp/business_login.html')


def business_register(request):
    """Business registration view"""
    if request.user.is_authenticated:
        return redirect('katloapp:dashboard')
        
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Business.objects.create(
                user=user,
                name=f"{user.username}'s Business",
                public=False
            )
            login(request, user)
            messages.success(request, "Account created successfully! Please complete your business information.")
            return redirect("katloapp:business_edit")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = UserCreationForm()
    
    return render(request, "katloapp/business_register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def custom_logout(request):
    """Custom logout view that works for both GET and POST requests"""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'Goodbye {username}! You have been logged out successfully.')
    return redirect('katloapp:public_home')


@login_required
def admin_logout_redirect(request):
    """Redirect admin users to main site after logout"""
    logout(request)
    messages.info(request, 'You have been logged out from the admin panel.')
    return redirect('katloapp:public_home')


@login_required
def dashboard(request):
    """Main business dashboard"""
    try:
        business = request.user.business
    except Business.DoesNotExist:
        # Create business if it doesn't exist
        business = Business.objects.create(
            user=request.user,
            name=request.user.get_full_name() or f"{request.user.username}'s Business"
        )
    
    products = business.products.filter(active=True).order_by('-created_at')
    
    # Check if business setup is complete
    setup_complete = bool(business.whatsapp_number and business.description)
    if not setup_complete:
        messages.info(request, 'Complete your business profile to start sharing your catalog!')
        
    public_url = request.build_absolute_uri(business.get_public_url())
    
    return render(request, 'katloapp/business_dashboard.html', {
        'business': business, 
        'products': products,
        'setup_complete': setup_complete,
        'public_url': public_url
    })


@login_required
def business_edit(request):
    """Edit business information"""
    try:
        business = request.user.business
    except Business.DoesNotExist:
        business = Business.objects.create(
            user=request.user,
            name=request.user.get_full_name() or f"{request.user.username}'s Business"
        )
    
    if request.method == 'POST':
        form = BusinessForm(request.POST, instance=business)
        if form.is_valid():
            form.save()
            messages.success(request, 'Business information updated successfully!')
            return redirect('katloapp:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BusinessForm(instance=business)
    
    return render(request, 'katloapp/business_form.html', {'form': form, 'business': business})


@login_required
def product_list(request):
    """List all products for the logged-in business"""
    try:
        business = request.user.business
    except Business.DoesNotExist:
        messages.error(request, 'Please complete your business profile first.')
        return redirect('katloapp:business_edit')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    products = business.products.all()
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(sku__icontains=search_query)
        )
    
    # Status filter
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'active':
        products = products.filter(active=True)
    elif status_filter == 'inactive':
        products = products.filter(active=False)
    
    products = products.order_by('-created_at')
    
    return render(request, 'katloapp/product_list.html', {
        'products': products,
        'search_query': search_query,
        'status_filter': status_filter
    })


@login_required
def product_create(request):
    """Create a new product"""
    try:
        business = request.user.business
    except Business.DoesNotExist:
        messages.error(request, 'Please complete your business profile first.')
        return redirect('katloapp:business_edit')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.business = business
            product.save()
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('katloapp:product_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    
    return render(request, 'katloapp/product_form.html', {
        'form': form, 
        'page_title': 'Add New Product'
    })


@login_required
def product_edit(request, pk):
    """Edit an existing product"""
    product = get_object_or_404(Product, pk=pk, business__user=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('katloapp:product_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'katloapp/product_form.html', {
        'form': form, 
        'product': product,
        'page_title': 'Edit Product'
    })


@login_required
def product_delete(request, pk):
    """Delete a product"""
    product = get_object_or_404(Product, pk=pk, business__user=request.user)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('katloapp:product_list')
    
    return render(request, 'katloapp/product_confirm_delete.html', {'product': product})


def public_catalog(request, slug):
    """Public catalog view for customers"""
    business = get_object_or_404(Business, slug=slug, public=True)
    products = business.products.filter(active=True).order_by('-created_at')
    
    # Get the absolute URL for the catalog
    catalog_url = request.build_absolute_uri(business.get_public_url())

    products_with_links = []
    if business.whatsapp_number:
        for product in products:
            message = (
                f"Hi {business.name}, I'm interested in your product: *{product.name}*.\n\n"
                f"Seen on your Katlo catalog: {catalog_url}"
            )
            product.whatsapp_link = build_whatsapp_link(business.whatsapp_number, message)
            products_with_links.append(product)
    else:
        products_with_links = products

    # Build a general WhatsApp link for the business
    general_message = f"Hi! I found your business '{business.name}' via Katlo and would like to know more. {catalog_url}"
    wa_link = build_whatsapp_link(business.whatsapp_number, general_message) if business.whatsapp_number else None
    
    context = {
        'business': business, 
        'products': products_with_links, 
        'wa_link': wa_link,
        'catalog_url': catalog_url,
        'product_count': products.count()
    }
    
    return render(request, 'katloapp/public_catalog.html', context)


@login_required
def download_qr(request, slug):
    """Download QR code for WhatsApp catalog link"""
    business = get_object_or_404(Business, slug=slug, user=request.user)
    
    if not business.whatsapp_number:
        messages.error(request, 'Please add your WhatsApp number first.')
        return redirect('katloapp:business_edit')
    
    # Build the catalog URL and WhatsApp link
    catalog_url = request.build_absolute_uri(business.get_public_url())
    message = f"Hi! I'm interested in your products from {business.name}. {catalog_url}"
    wa_link = build_whatsapp_link(business.whatsapp_number, message)
    
    try:
        # Generate QR code
        buf = generate_qr_image_bytes(wa_link)
        
        # Return as downloadable file
        response = HttpResponse(buf, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{business.slug}-whatsapp-qr.png"'
        return response
        
    except Exception as e:
        messages.error(request, 'Error generating QR code. Please try again.')
        return redirect('katloapp:dashboard')