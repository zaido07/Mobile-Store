from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.
# class Employee(models.Model):
#     pass
# class Phone(models.Model):
#     pass
# class Camera(models.Model):
#     pass
#اساسيات المشروع 
                                                    #المدينة 
class City(models.Model):
    city_id=models.IntegerField(primary_key=True)
    city_name=models.CharField(max_length=20)
    
    def __str__(self):
        return self.city_name
#                                                العمل         
class Job(models.Model):
    job_id=models.IntegerField(primary_key=True)
    job_name=models.CharField(max_length=50)
    
    def __str__(self):
            return self.job_name
        
#                                                    الفرع 
class Branch(models.Model):
    branch_id=models.IntegerField(primary_key=True)
    branch_number=models.IntegerField()
    location=models.CharField(max_length=50)
    city_id=models.ForeignKey(City,on_delete=models.CASCADE)
    manager_id=models.ForeignKey('Employee',on_delete=models.CASCADE,null=True,blank=True)
        
    def __str__(self):
        return f"Branch {self.branch_number}-{self.location}"
    
    
                                #الموظف 
class Employee(models.Model):
    id=models.CharField(primary_key=True,max_length=20,null=False)
    f_name=models.CharField(max_length=20,null=False)
    middle_name=models.CharField(max_length=20,null=False)
    l_name=models.CharField(max_length=20,null=False)
    birthdate=models.DateField(null=False)
    address=models.CharField(max_length=50,null=False)
    email=models.EmailField(max_length=20,null=False)
    phone_num=models.CharField(max_length=20,null=False)
    gender_choice=[(True,'Male'),(False,'Female')]
    gender=models.BooleanField(choices=gender_choice)
    job_id=models.ForeignKey(Job,on_delete=models.CASCADE,null=False)
    branch_id=models.ForeignKey(Branch,on_delete=models.CASCADE,null=False)
    user_account = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='employee'
    )
    
    def __str__(self):
            return f"{self.f_name} {self.middle_name} {self.l_name}"
    def age(self):
        import datetime
        today = datetime.date.today()
        employee_age= int((today-self.birthdate).days/365.25)
        if employee_age>18:
            return employee_age
        else:
            return "Not Eligible for Job"
#المنتجاات //////////////////////////////////ا
#                                              الصنف 
class ProductCategory(models.Model):
    category_id=models.IntegerField(primary_key=True)
    category_name=models.CharField(max_length=40)
    def __str__(self):
        return self.category_name
#                                                     المنتح
class Product(models.Model):
    product_id=models.IntegerField(primary_key=True)
    product_name=models.CharField(max_length=20)
    category_id=models.ForeignKey(ProductCategory,on_delete=models.CASCADE)
    main_price=models.DecimalField(decimal_places=2,max_digits=7)
    sale_price=models.DecimalField(decimal_places=2,max_digits=7)
    quantity=models.IntegerField()
    
    def __str__(self):
        return self.product_name
#                                                                 نوع الاكسسوار  
class AccessoriesType(models.Model):
    accessories_type=models.IntegerField(primary_key= True)
    type=models.CharField(max_length=20)
    def __str__(self):
        return self.type
#                                            الاكسسوار
class Accessories(models.Model):
    product_id=models.ForeignKey(Product,on_delete=models.CASCADE)
    description=models.CharField(max_length=20)
    accessories_type=models.ForeignKey(AccessoriesType,on_delete=models.CASCADE)
    def __str__(self):
        return self.description
#                                                    البراند
class Brand(models.Model):
    brand_id=models.IntegerField(primary_key=True)
    brand_name=models.CharField(max_length=20)
    
    def __str__(self):
        return self.brand_name
#                                                    اللون 
class Color(models.Model):
    color_id=models.IntegerField(primary_key=True)
    color_name=models.CharField(max_length=20)
    
    def __str__(self):
        return self.color_name
#                                                       الكاميرا
class Camera(models.Model):
    camera_id=models.IntegerField(primary_key=True)
    front_camera=models.IntegerField()
    back_camera=models.IntegerField()
    
    def __str__(self):
        return f"front: {self.front_camera} and back: {self.back_camera}"
    #                                              الموبايل
