import django_filters
from django_filters import rest_framework as filters
from .models import *
from django.db.models import Q
class CityFilter(django_filters.FilterSet):
    city_name=django_filters.CharFilter(lookup_expr='icontains')
    city_id=django_filters.CharFilter(lookup_expr='iexact')
    class Meta:
        model = City
        fields = ['city_id', 'city_name']
        
class EmployeeFilter(django_filters.FilterSet):
    f_name=django_filters.CharFilter(lookup_expr='iexact')
    l_name=django_filters.CharFilter(lookup_expr='iexact')
    middle_name=django_filters.CharFilter(lookup_expr='iexact')
    branch_id=django_filters.CharFilter(lookup_expr='exact')
    job_title=django_filters.CharFilter(field_name='job_id__job_name', lookup_expr='icontains', label='Job Title')
    class Meta:
        models=Employee
        fields=['f_name','l_name','middle_name','job_title','branch_id']
        
class BranchFilter(django_filters.FilterSet):
    manager_name=django_filters.CharFilter(
        field_name='manager_id__f_name',
        lookup_expr='icontains',
        label='Manager Name'
    )
    branch_city = django_filters.CharFilter(
        field_name='city__id__city_name',
        lookup_expr='icontains',
        label='Branch City')
    class Meta:
        model=Branch
        fields=['manager_name', 'branch_city']

class ProductFilter(django_filters.FilterSet):
    product_name=django_filters.CharFilter(lookup_expr='icontains')
    category_name = filters.CharFilter(field_name='category_id__category_name', lookup_expr='iexact')
    min_price = filters.NumberFilter(field_name='sale_price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='sale_price', lookup_expr='lte')
    color = filters.CharFilter(method='filter_mobile_color')
    brand = filters.CharFilter(method='filter_mobile_brand')
    min_storage = filters.NumberFilter(method='filter_mobile_storage')
    max_storage = filters.NumberFilter(method='filter_mobile_storage')
    min_front_camera = filters.NumberFilter(method='filter_front_camera')
    max_front_camera = filters.NumberFilter(method='filter_front_camera')
    min_back_camera = filters.NumberFilter(method='filter_back_camera' )
    max_back_camera = filters.NumberFilter(method='filter_back_camera' )
    min_mobile_battery=filters.NumberFilter(method='filter_mobile_battery')
    max_mobile_battery=filters.NumberFilter(method='filter_mobile_battery')
    class Meta:
        model=Product
        fields=['product_name','min_price','max_price','category_name','color','brand','min_front_camera','min_back_camera','max_front_camera','max_back_camera','max_storage','min_storage']
    def filter_mobile_color(self, queryset, name, value):
        return queryset.filter(
            Q(category_id__category_name__iexact='phone') |
            Q(category_id__category_name__iexact='mobile'),
            phone_set__color_id__color_name__iexact=value
        )
    def filter_mobile_battery(self, queryset, name, value):
        return queryset.filter(
            Q(category_id__category_name__iexact='phone') |
            Q(category_id__category_name__iexact='mobile'),
            phone_set__battery__iexact=value
        )
    def filter_mobile_brand(self, queryset, name, value):
        return queryset.filter(
            Q(category_id__category_name__iexact='phone') |
            Q(category_id__category_name__iexact='mobile'),
            phone_set__brand_id__brand_name__iexact=value
        )
    def filter_mobile_storage(self, queryset, name, value):
        min_storage = self.data.get('min_storage')
        max_storage = self.data.get('max_storage')

        queryset = queryset.filter(
            Q(category_id__category_name__iexact='phone') |
            Q(category_id__category_name__iexact='mobile'),
        )
        storage_filters = Q()
        
        if min_storage:
            storage_filters &= Q(phone_set__storage__gte=min_storage)
            
        if max_storage:
            storage_filters &= Q(phone_set__storage__lte=max_storage)

        return queryset.filter(storage_filters)
    
    
    def filter_front_camera(self, queryset, name, value):
        min_fc = self.data.get('min_front_camera')
        max_fc = self.data.get('max_front_camera')
    
    
        queryset = queryset.filter( Q(category_id__category_name__iexact='phone') |
        Q(category_id__category_name__iexact='mobile'))
        
        fc = Q()
        if min_fc:
            fc &= Q(phone_set__camera_id__front_camera__gte=min_fc)
        if max_fc:
            fc &= Q(phone_set__camera_id__front_camera__lte=max_fc)
            
        return queryset.filter(fc)

    def filter_back_camera(self, queryset, name, value):
        min_bc = self.data.get('min_back_camera')
        max_bc = self.data.get('max_back_camera')
        
        # Only apply to mobile category
        queryset = queryset.filter( Q(category_id__category_name__iexact='phone') |
        Q(category_id__category_name__iexact='mobile'),)
        
        bc = Q()
        if min_bc:
            bc &= Q(phone_set__camera_id__back_camera__gte=min_bc)
        if max_bc:
            bc &= Q(phone_set__camera_id__back_camera__lte=max_bc)
            
        return queryset.filter(bc)
    
    
### for products log movement filter 
# filters.py
import django_filters
from .models import ProductTransaction
from django.db.models import Q

class ProductTransactionFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='date_of_transaction', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date_of_transaction', lookup_expr='lte')
    branch = django_filters.CharFilter(field_name='branch_id__location', lookup_expr='icontains')
    movement_type = django_filters.ChoiceFilter(choices=ProductTransaction.MOVEMENT_TYPE_CHOICES)
    product = django_filters.NumberFilter(method='filter_by_product')
    
    class Meta:
        model = ProductTransaction
        fields = ['date_from', 'date_to', 'branch', 'movement_type', 'is_done']
    
    def filter_by_product(self, queryset, name, value):
        return queryset.filter(
            Q(transportedproducts_set__product_id=value)
        ).distinct()
    
    
## request log WAREHOUSE MANAGER 
# filters.py
import django_filters
from .models import BranchOrder
from django.db.models import Q

class BranchOrderFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='date_of_order', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date_of_order', lookup_expr='lte')
    branch = django_filters.CharFilter(field_name='branch_id__location', lookup_expr='icontains')
    city = django_filters.CharFilter(field_name='branch_id__city_id__city_name', lookup_expr='icontains')
    status = django_filters.ChoiceFilter(
        method='filter_by_status',
        choices=[('P', 'Pending'), ('S', 'Approved'), ('R', 'Rejected')]
    )
    product = django_filters.NumberFilter(method='filter_by_product')

    class Meta:
        model = BranchOrder
        fields = ['date_from', 'date_to', 'branch', 'city', 'status', 'product']

    def filter_by_status(self, queryset, name, value):
        return queryset.filter(
            Q(requestedproducts_set__status=value)
        ).distinct()

    def filter_by_product(self, queryset, name, value):
        return queryset.filter(
            Q(requestedproducts_set__product_id=value)
        ).distinct()