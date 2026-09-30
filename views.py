from math import asin, cos, radians, sin, sqrt #me lo sugirio asi de una la consola, wow

from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action

from .models import (
    Category,
    DietaryRestriction,
    Establishment,
    Favorite,
    Product,
    UserProfile,
)
from .serializers import (
    CategorySerializer,
    DietaryRestrictionSerializer,
    EstablishmentSerializer,
    FavoriteSerializer,
    RegisterSerializer,
    SearchParamsSerializer,
    UserProfileSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class CurrentProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(UserProfile, user=self.request.user)


class DietaryRestrictionViewSet(ReadOnlyModelViewSet):
    queryset = DietaryRestriction.objects.all()
    serializer_class = DietaryRestrictionSerializer


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


def parse_restrictions(query_params):
    values = query_params.getlist("restrictions")
    return sorted(
        {
            slug.strip()
            for value in values
            for slug in value.split(",")
            if slug.strip()
        }
    )


def haversine_km(latitude, longitude, other_latitude, other_longitude):
    earth_radius_km = 6371.0088
    latitude_delta = radians(other_latitude - latitude)
    longitude_delta = radians(other_longitude - longitude)
    value = (
        sin(latitude_delta / 2) ** 2
        + cos(radians(latitude))
        * cos(radians(other_latitude))
        * sin(longitude_delta / 2) ** 2
    )
    return 2 * earth_radius_km * asin(sqrt(value))


class EstablishmentViewSet(ReadOnlyModelViewSet):
    serializer_class = EstablishmentSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return (
            Establishment.objects.filter(is_active=True)
            .prefetch_related(
                Prefetch(
                    "products",
                    queryset=Product.objects.filter(is_active=True)
                    .select_related("category")
                    .prefetch_related("declared_compatible_with"),
                )
            )
        )

    @action(detail=False, methods=["get"])
    def search(self, request):
        raw_params = {"q": request.query_params.get("q", "")}
        for field in ("category", "latitude", "longitude", "radius_km"):
            value = request.query_params.get(field)
            if value is not None:
                raw_params[field] = value
        restrictions = parse_restrictions(request.query_params)
        if restrictions:
            raw_params["restrictions"] = restrictions
        params = SearchParamsSerializer(data=raw_params)
        params.is_valid(raise_exception=True)
        filters = params.validated_data

        products = Product.objects.filter(
            is_active=True, establishment__is_active=True
        )
        if "category" in filters:
            products = products.filter(category__slug=filters["category"])
        restrictions = filters.get("restrictions", [])
        if restrictions:
            products = (
                products.filter(
                    declared_compatible_with__slug__in=restrictions
                )
                .annotate(
                    matched_restrictions=Count(
                        "declared_compatible_with", distinct=True
                    )
                )
                .filter(matched_restrictions=len(restrictions))
            )

        query = filters.get("q", "").strip()
        matching_place_ids = products.values_list("establishment_id", flat=True)
        establishments = Establishment.objects.filter(is_active=True)
        if query:
            establishments = establishments.filter(
                Q(name__icontains=query) | Q(pk__in=matching_place_ids)
            )
        elif restrictions or "category" in filters:
            establishments = establishments.filter(pk__in=matching_place_ids)

        filtered_products = products.select_related("category").prefetch_related(
            "declared_compatible_with"
        )
        establishments = establishments.prefetch_related(
            Prefetch("products", queryset=filtered_products, to_attr="matching_products")
        )

        if "latitude" in filters:
            latitude = filters["latitude"]
            longitude = filters["longitude"]
            radius = filters.get("radius_km", 10)
            latitude_delta = radius / 110.574
            longitude_delta = min(
                radius / (111.320 * max(abs(cos(radians(latitude))), 0.01)), 180
            )
            establishments = establishments.filter(
                latitude__gte=max(latitude - latitude_delta, -90),
                latitude__lte=min(latitude + latitude_delta, 90),
                longitude__gte=max(longitude - longitude_delta, -180),
                longitude__lte=min(longitude + longitude_delta, 180),
            )

        results = list(establishments.distinct())
        if "latitude" in filters:
            results_with_distance = []
            for establishment in results:
                distance = haversine_km(
                    latitude,
                    longitude,
                    float(establishment.latitude),
                    float(establishment.longitude),
                )
                if distance <= radius:
                    establishment.distance_km = distance
                    results_with_distance.append(establishment)
            results = sorted(results_with_distance, key=lambda item: item.distance_km)

        page = self.paginate_queryset(results)
        if page is not None:
            data = self.get_serializer(page, many=True).data
            return self.get_paginated_response(data)
        return Response(self.get_serializer(results, many=True).data)


class FavoriteViewSet(ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related(
            "establishment"
        ).prefetch_related(
            "establishment__products__category",
            "establishment__products__declared_compatible_with",
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
