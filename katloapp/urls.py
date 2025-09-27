from django.urls import path
from . import views

app_name = "katloapp"

urlpatterns = [
    path('', views.public_home, name='public_home'),
    path('catalogs/', views.catalog_list, name='catalog_list'), 

    # Business Auth
    path('business/login/', views.business_login, name='business_login'),
    path('business/register/', views.business_register, name='business_register'),
    path('business/logout/', views.custom_logout, name='custom_logout'),

    # Dashboard & Business Info
    path('dashboard/', views.dashboard, name='dashboard'),
    path('business/edit/', views.business_edit, name='business_edit'),

    # Product Management
    path('products/', views.product_list, name='product_list'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Public Catalog
    path('catalog/<slug:slug>/', views.public_catalog, name='public_catalog'),
    path('catalog/<slug:slug>/qr/', views.download_qr, name='download_qr'),
    
    # Admin helpers
    path('admin-logout/', views.admin_logout_redirect, name='admin_logout_redirect'),
]