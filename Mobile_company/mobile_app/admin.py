from django.contrib import admin
from .models import *
from .models import City,Job,Branch,Employee,ProductCategory,Product,Accessories,AccessoriesType,Brand,Color,Camera,Phone,BranchProducts,Customer,Purchase,SoldProduct,BranchOrder,RequestedProducts,ProductTransaction,TransportedProducts
# Register your models here.
admin.site.register(City)
admin.site.register(Job)
admin.site.register(Branch)
admin.site.register(Employee)
admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(Accessories)
admin.site.register(AccessoriesType)
admin.site.register(Brand)
admin.site.register(Color)
admin.site.register(Camera)
admin.site.register(Phone)
admin.site.register(BranchProducts)
admin.site.register(Customer)
admin.site.register(Purchase)
admin.site.register(SoldProduct)
admin.site.register(BranchOrder)
admin.site.register(RequestedProducts)
admin.site.register(ProductTransaction)
admin.site.register(TransportedProducts)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'instance_id', 'timestamp')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'model_name', 'instance_id')
    readonly_fields = ('user', 'action', 'model_name', 'instance_id', 'details', 'ip_address', 'timestamp')
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False