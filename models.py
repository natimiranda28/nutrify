from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q



#aca se definen los datos, restricciones alimentarias, perfiles

class restricciones_dietas(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    restrictions = models.ManyToManyField(
        restricciones_dietas, blank=True, related_name="profiles"
    )

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Establecimientos(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    phone = models.CharField(max_length=40, blank=True)
    hours = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(latitude__isnull=True, longitude__isnull=True)
                    | Q(latitude__isnull=False, longitude__isnull=False)
                ),
                name="establishment_coordinates_paired",
            )
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    establishment = models.ForeignKey(
        Establecimientos, on_delete=models.CASCADE, related_name="products"
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    name = models.CharField(max_length=160)
    descripcion = models.TextField(blank=True)
    ingredientes = models.TextField(blank=True)
    alergias = models.TextField(blank=True)
    #cross_contamination_info = models.TextField(blank=True)
    declared_compatible_with = models.ManyToManyField(
        restricciones_dietas, blank=True, related_name="declared_compatible_products"
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} — {self.establishment.name}"




    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "establishment"], name="unique_user_favorite"
            )
        ]

