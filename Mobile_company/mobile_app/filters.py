import django_filters
from django_filters import rest_framework as filters
from .models import *
from django.db.models import Q,Sum,F,Value,Func
from django.db.models.functions import Replace,Lower
class CityFilter(django_filters.FilterSet):
    city_name=django_filters.CharFilter(lookup_expr='icontains')
    city_id=django_filters.CharFilter(lookup_expr='iexact')
    class Meta:
        model = City
        fields = ['city_id', 'city_name']
        
class EmployeeFilter(django_filters.FilterSet):
    f_name=django_filters.CharFilter(lookup_expr='icontains')
    l_name=django_filters.CharFilter(lookup_expr='iexact')
    middle_name=django_filters.CharFilter(lookup_expr='iexact')
    branch_location=django_filters.CharFilter(field_name='branch_id__location',lookup_expr='exact')
    job_title=django_filters.CharFilter(field_name='job_id__job_name', lookup_expr='icontains', label='Job Title')
    class Meta:
        model=Employee
        fields=['f_name','l_name','middle_name','job_title','branch_id']
        
class BranchFilter(django_filters.FilterSet):
    manager_name=django_filters.CharFilter(
        field_name='manager_id__f_name',
        lookup_expr='icontains',
        label='Manager Name'
    )
    branch_city = django_filters.CharFilter(
        field_name='city_id__city_name',
        lookup_expr='icontains',
        label='Branch City')
    location=django_filters.CharFilter(
        field_name='location',
        lookup_expr='icontains',
        label='location')
    class Meta:
        model=Branch
        fields=['manager_name', 'branch_city','location']
        
