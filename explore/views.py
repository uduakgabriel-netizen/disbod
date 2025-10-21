from django.db.models import Q, Count, Avg
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from datetime import timedelta

from business.models import Business
from products.models import Product, ProductCategory, ProductView
from ratings.models import Rating
from explore.serializers import BusinessListSerializer, ProductListSerializer, ProductCategorySerializer
from explore.models import TrendingProductCache, FeaturedBusiness


class StandardPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


# ---------- Categories ----------
class CategoryListView(generics.ListAPIView):
    queryset = ProductCategory.objects.all().order_by('name')
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # return all categories


# ---------- Search businesses & products ----------
class ExploreSearchView(APIView):
    """
    Unified search endpoint:
    params: q, type=(business|product|both), category, country, region, city, sort
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        search_type = request.query_params.get('type', 'both')
        category = request.query_params.get('category')
        country = request.query_params.get('country')
        region = request.query_params.get('region')
        city = request.query_params.get('city')
        sort = request.query_params.get('sort')  # 'followers', 'rating', 'recent', 'relevance'

        results = {'businesses': [], 'products': []}

        if search_type in ('business', 'both'):
            bs_q = Business.objects.filter()
            # only business/premium, and suggested criteria optional removed; we allow searching all businesses
            bs_q = bs_q.filter()  # placeholder, no-op
            if q:
                bs_q = bs_q.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(owner__username__icontains=q))
            if category:
                bs_q = bs_q.filter(category__icontains=category)
            if country:
                bs_q = bs_q.filter(country__icontains=country)
            if region:
                bs_q = bs_q.filter(region__icontains=region)
            if city:
                bs_q = bs_q.filter(city__icontains=city)

            # sort
            if sort == 'followers':
                bs_q = bs_q.annotate(fcount=Count('owner__followers_set')).order_by('-owner__followers_count')
            elif sort == 'rating':
                bs_q = bs_q.annotate(avg=Avg('owner__received_ratings__stars')).order_by('-avg')
            elif sort == 'recent':
                bs_q = bs_q.order_by('-created_at')

            serializer = BusinessListSerializer(bs_q, many=True, context={'request': request})
            results['businesses'] = serializer.data

        if search_type in ('product', 'both'):
            p_q = Product.objects.select_related('category', 'category__business').all()
            if q:
                p_q = p_q.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q))
            if category:
                p_q = p_q.filter(category__name__icontains=category)
            if country:
                p_q = p_q.filter(category__business__country__icontains=country)
            if region:
                p_q = p_q.filter(category__business__region__icontains=region)
            if city:
                p_q = p_q.filter(category__business__city__icontains=city)

            if sort == 'views':
                # top by view count
                p_q = p_q.annotate(vcount=Count('views')).order_by('-vcount')
            elif sort == 'recent':
                p_q = p_q.order_by('-created_at')
            elif sort == 'price_asc':
                p_q = p_q.order_by('price')
            elif sort == 'price_desc':
                p_q = p_q.order_by('-price')

            paginator = StandardPagination()
            page = paginator.paginate_queryset(p_q, request)
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response({'businesses': results['businesses'], 'products': serializer.data})

        return Response(results)


# ---------- Suggested businesses ----------
class SuggestedBusinessView(generics.ListAPIView):
    """
    Suggest businesses based on:
     - followers_count >= 20 OR high rating OR featured by admin
     - optional location filters
    """
    serializer_class = BusinessListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagination

    def get_queryset(self):
        country = self.request.query_params.get('country')
        region = self.request.query_params.get('region')
        city = self.request.query_params.get('city')
        base = Business.objects.filter(owner__account_type__in=['business', 'premium'])
        # Suggested: followers >=20 OR avg rating >=4 OR Featured active
        base = base.annotate(avg_rating=Avg('owner__received_ratings__stars'))

        qs = base.filter(
            Q(owner__followers_count__gte=20) |
            Q(avg_rating__gte=4.0) |
            Q(featured__isnull=False)
        )

        if country:
            qs = qs.filter(country__icontains=country)
        if region:
            qs = qs.filter(region__icontains=region)
        if city:
            qs = qs.filter(city__icontains=city)

        # order by featured first, then followers_count, then rating
        qs = qs.annotate(is_featured=Count('featured')).order_by('-is_featured', '-owner__followers_count', '-avg_rating')
        return qs


# ---------- Trending products ----------
class TrendingProductsView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagination

    def get_queryset(self):
        # Trending score: weighted combination of recent views and recency
        # We'll approximate: count views in last 7 days and order by that + is_featured
        since_days = int(self.request.query_params.get('days', 7))
        since = timezone.now() - timedelta(days=since_days)

        qs = Product.objects.select_related('category', 'category__business').all()
        qs = qs.annotate(views_recent=Count('views', filter=Q(views__viewed_at__gte=since)))
        # boost featured
        qs = qs.annotate(score=models.F('views_recent') + models.Case(
            models.When(is_featured=True, then=models.Value(10)),
            default=models.Value(0),
            output_field=models.IntegerField()
        ))
        qs = qs.order_by('-score', '-created_at')
        return qs


# ---------- Top Rated Businesses ----------
class TopRatedBusinessesView(generics.ListAPIView):
    serializer_class = BusinessListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = Business.objects.annotate(avg=Avg('owner__received_ratings__stars')).order_by('-avg', '-owner__followers_count')
        return qs
