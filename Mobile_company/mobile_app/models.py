from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User  
from datetime import date
from django.core.exceptions import ValidationError
class TrackChangesMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_state = self._get_current_state()

    def _get_current_state(self):
        return {field.name: getattr(self, field.name) 
                for field in self._meta.fields
                if not field.is_relation or field.many_to_one}

    def get_changes(self):
        current_state = self._get_current_state()
        return {
            field: {'from': self._original_state[field], 'to': current_state[field]}
            for field in current_state
            if current_state[field] != self._original_state[field]
        }

                                 #المدينة 
class City(models.Model,TrackChangesMixin):
    city_id=models.AutoField(primary_key=True)
    city_name=models.CharField(max_length=20)
    
    def __str__(self):
        return self.city_name
#                                                العمل         
class Job(models.Model,TrackChangesMixin):
    job_id=models.AutoField(primary_key=True)
    job_name=models.CharField(max_length=50)
    
    def __str__(self):
            return self.job_name
        
#                                                    الفرع 
class Branch(models.Model,TrackChangesMixin):
    branch_id=models.AutoField(primary_key=True)
    branch_number=models.IntegerField()
    location=models.CharField(max_length=50)
    city_id=models.ForeignKey(City,on_delete=models.CASCADE)
    manager_id=models.ForeignKey('Employee',on_delete=models.CASCADE,null=True,blank=True)
    
    def __str__(self):
        return f"Branch {self.branch_number}-{self.location}"
    
    
                                #الموظف 


class Employee(models.Model,TrackChangesMixin):
    phone_validator = RegexValidator(
        regex=r'^09\d{8}$',
        message="Phone number must be 10 digits (e.g., '9876543210')."
    )
    national_num_validator=RegexValidator(
        regex=r'^\d{11}$',
        message="national number must be 11 digits (e.g., '10987654321')."
    )
    def validate_age(birthdate):
        today = date.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        if age < 18:
            raise ValidationError("Employee must be at least 18 years old.")
    def validate_salary(value):
        if value >= 9999999.99:
            raise ValidationError('Salary must be less than 8 digits.')
    
    id = models.AutoField(primary_key=True,null=False)
    f_name = models.CharField(max_length=20, null=False)
    middle_name = models.CharField(max_length=20, null=False)
    l_name = models.CharField(max_length=20, null=False)
    birthdate = models.DateField(null=False, validators=[validate_age])
    address = models.CharField(max_length=50, null=False)
    email = models.EmailField(max_length=20, null=False)
    phone_num = models.CharField(max_length=10,null=False, validators=[phone_validator])
    gender_choices = [(True, 'Male'), (False, 'Female')]
    gender = models.BooleanField(choices=gender_choices)
    job_id = models.ForeignKey('Job', on_delete=models.CASCADE, null=False)
    branch_id = models.ForeignKey('Branch', on_delete=models.CASCADE, null=False)
    user_account = models.OneToOneField(
        User,  
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee'
    )
    salary = models.DecimalField(max_digits=9,decimal_places=2,null=True,blank=True)
    national_num=models.CharField(max_length=11,validators=[national_num_validator])
    profile_image = models.ImageField(
        upload_to='employee_images/',  
        null=True,
        blank=True
    )
    def __str__(self):
        return f"{self.f_name} {self.l_name}"
#المنتجاات //////////////////////////////////ا
#                                              الصنف 
class ProductCategory(models.Model,TrackChangesMixin):
    category_id=models.IntegerField(primary_key=True)
    category_name=models.CharField(max_length=40)
    def __str__(self):
        return self.category_name
#                                                     المنتح
class Product(models.Model,TrackChangesMixin):
    product_id=models.AutoField(primary_key=True)
    product_name=models.CharField(max_length=20)
    category_id=models.ForeignKey(ProductCategory,on_delete=models.CASCADE)
    main_price=models.DecimalField(decimal_places=2,max_digits=7)
    sale_price=models.DecimalField(decimal_places=2,max_digits=7)
    quantity=models.IntegerField(validators=[MinValueValidator(1)],  # Ensures quantity is at least 1
        help_text="Quantity must be greater than 0")
    
    def __str__(self):
        return self.product_name
#                                                                 نوع الاكسسوار  
class AccessoriesType(models.Model,TrackChangesMixin):
    accessories_type=models.AutoField(primary_key= True)
    type=models.CharField(max_length=20)
    def __str__(self):
        return self.type
