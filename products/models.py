from django.db import models
from django.utils.text import slugify

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price_inr = models.DecimalField(max_digits=10, decimal_places=2)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    category = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name