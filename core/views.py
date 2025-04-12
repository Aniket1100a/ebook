import os
import json
import logging
from django.conf import settings
from django.http import FileResponse, JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.models import (
    Category, Vendor, Product, ProductImage, Purchase, Rental,
    Cart, Wishlist, Offer, Blog, CartOrder, CartOrderItem, Billboard, AboutSection, Library
)
from core.forms import ContactForm

# Home Page View
def index(request):
    """
    View for rendering the homepage.
    Includes billboard items, featured books, best-selling book, popular books, 
    books with active offers, and latest blogs.
    """
    billboards = Billboard.objects.filter(is_active=True).order_by('-created_at')
    featured_books = Product.objects.filter(is_featured=True, is_published=True).order_by('-created_at')[:8]
    best_selling = Product.objects.filter(is_best_seller=True, is_published=True).order_by('-created_at').first()
    popular_books = Product.objects.filter(is_popular=True, is_published=True).distinct().order_by('-created_at')
    offer_books = Product.objects.filter(
        offers__start_date__lte=now(), offers__end_date__gte=now(), is_published=True
    ).distinct().order_by('-created_at')
    blogs = Blog.objects.all().order_by('-created_at')[:3]

    context = {
        'billboards': billboards,
        'featured_books': featured_books,
        'best_selling': best_selling,
        'popular_books': popular_books,
        'offer_books': offer_books,
        'blogs': blogs,
    }

    return render(request, 'core/index.html', context)

def billboard_view(request):
    """
    View to render a dedicated page for billboard items dynamically.
    """
    billboards = Billboard.objects.filter(is_active=True).order_by('-created_at')
    context = {
        'billboards': billboards,
    }
    return render(request, 'core/billboard.html', context)

def product_list(request):
    """
    View to list all available products.
    """
    products = Product.objects.filter(is_published=True).order_by('-created_at')
    context = {
        'products': products,
    }
    return render(request, 'core/product_list.html', context)

def featured_books_view(request):
    """View to display featured books."""
    featured_books = Product.objects.filter(is_featured=True, is_published=True).order_by('-created_at')
    context = {
        'featured_books': featured_books,
    }
    return render(request, 'core/featured_books.html', context)

def product_detail(request, product_id):
    """View for displaying product details."""
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product,
    }
    return render(request, 'core/product_detail.html', context)

def popular_books_view(request):
    popular_books = Product.objects.filter(is_published=True, is_popular=True)
    return render(request, "core/popular_books.html", {"popular_books": popular_books})

def all_books_view(request):
    books = Product.objects.all()
    categories = Category.objects.all()
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(title__icontains=search_query) | books.filter(author__icontains=search_query)
    category_filter = request.GET.get('category', '')
    if category_filter:
        books = books.filter(category__title=category_filter)
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)
    if min_price:
        books = books.filter(price__gte=min_price)
    if max_price:
        books = books.filter(price__lte=max_price)

    context = {
        'books': books,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'min_price': min_price,
        'max_price': max_price,
        'offer_price': [book.get_offer_price() for book in books]
    }
    return render(request, 'core/all_books.html', context)

def blog_list(request):
    """
    View to list all blogs.
    """
    blogs = Blog.objects.all().order_by('-created_at')
    context = {
        'blogs': blogs,
    }
    return render(request, 'core/blog_list.html', context)

def blog_detail(request, bid):
    blog = get_object_or_404(Blog, bid=bid)
    return render(request, 'core/blog_detail.html', {'blog': blog})


import json
import razorpay
import logging
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Cart, Library, CartOrder, CartOrderItem, Product

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
import json
import logging
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Cart, CartOrder, CartOrderItem, Library

from razorpay.errors import BadRequestError, ServerError  # Import specific errors
import logging


# Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user, is_active=True)
    total_price = sum(item.get_total_price() for item in cart_items)

    # Generate order only if cart is not empty
    if total_price > 0:
        order_data = {"amount": int(total_price * 100), "currency": "INR", "payment_capture": "1"}
        razorpay_order = client.order.create(order_data)
        razorpay_order_id = razorpay_order["id"]
    else:
        razorpay_order_id = None  # No need for payment if total is 0

    return render(request, 'core/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': razorpay_order_id
    })

@login_required
def create_order(request):
    if request.method == "POST":
        cart_items = Cart.objects.filter(user=request.user, is_active=True)
        if not cart_items:
            return JsonResponse({"error": "Cart is empty."}, status=400)

        total_price = sum(item.get_total_price() for item in cart_items) * 100  # Convert to paise

        try:
            order_data = {"amount": total_price, "currency": "INR", "payment_capture": "1"}
            razorpay_order = client.order.create(data=order_data)
            return JsonResponse({"order_id": razorpay_order["id"], "amount": total_price})
        except razorpay.errors.RazorpayError as e:
            logging.error(f"Error creating Razorpay order: {e}")
            return JsonResponse({"error": "Failed to create order."}, status=500)

    return JsonResponse({"error": "Invalid request."}, status=400)

from django.shortcuts import redirect

