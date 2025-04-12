from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.timezone import now
from django.utils.html import mark_safe
from django.utils.text import slugify
from django.templatetags.static import static
from shortuuid.django_fields import ShortUUIDField

# Helper function for dynamic image path
def user_directory_path(instance, filename):
    """Generates upload path for user-specific files."""
    return f'user_{instance.user.id}/{filename}'

def vendor_directory_path(instance, filename):
    """Generates upload path for vendor images."""
    return f'vendors/{instance.title}/{filename}'

class Category(models.Model):
    """Model representing product categories."""
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="abcdefgh12345")
    title = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to="category", default="category/default.jpg", blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['title']
        db_table = 'category'

    def category_image(self):
        """Returns a small HTML snippet to display the category image in the admin panel."""
        if self.image and hasattr(self.image, 'url'):
            return mark_safe(f'<img src="{self.image.url}" width="50px" style="border-radius: 5px;" />')
        return mark_safe('<span>No Image Available</span>')

    category_image.short_description = "Image Preview"

    def __str__(self):
        return self.title

class Vendor(models.Model):
    """Model representing product vendors."""
    vid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="ven", alphabet="abcdefgh12345")
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    image = models.ImageField(upload_to=vendor_directory_path, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15, blank=True, null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )
    address = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "vendors"
        ordering = ['title']
        db_table = 'vendor'

    def save(self, *args, **kwargs):
        """Generates slug if not present and saves the instance."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def vendor_image(self):
        """Returns an HTML image tag for the vendor's image."""
        if self.image and hasattr(self.image, 'url'):
            return mark_safe(f'<img src="{self.image.url}" width="50px" />')
        return "No Image Available"

    def __str__(self):
        return self.title

class Billboard(models.Model):
    """Model for managing billboard items."""
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True)
    image = models.ImageField(upload_to="billboard_images/")
    link = models.URLField(blank=True, null=True, help_text="Optional link for the billboard item")
    is_active = models.BooleanField(default=True, help_text="Only active items are displayed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Billboards"
        ordering = ['-created_at']
        db_table = 'billboard'

    def __str__(self):
        return self.title

class Book(models.Model):
    """Model representing a book."""
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    description = models.TextField()

    def get_old_price(self):
        """Returns the original price of the book or 'Free' if price is 0."""
        return "Free" if self.price == 0 else f"₹ {self.price}"

    def get_offer_price(self):
        """Returns the discounted price if discount is available or 'Free' if price is 0."""
        if self.price == 0:
            return "Free"
        if self.discount_percentage:
            discount = self.price * (self.discount_percentage / 100)
            return round(self.price - discount, 2)
        return self.price

    def __str__(self):
        return self.title

class Product(models.Model):
    """Model representing eBooks or any product in the store."""
    pid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="prd", alphabet="abcdefgh12345")
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name="products")
    vendor = models.ForeignKey('Vendor', on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    cover_image = models.ImageField(upload_to="product_images/", blank=True, null=True)
    pdf_file = models.FileField(upload_to="protected_pdfs/", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)], editable=False)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True, validators=[MinValueValidator(0)], help_text="Temporary price during an active offer")
    is_rentable = models.BooleanField(default=False)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False, db_index=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    is_best_seller = models.BooleanField(default=False)
    popularity_score = models.PositiveIntegerField(default=0)
    total_sales = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "products"
        ordering = ['-created_at']
        db_table = 'product'

    def __str__(self):
        return self.title

    def product_image(self):
        """Returns the product image URL or a default image if not available."""
        if self.cover_image and hasattr(self.cover_image, 'url'):
            return self.cover_image.url
        return static('assets/images/default_book_cover.jpg')

    def save(self, *args, **kwargs):
        """Ensure original_price is set only on creation."""
        if not self.pk:
            self.original_price = self.price  
        super().save(*args, **kwargs)

    def get_offer_price(self):
        """Returns the price during an active offer if available or 'Free' if price is 0."""
        if self.price == 0:
            return "Free"
        active_offer = self.offers.filter(start_date__lte=now(), end_date__gte=now()).first()
        if active_offer:
            discount = (self.price * active_offer.discount_percentage) / 100
            self.offer_price = round(self.price - discount, 2)
            self.save(update_fields=['offer_price'])
            return self.offer_price
        else:
            self.offer_price = None
            self.save(update_fields=['offer_price'])
            return self.price

    def get_old_price(self):
        """Returns the original price of the product or 'Free' if price is 0."""
        return "Free" if self.original_price == 0 else f"₹ {self.original_price}"

