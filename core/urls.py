from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

app_name = "core"

urlpatterns = [
    # Homepage
    path("", views.index, name="index"),
    
    # Book-related routes
    path('all-books/', views.all_books_view, name='all_books'),
    path('book/<int:book_id>/', views.book_detail_view, name='book_detail'),
    path('read/<int:book_id>/', views.read_book, name='read_book'),
    path('read-book/<int:book_id>/', views.read_book, name='read_book'),

    # Product-related routes
    path("products/", views.product_list, name="product_list"),
    path("featured-books/", views.featured_books_view, name="featured_books"),
    path("popular-books/", views.popular_books_view, name="popular_books"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),

    # Blog-related routes
    path("blogs/", views.blog_list, name="blog_list"),  # List of all blogs
    path('blogs/<str:bid>/', views.blog_detail, name='blog_detail'),

    # Cart-related routes
    path('cart_view/', views.cart_view, name='cart_view'),  # Redirects to the cart page
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart-order/', views.cart_order, name='cart_order'),

    # Other routes
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('library/', views.library_view, name='library'),

    path("add-free-books/", views.add_free_books, name="core:add_free_books"),
    

    path("create-order/", views.create_order, name="create_order"),
    path('checkout/', views.checkout, name='checkout'),
    path('verify_payment/', views.verify_payment, name='verify_payment'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