@login_required
def cart_order(request):
    if request.method == 'POST':
        try:
            # Handle Free Books
            if "free_books" in request.POST:
                cart_items = Cart.objects.filter(user=request.user, is_active=True, product__price=0)

                if not cart_items:
                    messages.error(request, "No free books in cart.")
                    return redirect("core:cart_view")  # Redirect to cart if no free books

                for item in cart_items:
                    Library.objects.get_or_create(user=request.user, product=item.product)
                    item.delete()  # Remove free books from cart

                messages.success(request, "Free books added to your Library.")
                return redirect("core:library")  # Redirect to library page after success

            # Process Paid Books with Razorpay
            data = json.loads(request.body)
            payment_id = data.get("razorpay_payment_id")
            order_id = data.get("razorpay_order_id")
            signature = data.get("razorpay_signature")

            cart_items = Cart.objects.filter(user=request.user, is_active=True, product__price__gt=0)
            if not cart_items:
                messages.error(request, "No paid items in cart.")
                return redirect("core:cart_view")

            if not all([payment_id, order_id, signature]):
                return JsonResponse({"error": "Missing payment details."}, status=400)

            # Verify Payment
            client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            })

            total_price = sum(item.get_total_price() for item in cart_items)

            # Create Order
            cart_order = CartOrder.objects.create(
                user=request.user,
                total_price=total_price,
                razorpay_order_id=order_id,
                payment_status="Paid"
            )

            # Move Paid Items to Library
            for item in cart_items:
                CartOrderItem.objects.create(order=cart_order, product=item.product, quantity=item.quantity, price=item.get_total_price())
                Library.objects.get_or_create(user=request.user, product=item.product)
                item.delete()

            messages.success(request, "Payment successful! Books added to your Library.")
            return redirect("core:library")

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed.")
            return redirect("core:cart_view")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            messages.error(request, "An error occurred.")
            return redirect("core:cart_view")

    return redirect("core:cart_view")  # Redirect if not a POST request




import razorpay
from razorpay.errors import BadRequestError, ServerError  # Import specific errors
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from core.models import Cart

from decimal import Decimal

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user, is_active=True)
    total_price = float(sum(item.get_total_price() for item in cart_items)) * 100  # Convert to paise

    # If books are free, add to library and clear cart
    if total_price == 0:
        for item in cart_items:
            Library.objects.get_or_create(user=request.user, product=item.product)

        cart_items.delete()
        return redirect('core:library')  # Redirect user to their library

    try:
        order_data = {
            "amount": int(total_price),
            "currency": "INR",
            "payment_capture": "1"
        }
        razorpay_order = client.order.create(data=order_data)

        return render(request, 'core/checkout.html', {
            'cart_items': cart_items,
            'total_price': total_price / 100,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order["id"]
        })
    except (razorpay.errors.BadRequestError, razorpay.errors.ServerError) as e:
        logging.error(f"Error creating Razorpay order: {e}")
        return redirect('core:cart_view')  # Redirect if order fails

@login_required
def add_free_books(request):
    cart_items = Cart.objects.filter(user=request.user, is_active=True)

    for item in cart_items:
        if item.product.price == 0:  # Only add free books
            Library.objects.get_or_create(user=request.user, product=item.product)
            item.is_active = False  # Mark as inactive (remove from cart)
            item.save()

    return redirect('core:library')  # Redirect to the library


import json
import logging
import razorpay
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from core.models import Cart, Library, Product, Book  # Ensure these are imported

@csrf_exempt
@login_required
def verify_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            payment_id = data.get("razorpay_payment_id")
            order_id = data.get("razorpay_order_id")
            signature = data.get("razorpay_signature")

            if not all([payment_id, order_id, signature]):
                return JsonResponse({"error": "Missing payment details."}, status=400)

            # Verify Razorpay Payment
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            })

            # Move items from cart to user's library
            user = request.user
            cart_items = Cart.objects.filter(user=user, is_active=True)

            for item in cart_items:
                Library.objects.get_or_create(user=user, product=item.product)

            # Clear the cart after successful payment
            cart_items.delete()

            return JsonResponse({"success": True, "message": "Payment verified. Books added to your library."})
        
        except Exception as e:
            logging.error(f"Payment verification failed: {e}")
            return JsonResponse({"error": "Payment verification failed."}, status=400)

    return JsonResponse({"error": "Invalid request."}, status=400)



@login_required
def remove_from_cart(request, item_id):
    if request.method == "POST":
        try:
            item = Cart.objects.get(id=item_id, user=request.user)
            item.delete()
            return JsonResponse({"success": True, "message": "Item removed."})
        except Cart.DoesNotExist:
            return JsonResponse({"error": "Item not found."}, status=404)
    return JsonResponse({"error": "Invalid request."}, status=400)

@login_required
def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            return JsonResponse({"success": True, "message": "Product added to cart."})
        except Exception as e:
            logging.error(f"Error adding to cart: {e}")
            return JsonResponse({"error": "Could not add to cart."}, status=500)
    return JsonResponse({"error": "Invalid request."}, status=400)


@login_required
def library_view(request):
    """
    View to display the user's library.
    """
    library_items = Library.objects.filter(user=request.user)
    context = {
        'library_items': library_items,
    }
    return render(request, 'core/library.html', context)







@login_required
def read_book(request, book_id):
    book = get_object_or_404(Product, id=book_id)
    if not book.pdf_file:
        return render(request, 'core/read_book.html', {'book': book, 'error': 'PDF not available'})
    pdf_url = book.pdf_file.url
    return render(request, 'core/read_book.html', {'book': book, 'pdf_url': pdf_url})



def about_view(request):
    about_sections = AboutSection.objects.all()
    return render(request, 'core/about.html', {'about_sections': about_sections})

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:contact')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})

def book_detail_view(request, book_id):
    book = get_object_or_404(Product, id=book_id)
    return render(request, 'core/book_detail.html', {'book': book})


