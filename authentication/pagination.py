from rest_framework.pagination import LimitOffsetPagination


class ApprovalListPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 1000
    limit_query_param = 'requests'
    offset_query_param = 'offset'