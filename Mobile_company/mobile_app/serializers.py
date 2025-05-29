from.models import *
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Sum,F,Count,Q
from django.core.cache import cache
import time
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

class ManageEmployeeSerializer(serializers.ModelSerializer):
    manager_name=serializers.SerializerMethodField()
    job_name=serializers.CharField(source='job_id.job_name',read_only=True)
    branch_location=serializers.CharField(source='branch_id.location',read_only=True)
    
    
    class Meta:
        model=Employee
        fields=['manager_name','job_name','branch_location','id']
    def get_manager_name(self,obj):
        return f"{obj.f_name} {obj.middle_name} {obj.l_name}"

class AddBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model=Branch
        fields='__all__'
        
        
        
class BranchSerializer(serializers.ModelSerializer):
    manager_name = serializers.SerializerMethodField()
    class Meta:
        model = Branch
        fields = ['manager_id','city_id','location','branch_number','manager_name']
        extra_kwargs = {
            'city_id': {
                'read_only': True  
            }
        }
    def get_manager_name(self, obj):
            if obj.manager_id:
                return f"{obj.manager_id.f_name} {obj.manager_id.l_name}"
            return None
    
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'

# serializers.py
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category_id.category_name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'product_id',
            'product_name', 
            'category_id',
            'category_name',
            'main_price',
            'sale_price',
            'quantity'
        ]
        extra_kwargs = {
            'product_id': {'read_only': True}
        }

class AccessoriesSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    
    class Meta:
        model = Accessories
        fields = '__all__'


# serializers.py
class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = '__all__'
class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = '__all__'

## sales manager


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'

class SoldProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoldProduct
        fields = '__all__'


    
class ProductItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)
    

    
    


##login 

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add admin claims to the token
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        token['username'] = user.username
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user info to the response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'is_staff': self.user.is_staff,
            'is_superuser': self.user.is_superuser
        }
        return data
    
### logout 

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()

    def validate(self, attrs):
        self.refresh_token = attrs['refresh']
        self.access_token = attrs['access']
        return attrs

    def save(self, **kwargs):
        try:
            # Blacklist refresh token
            RefreshToken(self.refresh_token).blacklist()
            
            # Blacklist access token
            access_token = AccessToken(self.access_token)
            jti = access_token['jti']
            expires_at = access_token['exp']
            remaining_lifetime = expires_at - int(time.time())
            
            if remaining_lifetime > 0:
                cache.set(
                    f'access_blacklist_{jti}',
                    True,
                    timeout=remaining_lifetime
                )
        except TokenError as e:
            raise serializers.ValidationError({'error': str(e)})



class SoldProductsLogSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_national_num = serializers.CharField(source='customer_id.national_num')
    branch = serializers.CharField(source='branch_id.location')
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        model = Purchase
        fields = [
            'purchase_id',
            'date_of_purchase',
            'total_price',
            'total_items',
            'customer_name',
            'customer_national_num',
            'branch'
        ]
    
    def get_customer_name(self, obj):
        return f"{obj.customer_id.first_name} {obj.customer_id.last_name}"

    def get_customer_name(self, obj):
        return f"{obj.customer_id.first_name} {obj.customer_id.middle_name} {obj.customer_id.last_name}"

    def get_total_products(self, obj):
        return obj.soldproduct_set.aggregate(total=Sum('quantity'))['total'] or 0

    def get_total_price(self, obj):
        return obj.soldproduct_set.aggregate(
            total=Sum(F('selling_price') * F('quantity'))
        )['total'] or 0

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
        
    


# warehouse MANAGER 

## send products 
class WarehouseProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'product_name', 'category_id', 'quantity', 'main_price', 'sale_price']


class ProductItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class ProductTransferSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)




class TransportedProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name')
    category_id = serializers.IntegerField(source='product_id.category_id.pk')
    category_name = serializers.CharField(source='product_id.category_id.category_name')
    
    class Meta:
        model = TransportedProducts
        fields = [
            'product_id',
            'product_name',
            'category_id',
            'category_name',
            'quantity',
            'main_price',
            'selling_price'
        ]

class TransportedProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name')
    category_id = serializers.IntegerField(source='product_id.category_id.pk')
    category_name = serializers.CharField(source='product_id.category_id.category_name')
    
    class Meta:
        model = TransportedProducts
        fields = [
            'product_id',
            'product_name',
            'category_id',
            'category_name',
            'quantity',
            'main_price',
            'selling_price'
        ]