class ProductFilter(django_filters.FilterSet):
    product_name=django_filters.CharFilter(method='filter_product_name')
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
    min_battery=filters.NumberFilter(method='filter_mobile_battery')
    max_battery=filters.NumberFilter(method='filter_mobile_battery')
    class Meta:
        model=Product
        fields=['product_name','min_price','max_price','category_name','color','brand','min_front_camera','min_back_camera','max_front_camera','max_back_camera','max_storage','min_storage']
    def filter_product_name(self, queryset, name, value):
        
        normalized_value = value.replace(" ", "").lower()

    
        return queryset.annotate(
            normalized_name=Lower(Replace(F('product_name'), Value(" "), Value("")))
        ).filter(normalized_name__icontains=normalized_value)
    def filter_mobile_color(self, queryset, name, value):
        return queryset.filter(
            Q(category_id__category_name__iexact='phone') |
            Q(category_id__category_name__iexact='mobile'),
            phones__color_id__color_name__iexact=value  
        )

    def filter_mobile_battery(self, queryset, name, value):
        min_battery = self.data.get('min_battery')
        max_battery = self.data.get('max_battery')

        queryset = queryset.filter(
            Q(category_id__category_name__iexact='phone') |
            Q(category_id__category_name__iexact='mobile'),
        )
        battery_filters = Q()
        
        if min_battery:
            battery_filters &= Q(phones__battery__gte=min_battery)  # Changed
            
        if max_battery:
            battery_filters &= Q(phones__battery__lte=max_battery)  # Changed

        return queryset.filter(battery_filters)

    def filter_mobile_brand(self, queryset, name, value):
        return queryset.filter(
            Q(category_id__category_name__iexact='phone') |
            Q(category_id__category_name__iexact='mobile'),
            phones__brand_id__brand_name__iexact=value  
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
            storage_filters &= Q(phones__storage__gte=min_storage)  
            
        if max_storage:
            storage_filters &= Q(phones__storage__lte=max_storage)  

        return queryset.filter(storage_filters)
    
    def filter_front_camera(self, queryset, name, value):
        min_fc = self.data.get('min_front_camera')
        max_fc = self.data.get('max_front_camera')
    
        queryset = queryset.filter(
            Q(category_id__category_name__iexact='phone') |
            Q(category_id__category_name__iexact='mobile')
        )
        
        fc = Q()
        if min_fc:
            fc &= Q(phones__camera_id__front_camera__gte=min_fc)  
        if max_fc:
            fc &= Q(phones__camera_id__front_camera__lte=max_fc) 
            
        return queryset.filter(fc)

    def filter_back_camera(self, queryset, name, value):
        min_bc = self.data.get('min_back_camera')
        max_bc = self.data.get('max_back_camera')
        
        queryset = queryset.filter(
            Q(category_id__category_name__iexact='phone') |
            Q(category_id__category_name__iexact='mobile')
        )
        
        bc = Q()
        if min_bc:
            bc &= Q(phones__camera_id__back_camera__gte=min_bc)  
        if max_bc:
            bc &= Q(phones__camera_id__back_camera__lte=max_bc)
            
        return queryset.filter(bc)
    
class BranchProductFilter(django_filters.FilterSet):
    # Price range filters
    min_price = django_filters.NumberFilter(
        field_name='product_id__sale_price', 
        lookup_expr='gte',
        label='Minimum Price'
    )
    max_price = django_filters.NumberFilter(
        field_name='product_id__sale_price', 
        lookup_expr='lte',
        label='Maximum Price'
    )
    
    # Category filter
    category = django_filters.NumberFilter(
        field_name='product_id__category_id',
        lookup_expr='exact'
    )

    class Meta:
        model = BranchProducts
        fields = {
            'product_id__product_name': ['icontains'],
        }
    


class ProductTransactionFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(
        field_name='date_of_transaction', 
        lookup_expr='gte',
        label='From Date'
    )
    date_to = django_filters.DateFilter(
        field_name='date_of_transaction', 
        lookup_expr='lte',
        label='To Date'
    )
    branch = django_filters.CharFilter(
        field_name='branch_id__location', 
        lookup_expr='icontains',
        label='Branch Location'
    )
    movement_type = django_filters.ChoiceFilter(
        choices=ProductTransaction.MOVEMENT_TYPE_CHOICES,
        label='Movement Type'
    )
    product = django_filters.NumberFilter(
        method='filter_by_product',
        label='Product ID'
    )
    
    class Meta:
        model = ProductTransaction
        fields = []
    
    def filter_by_product(self, queryset, name, value):
        return queryset.filter(
            transportedproducts__product_id=value
        ).distinct()


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
        


class BranchOrderRequestsFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(
        field_name='date_of_order', 
        lookup_expr='gte',
        label='Orders from this date (YYYY-MM-DD)'
    )
    date_to = django_filters.DateFilter(
        field_name='date_of_order', 
        lookup_expr='lte',
        label='Orders until this date (YYYY-MM-DD)'
    )
    branch_location = django_filters.CharFilter(
        method='filter_branch_location',
        label='Branch location contains'
    )
    product_name = django_filters.CharFilter(
        method='filter_product_name',
        label='Product name contains'
    )

    class Meta:
        model = BranchOrder
        fields = []

    def filter_product_name(self, queryset, name, value):
        return queryset.filter(
            requestedproducts_set__product_id__product_name__icontains=value
        ).distinct()

    def filter_branch_location(self, queryset, name, value):
        return queryset.filter(
            branch_id__location__icontains=value
        )

class CustomerFilter(filters.FilterSet):
    full_name = filters.CharFilter(method='filter_by_full_name')
    national_num = filters.CharFilter(field_name='national_num', lookup_expr='exact')

    class Meta:
        model = Customer
        fields = ['full_name', 'national_num']

    def filter_by_full_name(self, queryset, name, value):
        # Normalize whitespace and case
        value = value.strip().lower()
        return queryset.filter(
            first_name__isnull=False,
            middle_name__isnull=False,
            last_name__isnull=False
        ).filter(
            first_name__iregex=r'^' + value.split()[0] + '$',
            middle_name__iregex=r'^' + value.split()[1] + '$',
            last_name__iregex=r'^' + value.split()[2] + '$'
        )

        
        
### sales manager serializers 
