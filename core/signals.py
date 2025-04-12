from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Offer, Product
from django.utils.timezone import now

@receiver(post_save, sender=Offer)
def update_product_price_on_offer_create_or_update(sender, instance, **kwargs):
    """
    Update product price when an offer is created or updated.
    """
    product = instance.product
    current_time = now()  # Get the current time
    
    # Check if the offer is active
    if instance.start_date <= current_time <= instance.end_date:
        # Calculate the discounted price
        discount = (product.price * instance.discount_percentage) / 100
        discounted_price = round(product.price - discount, 2)
        
        # Update the product price only if the offer is active
        if product.price != discounted_price:
            product.price = discounted_price
            product.save()
    else:
        # If the offer is expired, reset the product price to the original price
        product.price = product.get_old_price()  # Restore the original price
        product.save()


@receiver(post_delete, sender=Offer)
def reset_product_price_on_offer_delete(sender, instance, **kwargs):
    """
    Reset product price when an offer is deleted.
    """
    product = instance.product
    # Check if there are any active offers left
    active_offer = product.offers.filter(start_date__lte=now(), end_date__gte=now()).first()
    
    if not active_offer:
        # No active offer, reset to the original price
        product.price = product.get_old_price()
        product.save()