# # For detail view
class ProductTransactionDetailSerializer(serializers.ModelSerializer):
    branch_location = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductTransaction
        fields = ['process_id', 'date_of_transaction', 'branch_location', 'products']
    
    def get_branch_location(self, obj):
        try:
            return obj.branch_id.location
        except:
            return None
    
    def get_products(self, obj):
        products_data = []
        for transported_item in obj.transported_items.all():
            product = transported_item.product
            try:
                products_data.append({
                    'product_id': product.pk,
                    'product_name': product.product_name,
                    'category': product.category_id.category_name if product.category_id else None,
                    'quantity': transported_item.quantity,
                    'type': 'phone' if hasattr(product, 'phone') else 'accessory' if hasattr(product, 'accessory') else 'unknown'
                })
            except Exception as e:
                continue
        return products_data



class RequestedProductLogSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name')
    category = serializers.CharField(source='product_id.category_id.category_name')
    status_display = serializers.SerializerMethodField()

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

    def get_status_display(self, obj):
        return obj.get_status_display()

class BranchOrderLogSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch_id.location')
    city = serializers.CharField(source='branch_id.city_id.city_name')
    manager_name = serializers.SerializerMethodField()
    products = RequestedProductLogSerializer(
        source='requestedproducts_set',
        many=True
    )
    status_summary = serializers.SerializerMethodField()
    total_items = serializers.IntegerField()
    total_quantity = serializers.IntegerField()

    class Meta:
        model = BranchOrder
        fields = [
            'order_id',
            'date_of_order',
            'branch_name',
            'city',
            'manager_name',
            'note',
            'is_done',
            'total_items',
            'total_quantity',
            'status_summary',
            'products'
        ]

    def get_manager_name(self, obj):
        if obj.branch_id.manager_id:
            return f"{obj.branch_id.manager_id.f_name} {obj.branch_id.manager_id.l_name}"
        return None

    def get_status_summary(self, obj):
        return {
            'pending': getattr(obj, 'pending', 0),
            'approved': getattr(obj, 'approved', 0),
            'rejected': getattr(obj, 'rejected', 0)
        }
class ProductActionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

class ProcessRequestSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject', 'partial'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    products = ProductActionSerializer(many=True, required=False)
    
    
    
##request logs 



class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['color_id', 'color_name']
        extra_kwargs = {
            'color_id': {
                'read_only': True  
            }
        }
class AccessoriesTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessoriesType
        fields = ['accessories_type', 'type']
        extra_kwargs = {
            'accessories_type': {
                'read_only': True  
            }
        }
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['brand_id', 'brand_name']
        extra_kwargs = {
            'brand_id': {
                'read_only': True  
            }
        }
    




class TransportedProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name')
    category_name = serializers.CharField(source='product.category_id.category_name') 

    class Meta:
        model = TransportedProducts
        fields = [
            'product_id',
            'product_name',
            'category_name',
            'quantity',
            'main_price',
            'selling_price'
        ]
        
        
        
        
### logging 
# from .models import ActivityLog

class ActivityLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    
    class Meta:
        model = ActivityLog
        fields = '__all__'
class RequestedProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestedProducts
        fields = ['id', 'product_id', 'quantity', 'status', 'rejection_reason']
        
class BranchOrderSerializer(serializers.ModelSerializer):
    requested_products = RequestedProductsSerializer(many=True, read_only=True, source='requestedproducts_set')
    
    class Meta:
        model = BranchOrder
        fields = ['order_id', 'branch_id', 'date_of_order', 'note', 'is_done', 'requested_products']

class RequestedProductActionSerializer1(serializers.Serializer):
    id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    quantity = serializers.IntegerField(required=False)
    rejection_reason = serializers.CharField(required=False)

class ProcessRequestSerializer1(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject', 'partial'])
    rejection_reason = serializers.CharField(required=False)
    products = RequestedProductActionSerializer1(many=True, required=False)
    
    def validate(self, data):
        action = data.get('action')
        products = data.get('products')

        if action == 'partial':
            if not products:
                raise serializers.ValidationError({
                    'products': 'This field is required for partial action.'
                })
            for p in products:
                if 'id' not in p or 'action' not in p:
                    raise serializers.ValidationError({
                        'products': 'Each product must include id and action.'
                    })

        return data
    
    
### sale manager serializers 

## make sale serializer
class MakeSaleSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    products = serializers.ListField(  
        child=serializers.DictField(   
            child=serializers.IntegerField()
        )
    )
    
### customer 
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
    
## search customer serializer 
class CustomerSearchSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['customer_id', 'full_name', 'national_num']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.middle_name} {obj.last_name}"
    

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

