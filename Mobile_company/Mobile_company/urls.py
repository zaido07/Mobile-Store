"""
URL configuration for Mobile_company project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from mobile_app import views
from mobile_app.views import *
from django.views.generic import TemplateView
router = DefaultRouter()

# Register all ViewSets
router.register(r'cities', views.CityViewSet)
router.register(r'jobs', views.JobViewSet)
router.register(r'employees', views.EmployeeViewSet)
router.register(r'branches', views.BranchViewSet)
router.register(r'product-categories', views.ProductCategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'accessories-types', views.AccessoriesTypeViewSet)
router.register(r'accessories', views.AccessoriesViewSet)
router.register(r'brands', views.BrandViewSet)
router.register(r'colors', views.ColorViewSet)
router.register(r'cameras', views.CameraViewSet)
router.register(r'phones', views.PhoneViewSet)
router.register(r'branch-products', views.BranchProductsViewSet)
router.register(r'customers', views.CustomerViewSet)
router.register(r'purchases', views.PurchaseViewSet)
router.register(r'sold-products', views.SoldProductViewSet)
router.register(r'branch-orders', views.BranchOrderViewSet)
router.register(r'requested-products', views.RequestedProductsViewSet)
router.register(r'product-transactions', views.ProductTransactionViewSet)
router.register(r'transported-products', views.TransportedProductsViewSet)

urlpatterns = [
    path('myadmin/', admin.site.urls),
    path('myapi/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # LOGIN AND LOGOUT
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'), 
    #branches urls
    path('admin/branches/', BranchManagement.as_view(), name='branch-list'),
    path('admin/branches/AddBranch/', BranchManagement.as_view(), name='add-branch'),
    path('admin/branches/<int:pk>/', BranchDetail.as_view(), name='branch-detail'),
    path('admin/branches/<int:pk>/detail/', BranchOperations.as_view(), name='branch-operations'),
    path('admin/branches/<int:pk>/branchstatistics/', BranchStatisticsView.as_view(),name='branch-statistics'),
    #setting url
    path('admin/settings/cities/add/', CityManagement.as_view(), name='add-city'),
    path('admin/settings/cities/', CityManagement.as_view(), name='show-city'),
    path('admin/settings/cities/delete/<int:pk>/', CityManagement.as_view(), name='delete-city'),
    path('admin/settings/jobs/', JobManagement.as_view(), name='show-jobs'),
    path('admin/settings/jobs/add/', JobManagement.as_view(), name='add-job'),
    path('admin/settings/jobs/delete/<int:pk>/', JobManagement.as_view(), name='delete-job'),
    #admin/statistics url
    path('admin/statistics/', AdminStatisticsView.as_view(), name='company-statistics'),
    ##### manage employee urls
    path('admin/manageEmployee/', EmployeeListView.as_view(), name='employee-list'),
    path('admin/manageEmployee/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('admin/manageEmployee/addEmployee/', AddEmployeeView.as_view(), name='add-employee'),
    path('admin/manageEmployee/<int:pk>/createAccount/', CreateEmployeeAccountView.as_view(), name='create-account'),
    ##### HR PAGE #####
    
    ## statistics ##
    path('ceo/statistics/', CeoStatisticsView.as_view(), name='cep-statistics'),
    
    ## branch statistics ##
    path('ceo/branchstatistics/<int:pk>/', CeoBranchStatisticsView.as_view(), name='ceo-branch-statistics'),
    
    ##ceo branch detail 
    path('ceo/branches/', CeoBranchManagement.as_view(), name='ceo-branch-list'),
    path('ceo/branches/AddBranch/', CeoBranchManagement.as_view(), name='ceo-add-branch'),
    path('ceo/branches/<int:pk>/', CeoBranchDetail.as_view(), name='ceo-branch-detail'),
    path('ceo/branches/<int:pk>/detail/', CeoBranchOperations.as_view(), name='ceo-branch-operations'),
    ##ceo settings for cities 
    path('ceo/settings/cities/add/', CeoCityManagement.as_view(), name='ceo-add-city'),
    path('ceo/settings/cities/', CeoCityManagement.as_view(), name='ceo-show-city'),
    path('ceo/settings/cities/delete/<int:pk>/', CeoCityManagement.as_view(), name='ceo-delete-city'),
    path('ceo/manageEmployee/', CeoEmployeeListView.as_view(), name='ceo-employee-list'),
    path('ceo/manageEmployee/<int:pk>/', CeoEmployeeDetailView.as_view(), name='ceo-employee-detail'),
    
    
    ### Hr ###
    ### manage employees ###
    path('HR/manageEmployee/', HrEmployeeListView.as_view(), name='Hr-employee-list'),
    path('HR/manageEmployee/<int:pk>/', HrEmployeeDetailView.as_view(), name='Hr-employee-detail'),
    path('HR/manageEmployee/addEmployee/',HrAddEmployeeView.as_view(), name='Hr-add-employee'),
    path('HR/manageEmployee/<int:pk>/createAccount/', HrCreateEmployeeAccountView.as_view(), name='Hr-create-account'),
    
    ## settings to manage job title 
    
    path('Hr/settings/jobs/', HrJobManagement.as_view(), name='Hr-show-jobs'),
    path('Hr/settings/jobs/add/', HrJobManagement.as_view(), name='Hr-add-job'),
    path('Hr/settings/jobs/delete/<int:pk>/', HrJobManagement.as_view(), name='Hr-delete-job'),

    #### sales manager 

    ## sale manager products 
    path('salesmanager/products/', SalesManagerProductsView.as_view(), name='salesmanager-products'),
    
    ## make sale
    path('salesmanager/makesale/', MakeSaleView.as_view(), name='make-sale'),
    ## add customer 
    path('salesmanager/addcustomer/', AddCustomerView.as_view(), name='add-customer'),
    ## customer crud 
    path('salesmanager/customer/', CustomerListView.as_view(), name='customer-list'),
    ## customer sales log
    path('salesmanager/customer/<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
        path('salesmanager/customer/customersoldproductslog/<int:pk>/', 
        CustomerSalesLogView.as_view(), 
        name='customer-sales-log'),
    path('salesmanager/customer/customersoldproductslog/<int:customer_pk>/<int:purchase_pk>/', 
        SaleDetailView.as_view(), 
        name='sale-detail'),
    ### sold products log
    path('salesmanager/soldproductlog/', SoldProductLogView.as_view(), name='sold-product-log'),
    path('salesmanager/soldproductlog/<str:purchase_id>/', PurchaseDetailView.as_view(), name='purchase-detail'),
    #### generate bill 
    path('salesmanager/bills/<str:purchase_id>/', GenerateBillView.as_view(), name='generate-bill'),
    path('salesmanager/bills/<str:purchase_id>/pdf/', GenerateBillPDFView.as_view(), name='generate-bill-pdf'),
    
    
    ## branch manager 
    #manager statistics 
    path('BranchManager/statistics/', BranchManagerStatisticsView.as_view(), name='branch-manager-statistics'),
    ### branch products
    path('BranchManager/products/', BranchManagerProductsView.as_view(), name='branch-manager-products'),
    path('BranchManager/products/mobile/<int:pk>/', BranchManagerPhoneDetailView.as_view(), name='branch-phone-detail'),
    path('BranchManager/products/Accessories/<int:pk>/', BranchManagerAccessoryDetailView.as_view(), name='branch-accessory-detail'),
    ## order product 
    path('BranchManager/orderProduct/', BranchManagerOrderProductsView.as_view(), name='branch-order-products'),
    ### requested products log 
    path('branchmanager/requestedproductslog/', RequestedProductsLogView.as_view(), name='requested-products-log'),
    path('branchmanager/requestedproductslog/<int:pk>/', RequestedProductDetailView.as_view(), name='requested-product-detail'),
    
    ## SOLD PRODUCTS LOG 
    path('branchmanager/soldproductslog/', SoldProductsLogView.as_view(),name='sold-products-log'),
    path('branchmanager/soldproductslog/<str:purchase_id>/',SoldProductPurchaseDetailView.as_view(), name='sold-products-detail') ,  
    
    
    ## WareHouse Manager Page ###
    ### products CRUD
    ## show products 
    path('warehousemanager/products/', WarehouseProductView.as_view(), name='warehouse-products'),
    ## specific phone
    path('warehousemanager/products/phone/<int:pk>/', PhoneManagementView.as_view(), name='phone-management'),
    ## specific accessory
    path('warehousemanager/products/accessory/<int:pk>/', AccessoryManagementView.as_view(), name='accessory-management'),
    ## add product
    path('warehousemanager/products/addproduct/', AddProduct.as_view(), name='add-product'),
    ## edit multiple products
    path('warehousemanager/products/editproducts/', EditMultiple.as_view(), name='bulk-edit-products'),
    ##send products 
    path('warehousemanager/sendproducts/', WarehouseSendProductsView.as_view(),  name='warehouse-send-products'),
    path('warehouse/manager/retrieveproducts/', WarehouseRetrieveProductsView.as_view(), name='warehouse-retrieve-products'),
    ### products movement 
    path('warehousemanager/productslog/', WarehouseManagerProductsLog.as_view(), name='warehouse-products-log'),
    path('warehousemanager/productslog/<int:process_id>/', WarehouseManagerProductLogDetail.as_view(), name='warehouse-product-log-detail'),
    ## manage requests from branches 
    path('warehouse/managerrequests/', WarehouseManagerRequests.as_view(), name='warehouse-manager-requests'),
    path('warehouse/managerrequests/<int:order_id>/', WarehouseManagerRequests.as_view(), name='process-request'),
    ### request logs
    path('warehousemanager/requestlogs/', WarehouseManagerRequestLogs.as_view(), name='warehouse-request-logs'),
    path('warehousemanager/requestlogs/<int:order_id>/', WarehouseManagerRequestLogDetail.as_view(), name='warehouse-request-detail'),
    #### settings brand 
    ## phone 
    path('settings/phone-brands/', PhoneBrandListCreateView.as_view(), name='phone-brand-list'),
    path('settings/phone-brands/<int:brand_id>/', PhoneBrandRetrieveUpdateDestroyView.as_view(), name='phone-brand-detail'),
    
    # Colors
    path('settings/colors/', ColorListCreateView.as_view(), name='color-list'),
    path('settings/colors/<int:color_id>/', ColorRetrieveUpdateDestroyView.as_view(), name='color-detail'),
    
    # Accessory Types
    path('settings/accessory-types/', AccessoryTypeListCreateView.as_view(), name='accessory-type-list'),
    path('settings/accessory-types/<int:accessory_type_id>/', AccessoryTypeRetrieveUpdateDestroyView.as_view(), name='accessory-type-detail'),
]



