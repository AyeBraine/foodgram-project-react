# isort: skip_file
from django.urls import include, path
from rest_framework import routers

from api.utils import CartPDFExportView
from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import UserViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet)

urlpatterns = [
    path('recipes/download_shopping_cart/', CartPDFExportView.as_view(),
         name='download_shopping_cart'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
