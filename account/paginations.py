from rest_framework.pagination import PageNumberPagination


class CustomResultsSetPagination(PageNumberPagination):
  page_query_param = "page"
  page_size_query_param = "page_size"
  max_page_size = 1000
