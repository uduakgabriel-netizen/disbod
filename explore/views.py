from django.db.models import Q, Count, Avg, F, Case, When, Value, IntegerField
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from datetime import timedelta

from accounts.models import User
from accounts.serializers import UserSerializer
from business.models import Business
from products.models import Product, ProductCategory
from ratings.models import Rating
from explore.serializers import (
    BusinessListSerializer,
    ProductListSerializer,
    ProductCategorySerializer,
)
from explore.models import TrendingProductCache, FeaturedBusiness


# ---------- Pagination ----------
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
        sort = request.query_params.get('sort')  # 'followers', 'rating', 'recent', 'views', 'price_asc', 'price_desc'

        results = {'businesses': [], 'products': []}

        # ----- Business search -----
        if search_type in ('business', 'both'):
            bs_q = Business.objects.all()

            if q:
                bs_q = bs_q.filter(
                    Q(name__icontains=q)
                    | Q(description__icontains=q)
                    | Q(owner__username__icontains=q)
                )
            if category:
                bs_q = bs_q.filter(category__icontains=category)
            if country:
                bs_q = bs_q.filter(country__icontains=country)
            if region:
                bs_q = bs_q.filter(region__icontains=region)
            if city:
                bs_q = bs_q.filter(city__icontains=city)

            # Sorting
            if sort == 'followers':
                bs_q = bs_q.annotate(fcount=Count('owner__followers')).order_by('-fcount')
            elif sort == 'rating':
                bs_q = bs_q.annotate(avg=Avg('owner__received_ratings__stars')).order_by('-avg')
            elif sort == 'recent':
                bs_q = bs_q.order_by('-created_at')

            serializer = BusinessListSerializer(bs_q, many=True, context={'request': request})
            results['businesses'] = serializer.data

        # ----- Product search -----
        if search_type in ('product', 'both'):
            p_q = Product.objects.select_related('category', 'category__business').all()

            if q:
                p_q = p_q.filter(
                    Q(name__icontains=q)
                    | Q(description__icontains=q)
                    | Q(category__name__icontains=q)
                )
            if category:
                p_q = p_q.filter(category__name__icontains=category)
            if country:
                p_q = p_q.filter(category__business__country__icontains=country)
            if region:
                p_q = p_q.filter(category__business__region__icontains=region)
            if city:
                p_q = p_q.filter(category__business__city__icontains=city)

            # Sorting
            if sort == 'views':
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
            return paginator.get_paginated_response({
                'businesses': results['businesses'],
                'products': serializer.data,
            })

        return Response(results)


# ---------- Suggested businesses ----------
class SuggestedBusinessView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = User.objects.filter(account_type='business')

        # Safely check if the User model has a followers relationship
        if hasattr(User, 'followers') or 'followers' in [f.name for f in User._meta.get_fields()]:
            # If followers relation exists, count them
            qs = qs.annotate(followers_total=Count('followers')).order_by('-followers_total')[:10]
        else:
            # If no followers field, just return latest businesses
            qs = qs.order_by('-date_joined')[:10]

        return qs


            


# ---------- Trending products ----------
class TrendingProductsView(generics.ListAPIView):
    """
    Trending products are scored using:
      - number of views in the recent period (days query param, default 7)
      - a small boost for products marked is_featured
    Returns paginated product list ordered by score then recency.
    """
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagination

    def get_queryset(self):
        # number of days to consider for "recent" — default 7
        try:
            since_days = int(self.request.query_params.get('days', 7))
        except (TypeError, ValueError):
            since_days = 7
        since = timezone.now() - timedelta(days=since_days)

        qs = Product.objects.select_related('category', 'category__business').all()
        # count recent views, boost featured products
        qs = qs.annotate(
            views_recent=Count('views', filter=Q(views__viewed_at__gte=since))
        ).annotate(
            score=F('views_recent') + Case(
                When(is_featured=True, then=Value(10)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('-score', '-created_at')

        return qs


# ---------- Top Rated Businesses ----------
class TopRatedBusinessesView(generics.ListAPIView):
    """
    List businesses ordered by average rating then follower count (if available).
    Uses Business model and BusinessListSerializer. Paginated.
    """
    serializer_class = BusinessListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagination

    def get_queryset(self):
        # Annotate businesses with avg rating (from ratings on the owner) and follower count if relation exists.
        qs = Business.objects.all().select_related('owner')

        # annotate average rating (ratings attached to the owner)
        qs = qs.annotate(avg_rating=Avg('owner__received_ratings__stars'))

        # try to annotate follower count from a related name; safe fallback if relation/mapping differs
        # common related names used earlier: 'followers', 'followers_set', 'followers_user', 'followers_set'
        follower_rel_candidates = [
            'owner__followers',        # e.g. Follow model FK->user: related_name='followers'
            'owner__followers_set',    # django default when related_name omitted
            'owner__followers_user',   # other possible names used earlier in your models
            'owner__followers_set'     # duplicate safe entry
        ]

        # We'll try to annotate using a valid relation name. If none exist, fallback to 0.
        annotated = False
        for rel in follower_rel_candidates:
            try:
                qs_test = qs.annotate(fcount=Count(rel))
                # executing a cheap queryset slice will reveal if DB accepts the annotation
                qs_test[:1]
                qs = qs.annotate(followers_count=Count(rel))
                annotated = True
                break
            except Exception:
                continue

        if not annotated:
            # no follower relation found — set followers_count to 0 for ordering via a Value
            qs = qs.annotate(followers_count=Value(0, output_field=IntegerField()))

        # order by avg_rating desc then followers_count desc then recently created
        qs = qs.order_by('-avg_rating', '-followers_count', '-created_at')
        return qs
