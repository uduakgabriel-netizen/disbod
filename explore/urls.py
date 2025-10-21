from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='explore-categories'),
    path('search/', views.ExploreSearchView.as_view(), name='explore-search'),
    path('suggested/', views.SuggestedBusinessView.as_view(), name='explore-suggested'),
    path('trending-products/', views.TrendingProductsView.as_view(), name='explore-trending'),
    path('top-businesses/', views.TopRatedBusinessesView.as_view(), name='explore-top-businesses'),
]
