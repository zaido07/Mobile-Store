from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Sum,F
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class AccessoriesTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessoriesType
        fields = '__all__'

class AccessoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accessories
        fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'

class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = '__all__'

class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = '__all__'


from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = [
            'customer_id',
            'full_name',
            'first_name',
            'middle_name',
            'last_name',
            'national_num',
            'phone_num',
            'gender',
            'date_created'
        ]
        read_only_fields = ['customer_id', 'date_created']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.middle_name} {obj.last_name}"

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'

class SoldProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoldProduct
        fields = '__all__'

class BranchOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchOrder
        fields = '__all__'

class RequestedProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestedProducts
        fields = '__all__'

class ProductTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTransaction
        fields = '__all__'

class TransportedProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportedProducts
        fields = '__all__'
        
    
    from rest_framework import serializers
### make sale 

class CustomerSearchSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['customer_id', 'full_name', 'national_num']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.middle_name} {obj.last_name}"
    
    
class ProductItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)
    
class MakeSaleSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(required=True, min_value=1)
    products = serializers.ListField(
        child=ProductItemSerializer(),
        min_length=1
    )
    
    
    



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'is_staff': self.user.is_staff,
            'username': self.user.username
        })
        return data
    
    
class BranchOrderLogSerializer(serializers.ModelSerializer):
    branch = serializers.CharField(source='branch_id.location')
    total_products = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = BranchOrder
        fields = ['order_id', 'date_of_order', 'branch', 'total_products', 'status']
    
    def get_total_products(self, obj):
        return obj.requestedproducts_set.count()
    
    def get_status(self, obj):
        return "Completed" if obj.is_done else "Pending"

class RequestedProductsDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name')
    product_category = serializers.CharField(source='product_id.category_id.category_name')
    status_display = serializers.CharField(source='get_status_display')
    
    class Meta:
        model = RequestedProducts
        fields = ['product_name', 'product_category', 'quantity', 'status', 'status_display']
        
        
        
        

class SoldProductsLogSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source='branch_id.location')
    branch_city = serializers.CharField(source='branch_id.city_id.city_name')
    total_products = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Purchase
        fields = ['purchase_id', 'customer_name', 'branch_name', 'branch_city', 
                'date_of_purchase', 'total_products', 'total_amount']

    def get_customer_name(self, obj):
        return f"{obj.customer_id.first_name} {obj.customer_id.middle_name} {obj.customer_id.last_name}"

    def get_total_products(self, obj):
        return obj.soldproduct_set.aggregate(total=Sum('quantity'))['total'] or 0

    def get_total_amount(self, obj):
        return obj.soldproduct_set.aggregate(
            total=Sum(F('selling_price') * F('quantity'))
        )['total'] or 0

class SoldProductsDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name')
    product_category = serializers.CharField(source='product_id.category_id.category_name')
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = SoldProduct
        fields = ['product_name', 'product_category', 'quantity', 
                'selling_price', 'total_price']

    def get_total_price(self, obj):
        return obj.quantity * obj.selling_price
    
    
    
    
    ### add customer sales manager 

class AddCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'first_name',
            'middle_name', 
            'last_name',
            'national_num',
            'phone_num',
            'gender'
        ]
        extra_kwargs = {
            'national_num': {'required': True},
            'phone_num': {'required': True}
        }
        
        
        
        
from rest_framework import serializers
from .models import Customer, Purchase, SoldProduct

class CustomerSaleSerializer(serializers.ModelSerializer):
    total_spent = serializers.SerializerMethodField()
    total_products = serializers.SerializerMethodField()
    
    class Meta:
        model = Purchase
        fields = [
            'purchase_id',
            'date_of_purchase',
            'branch_id',
            'total_spent',
            'total_products'
        ]
    
    def get_total_spent(self, obj):
        return sum(item.selling_price * item.quantity for item in obj.soldproduct_set.all())
    
    def get_total_products(self, obj):
        return sum(item.quantity for item in obj.soldproduct_set.all())

class SaleDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name')
    product_category = serializers.CharField(source='product_id.category_id.category_name')
    branch_location = serializers.CharField(source='purchase_id.branch_id.location')
    
    class Meta:
        model = SoldProduct
        fields = [
            'product_id',
            'product_name',
            'product_category',
            'quantity',
            'main_price',
            'selling_price',
            'branch_location',
            'purchase_id',
            'date_of_purchase'
        ]
    
    date_of_purchase = serializers.DateTimeField(source='purchase_id.date_of_purchase')
    
    
    
    
    
    
    from rest_framework import serializers
from .models import Purchase, SoldProduct

class PurchaseLogSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    branch_location = serializers.CharField(source='branch_id.location')
    total_amount = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Purchase
        fields = [
            'purchase_id',
            'date_of_purchase',
            'customer_name',
            'branch_location',
            'total_amount',
            'total_items'
        ]

    def get_customer_name(self, obj):
        return f"{obj.customer_id.first_name} {obj.customer_id.last_name}"

    def get_total_amount(self, obj):
        return sum(item.selling_price * item.quantity for item in obj.soldproduct_set.all())

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.soldproduct_set.all())

class SoldProductDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name')
    product_category = serializers.CharField(source='product_id.category_id.category_name')
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = SoldProduct
        fields = [
            'product_id',
            'product_name',
            'product_category',
            'quantity',
            'selling_price',
            'total_price'
        ]

    def get_total_price(self, obj):
        return obj.selling_price * obj.quantity
    
### branch manager requested products log 
class RequestedProductsLogSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='order_id.branch_id.location')
    date_of_request = serializers.DateTimeField(source='order_id.date_of_order')
    status_display = serializers.CharField(source='get_status_display')

    class Meta:
        model = RequestedProducts
        fields = [
            'id',
            'date_of_request',
            'branch_name',
            'product_id',
            'quantity',
            'status',
            'status_display'
        ]

class RequestedProductDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name')
    category_name = serializers.CharField(source='product_id.category_id.category_name')
    branch_name = serializers.CharField(source='order_id.branch_id.location')
    date_of_request = serializers.DateTimeField(source='order_id.date_of_order')
    status_display = serializers.CharField(source='get_status_display')

    class Meta:
        model = RequestedProducts
        fields = [
            'id',
            'product_name',
            'category_name',
            'quantity',
            'status',
            'status_display',
            'branch_name',
            'date_of_request',
            'rejection_reason'
        ]
        
        
### sold products logs for branch managers 
class SoldProductsLogSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Purchase
        fields = ['purchase_id', 'date_of_purchase', 'customer_name', 'total_amount', 'total_items']

    def get_customer_name(self, obj):
        return f"{obj.customer_id.first_name} {obj.customer_id.last_name}"

    def get_total_amount(self, obj):
        return obj.soldproduct_set.aggregate(
            total=Sum(F('selling_price') * F('quantity'))
        )['total'] or 0

    def get_total_items(self, obj):
        return obj.soldproduct_set.aggregate(
            total=Sum('quantity')
        )['total'] or 0

class SoldProductDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name')
    category_name = serializers.CharField(source='product_id.category_id.category_name')
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = SoldProduct
        fields = ['product_id', 'product_name', 'category_name', 'quantity', 'selling_price', 'total_price']

    def get_total_price(self, obj):
        return obj.selling_price * obj.quantity



# warehouse MANAGER 

## send products 
class WarehouseProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'product_name', 'category_id', 'quantity', 'main_price', 'sale_price']


class ProductItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class SendProductsSerializer(serializers.Serializer):
    branch_name = serializers.CharField(required=True)
    products = serializers.ListField(
        child=ProductItemSerializer(),
        min_length=1
    )
    
    
### retrieve from branch 
from .models import BranchProducts

class BranchProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product_id.product_id')
    product_name = serializers.CharField(source='product_id.product_name')
    category = serializers.CharField(source='product_id.category_id.category_name')
    main_price = serializers.DecimalField(source='product_id.main_price', max_digits=10, decimal_places=2)
    sale_price = serializers.DecimalField(source='product_id.sale_price', max_digits=10, decimal_places=2)
    
    class Meta:
        model = BranchProducts
        fields = [
            'product_id',
            'product_name',
            'category',
            'main_price',
            'sale_price',
            'quantity'
        ]


class RetrieveProductsSerializer(serializers.Serializer):
    branch_id = serializers.IntegerField(required=True)
    products = serializers.ListField(
        child=ProductItemSerializer(),
        min_length=1
    )
    
    
    
### products log serializer 
# serializers.py
from rest_framework import serializers
from .models import ProductTransaction, TransportedProducts

class TransportedProductsSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name')
    category = serializers.CharField(source='product_id.category_id.category_name')
    
    class Meta:
        model = TransportedProducts
        fields = [
            'product_id', 
            'product_name',
            'category',
            'main_price',
            'selling_price',
            'quantity',
            'movement_type'
        ]

class ProductTransactionSerializer(serializers.ModelSerializer):
    products = TransportedProductsSerializer(
        source='transportedproducts_set', 
        many=True
    )
    branch_name = serializers.CharField(source='branch_id.location')
    movement_type_display = serializers.CharField(source='get_movement_type_display')
    
    class Meta:
        model = ProductTransaction
        fields = [
            'process_id',
            'date_of_transaction',
            'branch_name',
            'movement_type',
            'movement_type_display',
            'is_done',
            'products'
        ]



### manage requests 
# serializers.py
from rest_framework import serializers
from .models import BranchOrder, RequestedProducts

class RequestedProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name')
    category = serializers.CharField(source='product_id.category_id.category_name')
    current_warehouse_stock = serializers.SerializerMethodField()

    class Meta:
        model = RequestedProducts
        fields = [
            'id',
            'product_id',
            'product_name',
            'category',
            'quantity',
            'status',
            'current_warehouse_stock',
            'rejection_reason'
        ]

    def get_current_warehouse_stock(self, obj):
        return obj.product_id.quantity

class BranchOrderSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch_id.location')
    requested_products = RequestedProductSerializer(
        source='requestedproducts_set', 
        many=True,
        read_only=True
    )
    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = BranchOrder
        fields = [
            'order_id',
            'branch_name',
            'manager_name',
            'date_of_order',
            'note',
            'is_done',
            'requested_products'
        ]

    def get_manager_name(self, obj):
        if obj.branch_id.manager_id:
            return str(obj.branch_id.manager_id)
        return None

class ProductActionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

class ProcessRequestSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject', 'partial'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    products = ProductActionSerializer(many=True, required=False)
    
    
    
##request logs 
# serializers.py
from rest_framework import serializers
from .models import BranchOrder, RequestedProducts

class RequestedProductLogSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name')
    category = serializers.CharField(source='product_id.category_id.category_name')
    status_display = serializers.CharField(source='get_status_display')

    class Meta:
        model = RequestedProducts
        fields = [
            'id',
            'product_id',
            'product_name',
            'category',
            'quantity',
            'status',
            'status_display',
            'rejection_reason'
        ]

class BranchOrderLogSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch_id.location')
    city = serializers.CharField(source='branch_id.city_id.city_name')
    manager_name = serializers.SerializerMethodField()
    products = RequestedProductLogSerializer(
        source='requestedproducts_set', 
        many=True
    )
    status_summary = serializers.SerializerMethodField()

    class Meta:
        model = BranchOrder
        fields = [
            'order_id',
            'branch_name',
            'city',
            'manager_name',
            'date_of_order',
            'note',
            'is_done',
            'status_summary',
            'products'
        ]

    def get_manager_name(self, obj):
        return str(obj.branch_id.manager_id) if obj.branch_id.manager_id else None

    def get_status_summary(self, obj):
        products = obj.requestedproducts_set.all()
        return {
            'pending': products.filter(status='P').count(),
            'approved': products.filter(status='S').count(),
            'rejected': products.filter(status='R').count()
        }