class Phone(models.Model):
        product_id=models.ForeignKey(Product,on_delete=models.CASCADE)
        brand_id=models.ForeignKey(Brand,on_delete=models.CASCADE)
        color_id=models.ForeignKey(Color,on_delete=models.CASCADE)
        camera_id=models.ForeignKey(Camera,on_delete=models.CASCADE)
        storage=models.IntegerField()
        battery=models.IntegerField()
        dual_sim=models.BooleanField()
        sd_card=models.BooleanField()
        ram=models.IntegerField()
        display_size=models.DecimalField(max_digits=7,decimal_places=2)
        description=models.CharField(max_length=50)
        release_date=models.DateField()
        
        def __str__(self):
            return f"{self.product_id}"
#                                                       منتجات الفرع 
class BranchProducts(models.Model):
    branch_id=models.ForeignKey(Branch,on_delete=models.CASCADE)
    product_id=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    #يعيد رقم الفرع
    def __str__(self):
        return self.branch_id    


# عملية الشراء مع الزبون 
#                                                              الزبون 
class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    national_num=models.CharField(max_length=20,unique=True)
    first_name=models.CharField(max_length=20)
    middle_name=models.CharField(max_length=20)
    last_name=models.CharField(max_length=20)
    phone_num=models.CharField(max_length=20,unique=True)
    gender_choice=[(True,'Male'),(False,'Female')]
    gender=models.BooleanField(choices=gender_choice)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name+" "+self.middle_name+" "+self.last_name
#                                           عملية الشراء
class Purchase(models.Model):
    purchase_id=models.CharField(primary_key=True,max_length=20)
    branch_id=models.ForeignKey(Branch,on_delete=models.CASCADE)
    customer_id=models.ForeignKey(Customer, on_delete=models.CASCADE)
    date_of_purchase=models.DateField()
    
    def __str__(self):
        return f"Purchase {self.purchase_id}"
#                                                          معلومات الشراء 
class SoldProduct(models.Model):
    purchase_id=models.ForeignKey(Purchase,on_delete=models.CASCADE)
    product_id=models.ForeignKey(Product,on_delete=models.CASCADE)
    main_price=models.DecimalField(decimal_places=2,max_digits=12)
    selling_price=models.DecimalField(decimal_places=2,max_digits=12)
    quantity=models.IntegerField()
    
    def __str__(self):
        return f"{self.purchase_id} sold{self.product_id} with {self.quantity} pieces"
# طلب المنتجات/////////////////////////////////////////////////////////////////////////////////
class BranchOrder(models.Model):
    order_id=models.IntegerField(primary_key=True)
    branch_id=models.ForeignKey(Branch,on_delete=models.CASCADE)
    date_of_order=models.DateField()
    note=models.CharField(max_length=50)
    is_done=models.BooleanField()
    def __str__(self):
        return f" order: {self.order_id} to branch {self.branch_id}"
#طلب المنتجات
class RequestedProducts(models.Model):
    order_id=models.ForeignKey(BranchOrder,on_delete=models.CASCADE)
    product_id=models.ForeignKey(Product,on_delete=models.CASCADE)
    status_choices=[('S','success'),('R','Rejected'),('P','Pending')]
    status=models.CharField(max_length=1,choices=status_choices,default='p')
    def __str__(self):
        return f"order {self.order_id} product {self.product_id} status {self.status}"

class ProductTransaction(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('TRANSFER', 'Transfer Between Branches'),
        ('RETURN', 'Return to Supplier'),
        ('ADJUSTMENT', 'Inventory Adjustment'),
    ]
    
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPE_CHOICES
    )
    process_id=models.IntegerField(primary_key=True)
    branch_id=models.ForeignKey(Branch,on_delete=models.CASCADE)
    date_of_transaction=models.DateTimeField()
    is_done=models.BooleanField()
    
    def __str__(self):
        return f"process {self.process_id} branch{self.branch_id}"

class TransportedProducts(models.Model):
    process_id=models.ForeignKey(ProductTransaction,on_delete=models.CASCADE)
    product_id=models.ForeignKey(Product,on_delete=models.CASCADE)
    main_price=models.DecimalField(decimal_places=2,max_digits=12)
    selling_price=models.DecimalField(decimal_places=2,max_digits=12)
    quantity=models.IntegerField()
    
    def __str__(self):
        return f"process{self.process_id} product{self.product_id} "
    