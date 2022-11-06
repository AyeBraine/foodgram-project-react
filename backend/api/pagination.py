from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class AdjustablePagination(PageNumberPagination):
    page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
    page_size_query_param = 'limit'
