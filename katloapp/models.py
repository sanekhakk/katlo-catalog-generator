from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Business(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='business', null=True, blank=True)
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(blank=True)
    whatsapp_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100, blank=True)
    native_place = models.CharField(max_length=100, blank=True)
    public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or 'business'
            slug = base
            i = 1
            while Business.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_public_url(self):
        return reverse('katloapp:public_catalog', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

class Product(models.Model):
    business = models.ForeignKey(Business, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    sku = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.business.name}"
