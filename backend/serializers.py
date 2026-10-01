from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import (
    Category,
    DietaryRestriction,
    Establishment,
    Favorite,
    Product,
    UserProfile,
)

User = get_user_model()


class DietaryRestrictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietaryRestriction
        fields = ["id", "name", "slug", "description"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    declared_compatible_with = DietaryRestrictionSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "category",
            "ingredients",
            "allergens",
            "cross_contamination_info",
            "declared_compatible_with",
        ]


class EstablishmentSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = Establishment
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "address",
            "latitude",
            "longitude",
            "phone",
            "hours",
            "products",
            "distance_km",
        ]

    def get_products(self, establishment):
        products = getattr(establishment, "matching_products", None)
        if products is None:
            products = establishment.products.filter(is_active=True).select_related(
                "category"
            ).prefetch_related("declared_compatible_with")
        return ProductSerializer(products, many=True).data

    def get_distance_km(self, establishment):
        distance = getattr(establishment, "distance_km", None)
        return round(distance, 2) if distance is not None else None


class UserProfileSerializer(serializers.ModelSerializer):
    restrictions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=DietaryRestriction.objects.all(), required=False
    )

    class Meta:
        model = UserProfile
        fields = ["restrictions"]


class UserSerializer(serializers.ModelSerializer):
    restrictions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "restrictions"]

    def get_restrictions(self, user):
        return DietaryRestrictionSerializer(
            user.profile.restrictions.all(), many=True
        ).data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, validators=[validate_password], trim_whitespace=False
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    establishment = EstablishmentSerializer(read_only=True)
    establishment_id = serializers.PrimaryKeyRelatedField(
        source="establishment",
        queryset=Establishment.objects.filter(is_active=True),
        write_only=True,
    )

    class Meta:
        model = Favorite
        fields = ["id", "establishment", "establishment_id", "created_at"]
        read_only_fields = ["id", "created_at"]


class SearchParamsSerializer(serializers.Serializer):
    q = serializers.CharField(required=False, allow_blank=True, max_length=120)
    category = serializers.SlugField(required=False)
    restrictions = serializers.ListField(
        child=serializers.SlugField(), required=False, allow_empty=False
    )
    latitude = serializers.FloatField(
        required=False, min_value=-90, max_value=90
    )
    longitude = serializers.FloatField(
        required=False, min_value=-180, max_value=180
    )
    radius_km = serializers.FloatField(
        required=False, min_value=0.1, max_value=100
    )

    def validate(self, attrs):
        if ("latitude" in attrs) != ("longitude" in attrs):
            raise serializers.ValidationError(
                "Envía latitude y longitude juntos para buscar por ubicación."
            )
        if "radius_km" in attrs and "latitude" not in attrs:
            raise serializers.ValidationError(
                "Envía latitude y longitude para filtrar por radio."
            )
        if "category" in attrs and not Category.objects.filter(
            slug=attrs["category"]
        ).exists():
            raise serializers.ValidationError(
                {"category": "La categoría indicada no existe."}
            )
        if "restrictions" in attrs:
            requested = set(attrs["restrictions"])
            found = set(
                DietaryRestriction.objects.filter(slug__in=requested).values_list(
                    "slug", flat=True
                )
            )
            if found != requested:
                raise serializers.ValidationError(
                    {"restrictions": "Una o más restricciones no existen."}
                )
        return attrs