#                                            الاكسسوار
class Accessories(models.Model,TrackChangesMixin):
    product_id = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='accessory'
    )
    description = models.CharField(max_length=20)
    accessories_type = models.ForeignKey(AccessoriesType, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.description   
    #البراند
class Brand(models.Model,TrackChangesMixin):
    brand_id=models.AutoField(primary_key=True)
    brand_name=models.CharField(max_length=20)
    
    def __str__(self):
        return self.brand_name
#                                                    اللون 
class Color(models.Model,TrackChangesMixin):
    color_id=models.AutoField(primary_key=True)
    color_name=models.CharField(max_length=20)
    
    def __str__(self):
        return self.color_name
#                                                       الكاميرا
class Camera(models.Model,TrackChangesMixin):
    camera_id=models.IntegerField(primary_key=True)
    front_camera=models.IntegerField()
    back_camera=models.IntegerField()
    
    def __str__(self):
        return f"front: {self.front_camera} and back: {self.back_camera}"
    #                                              ا
    # لموبايلclass 
class Phone(models.Model,TrackChangesMixin):
    product_id = models.OneToOneField(
        Product, 
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='phones'
    )
    brand_id = models.ForeignKey(Brand, on_delete=models.CASCADE)
    color_id = models.ForeignKey(Color, on_delete=models.CASCADE)
    camera_id = models.ForeignKey(Camera, on_delete=models.CASCADE)
    storage = models.IntegerField(help_text="Storage in GB")
    battery = models.IntegerField(help_text="Battery capacity in mAh")
    dual_sim = models.BooleanField(default=False)
    sd_card = models.BooleanField(default=False)
    ram = models.IntegerField(help_text="RAM in GB")
    processor=models.CharField(max_length=30)
    display_size = models.DecimalField(max_digits=3, decimal_places=2, help_text="Display size in inches")
    description = models.CharField(max_length=500, blank=True)
    release_date = models.DateField(null=True, blank=True)
    def __str__(self):
        return f"{self.product_id.product_name} (ID: {self.product_id_id})"
#                                                       منتجات الفرع 
class BranchProducts(models.Model,TrackChangesMixin):
    branch_id=models.ForeignKey(Branch,on_delete=models.CASCADE)
    product_id=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField(validators=[MinValueValidator(1)],  # Ensures quantity is at least 1
        help_text="Quantity must be greater than 0")
    #يعيد رقم الفرع
    def __str__(self):
        return f"{self.branch_id }"   


# عملية الشراء مع الزبون 
#                                                              الزبون 
class Customer(models.Model,TrackChangesMixin):
    national_num_validator = RegexValidator(
        regex=r'^\d{11}$',
        message="Phone number must be 11 digits (e.g., '9876543210')."
    )
    phone_validator = RegexValidator(
        regex=r'^\d{10}$',
        message="Phone number must be 10 digits (e.g., '9876543210')."
    )
    customer_id = models.AutoField(primary_key=True)
    national_num=models.CharField(max_length=20,unique=True,validators=[national_num_validator])
    first_name=models.CharField(max_length=20)
    middle_name=models.CharField(max_length=20)
    last_name=models.CharField(max_length=20)
    phone_num=models.CharField(max_length=20,unique=True,validators=[phone_validator])
    gender_choice=[(True,'Male'),(False,'Female')]
    gender=models.BooleanField(choices=gender_choice)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name+" "+self.middle_name+" "+self.last_name
#                                           عملية الشراء
class Purchase(models.Model,TrackChangesMixin):
    purchase_id=models.AutoField(primary_key=True)
    branch_id=models.ForeignKey(Branch,on_delete=models.CASCADE)
    customer_id=models.ForeignKey(Customer, on_delete=models.CASCADE)
    date_of_purchase=models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Purchase {self.purchase_id}"
#                                                          معلومات الشراء 
class SoldProduct(models.Model,TrackChangesMixin):
    purchase_id=models.ForeignKey(Purchase,on_delete=models.CASCADE)
    product_id=models.ForeignKey(Product,on_delete=models.CASCADE)
    main_price=models.DecimalField(decimal_places=2,max_digits=12)
    selling_price=models.DecimalField(decimal_places=2,max_digits=12)
    quantity=models.IntegerField(validators=[MinValueValidator(1)],  # Ensures quantity is at least 1
        help_text="Quantity must be greater than 0")
    
    def __str__(self):
        return f"{self.purchase_id} sold{self.product_id} with {self.quantity} pieces"
# طلب المنتجات/////////////////////////////////////////////////////////////////////////////////
class BranchOrder(models.Model,TrackChangesMixin):
    order_id=models.AutoField(primary_key=True)
    branch_id=models.ForeignKey(Branch,on_delete=models.CASCADE)
    date_of_order=models.DateField()
    note = models.CharField(
        max_length=50,
        blank=True,   # Allows empty string in forms/admin
        null=True,    # Allows NULL in the database
        default='',   # Optional: Default to empty string instead of NULL
    )
    is_done=models.BooleanField(default=False)
    def __str__(self):
        return f" order: {self.order_id} to branch {self.branch_id}"
#طلب المنتجات
class RequestedProducts(models.Model,TrackChangesMixin):
    order_id = models.ForeignKey(BranchOrder, on_delete=models.CASCADE,related_name='requestedproducts_set')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=1, choices=[('S','Approved'), ('R','Rejected'), ('P','Pending')], default='P')
    rejection_reason = models.CharField(max_length=255, blank=True, null=True) 
    processed_date = models.DateTimeField(null=True, blank=True) 
    
    
    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status)
    
    def __str__(self):
        return f"Order {self.order_id} - Product {self.product_id}"

class ProductTransaction(models.Model,TrackChangesMixin):
    MOVEMENT_TYPE_CHOICES = [
        ('sent', 'sent'),
        ('retrieved', 'retrieved'),
    ]
    
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPE_CHOICES
    )
    process_id = models.AutoField(primary_key=True)  # Let Django handle the ID automatically
    branch_id = models.ForeignKey(Branch, on_delete=models.CASCADE)
    date_of_transaction = models.DateTimeField(auto_now_add=True)  # Automatically set date
    is_done = models.BooleanField(default=False)
    class Meta:
        db_table = 'product_transaction'
    
    def __str__(self):
        return f"process {self.process_id} branch {self.branch_id}"
class TransportedProducts(models.Model,TrackChangesMixin):
    # The foreign key should point to ProductTransaction
    transaction = models.ForeignKey(
        ProductTransaction, 
        on_delete=models.CASCADE,
        related_name='transported_items',
        db_column='process_id'  # Explicitly map to your database column
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    main_price = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.IntegerField()

    class Meta:
        db_table = 'transported_products'
        
        
        
########################### Logging 
from django.contrib.auth import get_user_model

User = get_user_model()

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    instance_id = models.CharField(max_length=50, null=True, blank=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} at {self.timestamp}"