from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        # This fixes the plural spelling in the admin panel (so it doesn't say "Categorys")
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    # The ForeignKey links each product to a specific category
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    # DecimalField is best practice for handling money/prices securely
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # This requires the Pillow library we installed earlier
    image = models.ImageField(upload_to='images/products/', blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
