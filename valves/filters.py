import django_filters
from .models import PartCode
from django.db.models import Q

class PartCodeFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = PartCode
        fields = [] # No direct field filtering, using custom search method

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(sap_code__icontains=value) |
            Q(oracle_code__icontains=value) |
            Q(description__icontains=value) |
            Q(part_number__icontains=value) |
            Q(manufacturer_co__icontains=value)
        )
