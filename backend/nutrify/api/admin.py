from django.contrib import admin

from .models import Category, DietaryRestriction, Establishment, Favorite, Product, UserProfile


@admin.register(DietaryRestriction)
class DietaryRestrictionAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    filter_horizontal = ["declared_compatible_with"]


@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ["name", "address", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "address"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [ProductInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "establishment", "category", "is_active"]
    list_filter = ["is_active", "category"]
    search_fields = ["name", "establishment__name"]
    filter_horizontal = ["declared_compatible_with"]


admin.site.register(UserProfile)
admin.site.register(Favorite)

