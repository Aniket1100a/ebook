from django.contrib import admin
from django.utils.safestring import mark_safe
from core.models import (
    Category, Vendor, Product, ProductImage, Purchase, Rental,
    Cart, Wishlist, Offer, Blog, CartOrder, CartOrderItem, Billboard, AboutSection, ContactFormSubmission, Library
)

# Inline admin for Product images
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text']

# Admin for Product with inline ProductImage
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'vendor', 'price', 'is_featured', 'is_popular', 'product_image']
    list_filter = ['vendor', 'category', 'is_featured', 'is_popular', 'author']
    search_fields = ['title', 'author__name', 'description', 'category__title']
    inlines = [ProductImageInline]
    list_editable = ['is_featured', 'is_popular']
    actions = ['mark_as_popular', 'unmark_as_popular']

    def product_image(self, obj):
        if obj.cover_image and hasattr(obj.cover_image, 'url'):
            return mark_safe(f'<img src="{obj.cover_image.url}" width="50px" />')
        return "No Image Available"
    product_image.short_description = "Cover Image"

    @admin.action(description="Mark selected books as Popular")
    def mark_as_popular(self, request, queryset):
        queryset.update(is_popular=True)
        self.message_user(request, "Selected books marked as popular.")

    @admin.action(description="Unmark selected books as Popular")
    def unmark_as_popular(self, request, queryset):
        queryset.update(is_popular=False)
        self.message_user(request, "Selected books unmarked as popular.")

@admin.register(Billboard)
class BillboardAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    search_fields = ('title',)
    list_filter = ('is_active',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category_image')
    list_filter = ('title',)
    search_fields = ('title',)

    def category_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return mark_safe(f'<img src="{obj.image.url}" width="50px" />')
        return "No Image Available"
    category_image.short_description = "Image"

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['title', 'email', 'phone_number', 'user', 'vendor_image']
    search_fields = ['title', 'email', 'phone_number', 'user__username']
    list_filter = ['user']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['title']

    def vendor_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return mark_safe(f'<img src="{obj.image.url}" width="50px" />')
        return "No Image Available"
    vendor_image.short_description = "Image"

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'product', 'discount_percentage', 'start_date', 'end_date', 'is_active']
    search_fields = ['title', 'product__title']
    list_filter = ['start_date', 'end_date', 'discount_percentage']
    ordering = ['-start_date']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product']
    search_fields = ['user__username', 'product__title']
    list_filter = ['user']
    ordering = ['user']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity']
    search_fields = ['user__username', 'product__title']
    list_filter = ['user']
    ordering = ['user']

class CartOrderItemInline(admin.TabularInline):
    model = CartOrderItem
    extra = 0
    readonly_fields = ['get_total_price']
    fields = ['product', 'quantity', 'price', 'get_total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = "Total Price"

@admin.register(CartOrder)
class CartOrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'user__username', 'address']
    ordering = ['-created_at']
    inlines = [CartOrderItemInline]
    readonly_fields = ['get_total_items']

    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = "Total Items"

@admin.register(CartOrderItem)
class CartOrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'get_total_price']
    search_fields = ['order__order_id', 'product__title']
    list_filter = ['order']
    readonly_fields = ['get_total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = "Total Price"

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'purchased_at']
    search_fields = ['user__username', 'product__title']
    list_filter = ['purchased_at']
    ordering = ['-purchased_at']

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rented_at', 'expires_at', 'is_active']
    search_fields = ['user__username', 'product__title']
    list_filter = ['rented_at', 'expires_at']
    ordering = ['-rented_at']

    def is_active(self, obj):
        return obj.is_active()
    is_active.boolean = True
    is_active.short_description = "Active Rental"

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'blog_image']
    search_fields = ['title', 'content', 'author__username']
    list_filter = ['author', 'created_at']
    ordering = ['-created_at']
    readonly_fields = ['blog_image']

    def blog_image(self, obj):
        if obj.cover_image and hasattr(obj.cover_image, 'url'):
            return mark_safe(f'<img src="{obj.cover_image.url}" width="50px" />')
        return "No Image Available"
    blog_image.short_description = "Cover Image"

@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)

@admin.register(ContactFormSubmission)
class ContactFormSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'submitted_at')
    search_fields = ('name', 'email', 'message')
    list_filter = ('submitted_at',)

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'added_at')
    list_filter = ('user', 'added_at')
    search_fields = ('user__username', 'book__title')
    ordering = ('-added_at',)
