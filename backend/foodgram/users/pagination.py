from rest_framework.pagination import PageNumberPagination


class QueryPageSizePagination(PageNumberPagination):
    page_size_query_param = 'limit'