class Library(models.Model):
    """Model representing a user's library and the books they own."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="library")
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True, related_name="libraries")
    book = models.ForeignKey('Book', on_delete=models.CASCADE, null=True, blank=True, related_name="libraries")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username}'s Library - {self.product or self.book}"

class ProductImage(models.Model):
    """Model for managing multiple images for a single product."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="product_images/")
    alt_text = models.CharField(max_length=255, blank=True, null=True, help_text="Alternative text for the image (for accessibility).")
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "product images"
        db_table = 'product_image'

    def __str__(self):
        return f"Image for {self.product.title}"

class Purchase(models.Model):
    """Model for tracking purchased books."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="purchases")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="purchases")
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "purchases"
        db_table = 'purchase'

    def __str__(self):
        return f"{self.user.username} purchased {self.product.title}"

class Rental(models.Model):
    """Model for tracking rented books."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rentals")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="rentals")
    rented_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name_plural = "rentals"
        db_table = 'rental'

    def __str__(self):
        return f"{self.user.username} rented {self.product.title}"

    def is_active(self):
        """Check if the rental is still active."""
        return now() < self.expires_at

class Offer(models.Model):
    """Model representing special offers for books."""
    oid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="off", alphabet="abcdefgh12345")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    discount_percentage = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], help_text="Discount percentage (e.g., 20 for 20%).")
    product = models.ForeignKey('core.Product', on_delete=models.CASCADE, related_name="offers")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        verbose_name_plural = "Offers"
        db_table = 'offer'

    def __str__(self):
        return f"{self.title} - {self.discount_percentage}%"

    def is_active(self):
        """Check if the offer is currently active."""
        return self.start_date <= now() <= self.end_date

class Wishlist(models.Model):
    """Model for managing wishlist items."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist_items")

    class Meta:
        unique_together = ('user', 'product')
        verbose_name_plural = "wishlist items"
        db_table = 'wishlist'

    def __str__(self):
        return f"{self.product.title} in {self.user.username}'s wishlist"

class Cart(models.Model):
    """Model for managing cart items."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'product')
        verbose_name_plural = "Cart Items"
        db_table = 'cart'

    def __str__(self):
        return f"{self.quantity} x {self.product.title} in {self.user.username}'s cart"

    def get_total_price(self):
        return self.product.price * self.quantity

    @classmethod
    def get_cart_total(cls, user):
        cart_items = cls.objects.filter(user=user, is_active=True)
        return sum(item.get_total_price() for item in cart_items)

class CartOrder(models.Model):
    """Model for managing cart orders."""
    order_id = ShortUUIDField(unique=True, length=10, max_length=20, prefix="ORD", alphabet="abcdefgh12345")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    address = models.TextField()
    status = models.CharField(
        max_length=50,
        choices=(
            ("Pending", "Pending"),
            ("Confirmed", "Confirmed"),
            ("Shipped", "Shipped"),
            ("Delivered", "Delivered"),
            ("Cancelled", "Cancelled"),
        ),
        default="Pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Cart Orders"
        db_table = 'cart_order'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"

    def get_total_items(self):
        total_items = self.items.aggregate(total=Sum('quantity'))['total'] or 0
        return total_items

    def get_order_summary(self):
        items = self.items.all()
        if not items:
            return "No items in order"
        return ", ".join([f"{item.quantity} x {item.product.title}" for item in items])

class CartOrderItem(models.Model):
    """Model for managing items in a cart order."""
    order = models.ForeignKey('CartOrder', on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.title} in Order {self.order.order_id}"

class Blog(models.Model):
    """Model for latest blogs."""
    bid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="blog", alphabet="abcdefgh12345")
    title = models.CharField(max_length=255)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blogs")
    content = models.TextField()
    cover_image = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "blogs"
        ordering = ['-created_at']
        db_table = 'blog'

    def __str__(self):
        return self.title

    def blog_image(self):
        """Display the blog image in the admin panel."""
        if self.cover_image and hasattr(self.cover_image, 'url'):
            return mark_safe(f'<img src="{self.cover_image.url}" width="50px" />')
        return "No Image Available"

class AboutSection(models.Model):
    """Model for the about section."""
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='about_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ContactFormSubmission(models.Model):
    """Model for contact form submissions."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} at {self.submitted_at}"