## for purchase 
class CustomerSaleSerializer(serializers.ModelSerializer):
    date_of_purchase = serializers.DateField(format='%Y-%m-%d')
    branch_id = serializers.IntegerField(source='branch_id.branch_id')
    total_spent = serializers.SerializerMethodField()
    total_products = serializers.SerializerMethodField()

    class Meta:
        model = Purchase
        fields = [
            'purchase_id', 'date_of_purchase', 'branch_id',
            'total_spent', 'total_products'
        ]

    def get_total_spent(self, obj):
        return sum(item.selling_price * item.quantity for item in obj.soldproduct_set.all())

    def get_total_products(self, obj):
        return sum(item.quantity for item in obj.soldproduct_set.all())
    
## for customer sales details 
class SaleDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name')
    product_category = serializers.CharField(source='product_id.category_id.category_name')
    total_price = serializers.SerializerMethodField()
    date_of_purchase = serializers.DateField(
        source='purchase_id.date_of_purchase', 
        format='%Y-%m-%d'
    )
    branch_location = serializers.CharField(source='purchase_id.branch_id.location')

    class Meta:
        model = SoldProduct
        fields = [
            'product_id', 'product_name', 'product_category',
            'quantity', 'main_price', 'selling_price', 'total_price',
            'branch_location', 'date_of_purchase'
        ]

    def get_total_price(self, obj):
        return obj.quantity * obj.selling_price

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
    
    
    ### branch manager 
class CreateBranchOrderSerializer(serializers.ModelSerializer):
    products = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = BranchOrder
        fields = ['note', 'products']  
        extra_kwargs = {
            'note': {'required': False, 'allow_blank': True}
        }

    def validate_products(self, value):
        for product in value:
            if not all(k in product for k in ['product_id', 'quantity']):
                raise serializers.ValidationError("Each product must contain product_id and quantity")
            if product['quantity'] <= 0:
                raise serializers.ValidationError("Quantity must be positive")
        return value
    
class OrderLogSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch_id.location', read_only=True)
    total_items = serializers.SerializerMethodField()
    total_quantity = serializers.SerializerMethodField()
    status_summary = serializers.SerializerMethodField()

    class Meta:
        model = BranchOrder
        fields = [
            'order_id', 
            'branch_name',
            'date_of_order',
            'note',
            'is_done',
            'total_items',
            'total_quantity',
            'status_summary'
        ]
        read_only_fields = fields

    def get_total_items(self, obj):
        return obj.requestedproducts_set.count()

    def get_total_quantity(self, obj):
        return obj.requestedproducts_set.aggregate(
            total=Sum('quantity')
        )['total'] or 0

    def get_status_summary(self, obj):
        return obj.requestedproducts_set.aggregate(
            pending=Count('status', filter=Q(status='P')),
            approved=Count('status', filter=Q(status='A')),
            rejected=Count('status', filter=Q(status='R'))
        )

class OrderDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name')
    category = serializers.CharField(source='product_id.category_id.category_name')
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = RequestedProducts
        fields = [
            'id',
            'product_name',
            'category',
            'quantity',
            'status',
            'status_display'
        ]
    
    def get_status_display(self, obj):
        status_dict = {
            'P': 'Pending',
            'A': 'Approved',
            'R': 'Rejected'
        }
        return status_dict.get(obj.status, 'Unknown')

class SoldProductsLogSerializer(serializers.ModelSerializer):###used
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

class SoldProductDetailSerializer(serializers.ModelSerializer):###used
    product_name = serializers.CharField(source='product_id.product_name')
    category_name = serializers.CharField(source='product_id.category_id.category_name')
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = SoldProduct
        fields = ['product_id', 'product_name', 'category_name', 'quantity', 'selling_price', 'total_price']

    def get_total_price(self, obj):
        return obj.selling_price * obj.quantity

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


### warehouse manager 
class SendProductsSerializer(serializers.Serializer):
    branch_location = serializers.CharField(required=True)
    products = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        )
    )
    
    def validate_branch_location(self, value):
        if not Branch.objects.filter(location__iexact=value).exists():
            raise serializers.ValidationError("Branch location not found")
        return value
        
    def validate_products(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("At least one product must be specified")
        return value

class RetrieveProductsSerializer(serializers.Serializer):
    branch_location = serializers.CharField(required=True)
    products = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        ),
        min_length=1
    )

    def validate_branch_location(self, value):
        if not Branch.objects.filter(location__iexact=value).exists():
            raise serializers.ValidationError("Branch location not found")
        return value

##for retrieving 
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

class ProductTransactionListSerializer(serializers.ModelSerializer):
    branch_location = serializers.CharField(source='branch_id.location')  
    total_products = serializers.IntegerField()
    total_quantity = serializers.IntegerField()

    class Meta:
        model = ProductTransaction
        fields = [
            'process_id',
            'date_of_transaction',
            'branch_location',
            'movement_type',
            'total_products',
            'total_quantity',
            'is_done'
        ]