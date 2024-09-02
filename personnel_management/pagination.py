from rest_framework.pagination import LimitOffsetPagination


class EmployeeListPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 1000
    limit_query_param = 'employees'
    offset_query_param = 'offset'
