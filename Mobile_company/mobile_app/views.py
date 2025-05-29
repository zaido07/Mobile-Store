from rest_framework_simplejwt.authentication import JWTAuthentication
from .authentication import *
from rest_framework import status
from django.core.exceptions import ValidationError,FieldError,ObjectDoesNotExist
from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import ValidationError,APIException
from decimal import Decimal
from .models import *
from .serializers import *
from .permissions import *
from rest_framework.filters import OrderingFilter
from django.db.models import Prefetch
from django.db import IntegrityError
from django.db import transaction as db_transaction
from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
### for pdf 
from django.template.loader import get_template
import pdfkit
from django.http import HttpResponse
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
###
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import permissions
from  django.http import JsonResponse 
from django_filters.rest_framework import DjangoFilterBackend
from .filters import *
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from django.db.models import Sum, F, FloatField, Q, Count
from .models import Branch, SoldProduct
from rest_framework.response import Response# views.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenBlacklistView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken

from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

#???????????????????????????????????????????????????????????????????????????????????????
class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filterset_class = CityFilter
    def get_permissions(self):
        if self.action=="list" or self.action=="retrieve":
            return [permissions.AllowAny()]
        else:
            return super().get_permissions()
class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filterset_class =EmployeeFilter
    def get_permissions(self):
        if self.action=="list" or self.action=="retrieve":
            return [permissions.AllowAny()]
        else:
            return super().get_permissions()

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    filterset_class = BranchFilter
    def get_permissions(self):
        if self.action=="list" or self.action=="retrieve":
            return [permissions.AllowAny()]
        return super().get_permissions()

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    def get_permissions(self):
        if self.action=="list" or self.action=="retrieve":
            return [permissions.AllowAny()]
        else:
            return super().get_permissions()


class AccessoriesViewSet(viewsets.ModelViewSet):
    queryset = Accessories.objects.all()
    serializer_class = AccessoriesSerializer



class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer

class PhoneViewSet(viewsets.ModelViewSet):
    queryset = Phone.objects.all()
    serializer_class = PhoneSerializer

class BranchProductsViewSet(viewsets.ModelViewSet):
    queryset = BranchProducts.objects.all()
    serializer_class = BranchProductSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

class SoldProductViewSet(viewsets.ModelViewSet):
    queryset = SoldProduct.objects.all()
    serializer_class = SoldProductSerializer

class BranchOrderViewSet(viewsets.ModelViewSet):
    queryset = BranchOrder.objects.all()
    serializer_class = BranchOrderLogSerializer

class RequestedProductsViewSet(viewsets.ModelViewSet):
    queryset = RequestedProducts.objects.all()
    serializer_class = RequestedProductsSerializer

class ProductTransactionViewSet(viewsets.ModelViewSet):
    queryset = ProductTransaction.objects.all()
    serializer_class = ProductTransactionSerializer

class TransportedProductsViewSet(viewsets.ModelViewSet):
    queryset = TransportedProducts.objects.all()
    serializer_class = TransportedProductsSerializer


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as e:
            return Response({
                'error': 'Authentication failed',
                'detail': str(e.detail)
            }, status=status.HTTP_401_UNAUTHORIZED)
        except InvalidToken as e:
            return Response({
                'error': 'Invalid token',
                'detail': str(e.detail)
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                access_token = auth_header.split(' ')[1]
            else:
                return Response(
                    {'error': 'Authorization header missing or invalid'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            data = request.data.copy()
            data['access'] = access_token
            
            serializer = self.serializer_class(data=data)  
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

####3 Admin 
### company statistics 
class AdminStatisticsView(GenericAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [CustomJWTAuthentication]  
    permission_classes = [IsActiveSuperAdmin]

    def get(self, request):
        
        period = request.query_params.get('period', 'all')
        date_str = request.query_params.get('date', None)

        
        sold_products = SoldProduct.objects.all()
        customers = Customer.objects.all()

        
        if period != 'all' and date_str:
            try:
                if period == 'daily':
                    try:
                        filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except ValueError:
                    
                        filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
            
                    start_datetime = datetime.combine(filter_date, datetime.min.time())
                    end_datetime = datetime.combine(filter_date, datetime.max.time())
                
                    date_filter = Q(purchase_id__date_of_purchase__range=(start_datetime, end_datetime))
                    customer_filter = Q(date_created__date=filter_date)
                elif period == 'monthly':
                    filter_date = datetime.strptime(date_str, '%Y-%m').date()
                    date_filter = (
                        Q(purchase_id__date_of_purchase__year=filter_date.year) &
                        Q(purchase_id__date_of_purchase__month=filter_date.month)
                    )
                    customer_filter = (
                        Q(date_created__year=filter_date.year) &
                        Q(date_created__month=filter_date.month)
                    )
                elif period == 'annual':
                    year = int(date_str)
                    date_filter = Q(purchase_id__date_of_purchase__year=year)
                    customer_filter = Q(date_created__year=year)
                
                sold_products = sold_products.filter(date_filter)
                customers = customers.filter(customer_filter)

            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD for daily, YYYY-MM for monthly, YYYY for annual"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        total_sales = sold_products.aggregate(
            total=Sum(F('selling_price') * F('quantity'), output_field=FloatField()
        ))['total'] or 0

        total_products_sold = sold_products.aggregate(
            total=Sum('quantity')
        )['total'] or 0

        most_sold_product = sold_products.values(
            'product_id__product_name'
        ).annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold').first()

        new_customers_count = customers.aggregate(
            total=Count('customer_id')
        )['total'] or 0
        profits=total_sales-sold_products.aggregate(
            total=Sum(F('main_price') * F('quantity'), output_field=FloatField()
        ))['total'] or 0
        response_data = {
            "period": period,
            "filter_date": date_str,
            "total_sales": round(total_sales, 2),
            "total_products_sold": total_products_sold,
            "profits":profits,
            "most_sold_product": {
                "name": most_sold_product['product_id__product_name'] if most_sold_product else None,
                "quantity": most_sold_product['total_sold'] if most_sold_product else 0
            },
            
            "new_customers": new_customers_count
        }

        return Response(response_data)
    
    ####branch statistics 
    ##############################BranchStatistics####################################



class BranchStatisticsView(GenericAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [CustomJWTAuthentication]  
    permission_classes = [IsActiveSuperAdmin]

    def get(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)

    
        period = request.query_params.get('period', 'all')
        date_str = request.query_params.get('date', None)
        
        sold_products = SoldProduct.objects.filter(purchase_id__branch_id=branch)

        if period != 'all' and date_str:
            try:
                if period == 'daily':
                    try:
                        filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        
                    except ValueError:
                    
                        filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
            
                    start_datetime = datetime.combine(filter_date, datetime.min.time())
                    end_datetime = datetime.combine(filter_date, datetime.max.time())
                
                    date_filter = Q(purchase_id__date_of_purchase__range=(start_datetime, end_datetime))
                    customer_filter = Q(date_created__date=filter_date)
                    sold_products = sold_products.filter(
                        Q(purchase_id__date_of_purchase__year=filter_date.year) &
                        Q(purchase_id__date_of_purchase__month=filter_date.month)&
                        Q(purchase_id__date_of_purchase__day=filter_date.day)
                    )
                elif period == 'monthly':
                    filter_date = datetime.strptime(date_str, '%Y-%m').date()
                    sold_products = sold_products.filter(
                        Q(purchase_id__date_of_purchase__year=filter_date.year) &
                        Q(purchase_id__date_of_purchase__month=filter_date.month)
                    )
                elif period == 'annual':
                    year = int(date_str)
                    sold_products = sold_products.filter(
                        purchase_id__date_of_purchase__year=year
                    )
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD for daily, YYYY-MM for monthly, YYYY for annual"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        total_sales = sold_products.aggregate(
            total=Sum(F('selling_price') * F('quantity'), output_field=FloatField())
        )['total'] or 0

        total_profits = sold_products.aggregate(
            total=Sum((F('selling_price') - F('main_price')) * F('quantity'), output_field=FloatField())
        )['total'] or 0

        total_products_sold = sold_products.aggregate(
            total=Sum('quantity')
        )['total'] or 0

        most_sold_product = sold_products.values(
            'product_id__product_name'
        ).annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold').first()
        response_data = {
            "branch_id": branch.branch_id,
            "period": period,
            "filter_date": date_str,
            "total_sales": round(total_sales, 2),
            "total_profits": round(total_profits, 2),
            "total_products_sold": total_products_sold,
            "most_sold_product": most_sold_product['product_id__product_name'] if most_sold_product else None,
            "most_sold_quantity": most_sold_product['total_sold'] if most_sold_product else 0
        }

        return Response(response_data)
## branch managements a####################
class BranchManagement(GenericAPIView):
    authentication_classes = [CustomJWTAuthentication]  
    permission_classes = [IsActiveSuperAdmin]
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BranchFilter  
    search_fields = ['manager_id__f_name']
    def get_queryset(self):
        return Branch.objects.select_related('manager_id').all()
    
    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = BranchSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AddBranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BranchDetail(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
            serializer = BranchSerializer(branch)
            return Response(serializer.data)
        except Branch.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class BranchOperations(GenericAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [CustomJWTAuthentication] 
    permission_classes = [IsActiveSuperAdmin]

    def put(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
            serializer = BranchSerializer(branch, data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Branch.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    
    def delete(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
            branch.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Branch.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


################# Manages Employee ##########################################
class EmployeeListView(GenericAPIView):
    permission_classes = [IsAdminUser]
    queryset = Employee.objects.all()  
    serializer_class =ManageEmployeeSerializer 
    filter_backends = [DjangoFilterBackend, SearchFilter,OrderingFilter]
    filterset_class = EmployeeFilter
    search_fields = ['f_name']
    ordering_fields = ['f_name', 'l_name', 'id']  
    ordering = ['f_name']
    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset()) 
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class EmployeeDetailView(GenericAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [CustomJWTAuthentication]  
    permission_classes = [IsActiveSuperAdmin]

    def get(self, request, pk):
        employee =Employee.objects.get(pk=pk)
        if not employee:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)

    def put(self, request, pk):
        employee =Employee.objects.get(pk=pk)
        if not employee:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeeSerializer(employee, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        employee =Employee.objects.get(pk=pk)
        if not employee:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AddEmployeeView(GenericAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [CustomJWTAuthentication] 
    permission_classes = [IsActiveSuperAdmin]
    

    def post(self, request):
        profile_image = models.ImageField(upload_to='employee_images/', null=True, blank=True)

        serializer = EmployeeSerializer(data=request.data,files=request.files)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateEmployeeAccountView(GenericAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [CustomJWTAuthentication] 
    permission_classes = [IsActiveSuperAdmin]

    def post(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        required_roles = ['manager', 'hr', 'ceo', 'warehouse manager', 'sales manager']
        if employee.job_id.job_name.lower() not in required_roles:
            return Response({"error": "This job role doesn't require an account"}, 
                          status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get('username')
        password1 = request.data.get('password1')
        password2 = request.data.get('password2')
        
        if not username or not password1 or not password2:
            return Response({"error": "username, password1 and password2 are required"},
                          status=status.HTTP_400_BAD_REQUEST)

        
        if password1 != password2:
            return Response({"error": "Passwords do not match"},
                          status=status.HTTP_400_BAD_REQUEST)


        if len(password1) < 8:
            return Response({"error": "Password must be at least 8 characters long"},
                          status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"},
                          status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(
                username=username,
                password=password1,  
                is_staff=True
            )
            
            employee.user_account = user
            employee.save()

            return Response({
                "message": "Account created successfully",
                "employee_id": employee.id,
                "username": username
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)},
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
###################settings###################################

class CityManagement(GenericAPIView):
    authentication_classes = [CustomJWTAuthentication] 
    permission_classes = [IsActiveSuperAdmin]  
    serializer_class = CitySerializer

    def get(self, request):
        city = City.objects.all()
        serializer = self.get_serializer(city, many=True)
        
            
        return Response({
            "count": city.count(),
            "cities": serializer.data,
            
            
        }, status=status.HTTP_200_OK)
    def post(self, request):
        
        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        
        try:
            city = City.objects.get(pk=pk)
            city.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except City.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class JobManagement(GenericAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [CustomJWTAuthentication] 
    permission_classes = [IsActiveSuperAdmin]
    def get(self,request):
        job = Job.objects.all() 
        serializer = JobSerializer(job, many=True)
        return Response({
            "count": job.count(),
            "jobs": serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            job = Job.objects.get(pk=pk)
            job.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Job.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        

    
    
    
#################################################################################


        
        
        
        
#### ceo #####

##statistics ####
class CeoStatisticsView(GenericAPIView):
    permission_classes = [IsCeo]

    def get(self, request):
        period = request.query_params.get('period', 'all')
        date_str = request.query_params.get('date', None)

        sold_products = SoldProduct.objects.all()
        customers = Customer.objects.all()

        if period != 'all' and date_str:
            try:
                if period == 'daily':
                    filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    date_filter = (
                        Q(purchase_id__date_of_purchase__year=filter_date.year) &
                        Q(purchase_id__date_of_purchase__month=filter_date.month)&
                        Q(purchase_id__date_of_purchase__day=filter_date.day)
                    )
                    customer_filter = Q(date_created__date=filter_date)
                elif period == 'monthly':
                    filter_date = datetime.strptime(date_str, '%Y-%m').date()
                    date_filter = (
                        Q(purchase_id__date_of_purchase__year=filter_date.year) &
                        Q(purchase_id__date_of_purchase__month=filter_date.month)
                    )
                    customer_filter = (
                        Q(date_created__year=filter_date.year) &
                        Q(date_created__month=filter_date.month)
                    )
                elif period == 'annual':
                    year = int(date_str)
                    date_filter = Q(purchase_id__date_of_purchase__year=year)
                    customer_filter = Q(date_created__year=year)
                
                sold_products = sold_products.filter(date_filter)
                customers = customers.filter(customer_filter)

            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD for daily, YYYY-MM for monthly, YYYY for annual"},
                    status=status.HTTP_400_BAD_REQUEST
                )

    
        total_sales = sold_products.aggregate(
            total=Sum(F('selling_price') * F('quantity'), output_field=FloatField())
        )['total'] or 0

        total_products_sold = sold_products.aggregate(
            total=Sum('quantity')
        )['total'] or 0

        most_sold_product = sold_products.values(
            'product_id__product_name'
        ).annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold').first()

        new_customers_count = customers.aggregate(
            total=Count('customer_id')
        )['total'] or 0

        response_data = {
            "period": period,
            "filter_date": date_str,
            "total_sales": round(total_sales, 2),
            "total_products_sold": total_products_sold,
            "most_sold_product": {
                "name": most_sold_product['product_id__product_name'] if most_sold_product else None,
                "quantity": most_sold_product['total_sold'] if most_sold_product else 0
            },
            "new_customers": new_customers_count
        }

        return Response(response_data)
    
## Branch Statistics ##
class CeoBranchStatisticsView(GenericAPIView):
    permission_classes = [IsCeo]

    def get(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)

        
        period = request.query_params.get('period', 'all')
        date_str = request.query_params.get('date', None)
        

        sold_products = SoldProduct.objects.filter(purchase_id__branch_id=branch)

    
        if period != 'all' and date_str:
            try:
                if period == 'daily':
                    filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    sold_products = sold_products.filter(
                        purchase_id__date_of_purchase__date=filter_date
                    )
                elif period == 'monthly':
                    filter_date = datetime.strptime(date_str, '%Y-%m').date()
                    sold_products = sold_products.filter(
                        Q(purchase_id__date_of_purchase__year=filter_date.year) &
                        Q(purchase_id__date_of_purchase__month=filter_date.month)
                    )
                elif period == 'annual':
                    year = int(date_str)
                    sold_products = sold_products.filter(
                        purchase_id__date_of_purchase__year=year
                    )
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD for daily, YYYY-MM for monthly, YYYY for annual"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        
        total_sales = sold_products.aggregate(
            total=Sum(F('selling_price') * F('quantity'), output_field=FloatField())
        )['total'] or 0

        total_profits = sold_products.aggregate(
            total=Sum((F('selling_price') - F('main_price')) * F('quantity'), output_field=FloatField())
        )['total'] or 0

        total_products_sold = sold_products.aggregate(
            total=Sum('quantity')
        )['total'] or 0

        most_sold_product = sold_products.values(
            'product_id__product_name'
        ).annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold').first()

        response_data = {
            "branch_id": branch.branch_id,
            "branch_location": branch.location,
            "period": period,
            "filter_date": date_str,
            "total_sales": round(total_sales, 2),
            "total_profits": round(total_profits, 2),
            "total_products_sold": total_products_sold,
            "most_sold_product": {
                "name": most_sold_product['product_id__product_name'] if most_sold_product else None,
                "quantity": most_sold_product['total_sold'] if most_sold_product else 0
            }
        }

        return Response(response_data)
    

## branches "" 
class CeoBranchManagement(GenericAPIView):
    permission_classes = [IsCeo]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BranchFilter  
    search_fields = ['location']  
    def get_queryset(self):
        return Employee.objects.all()
    def get(self, request):
        queryset = Branch.objects.all()
        
        
        filtered_queryset = self.filter_queryset(queryset)
        
        serializer = BranchSerializer(filtered_queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CeoBranchDetail(GenericAPIView):
    permission_classes = [IsCeo]

    def get(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
            serializer = BranchSerializer(branch)
            return Response(serializer.data)
        except Branch.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class CeoBranchOperations(GenericAPIView):
    permission_classes = [IsCeo]

    
    def put(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
            serializer = BranchSerializer(branch, data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Branch.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


    def delete(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
            branch.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Branch.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
## setting is add city 
class CeoCityManagement(GenericAPIView):
    permission_classes = [IsCeo]
    def get(self,request):
        city = City.objects.all()
        serializer = CitySerializer(city, many=True)
        return Response({
            "count": city.count(),
            "cities": serializer.data,
            
            
        }, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, pk):
        try:
            city = City.objects.get(pk=pk)
            city.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except City.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


## ceo browse employees 
class CeoEmployeeListView(GenericAPIView):
    permission_classes = [IsCeo]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class=EmployeeFilter
    search_fields = ['f_name']
    def get_queryset(self):
        return Employee.objects.all()
    def get(self, request):
        queryset = Employee.objects.all()
        
        
        filtered_queryset = self.filter_queryset(queryset)
        
        serializer = ManageEmployeeSerializer(filtered_queryset, many=True)
        return Response(serializer.data)
class CeoEmployeeDetailView(GenericAPIView):
    permission_classes = [IsCeo]

    def get(self, request, pk):
        employee =Employee.objects.get(pk=pk)
        if not employee:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)



## Hr PAGE###


                
                
class HrEmployeeListView(GenericAPIView):
    permission_classes = [IsHr]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class=EmployeeFilter
    search_fields = ['f_name']
    def get_queryset(self):
        return Employee.objects.all()
    def get(self, request):
        queryset = Employee.objects.all()
        
        filtered_queryset = self.filter_queryset(queryset)
        
        serializer = ManageEmployeeSerializer(filtered_queryset, many=True)
        return Response(serializer.data)
class HrEmployeeDetailView(GenericAPIView):
    permission_classes = [IsHr]

    def get(self, request, pk):
        employee =Employee.objects.get(pk=pk)
        if not employee:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)

    def put(self, request, pk):
        employee =Employee.objects.get(pk=pk)
        if not employee:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeeSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        employee =Employee.objects.get(pk=pk)
        if not employee:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class HrAddEmployeeView(GenericAPIView):
    permission_classes = [IsHr]

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HrCreateEmployeeAccountView(GenericAPIView):
    permission_classes = [IsHr]

    def post(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        required_roles = ['manager', 'hr', 'ceo', 'warehouse manager', 'sales manager']
        if employee.job_id.job_name.lower() not in required_roles:
            return Response({"error": "This job role doesn't require an account"}, 
                            status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({"error": "Username and password are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            password=password,
            is_staff=True
        )
        
        employee.user_account = user
        employee.save()

        return Response({
            "message": "Account created successfully",
            "employee_id": employee.id,
            "username": username
        }, status=status.HTTP_201_CREATED)
        
        
        
## hr settings to manage jobs and jobs titles 
class HrJobManagement(GenericAPIView):
    permission_classes = [IsHr]
    def get(self,request):
        job = Job.objects.all() 
        serializer = JobSerializer(job, many=True)
        return Response({
            "count": job.count(),
            "jobs": serializer.data
        }, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            job = Job.objects.get(pk=pk)
            job.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Job.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        

#Sales Manager
##  branch product 
class SalesManagerProductsView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['product_id__product_name']

    def get(self, request):
        try:
            # Get employee and branch info
            employee = request.user.employee
            if not employee or not employee.branch_id:
                return Response(
                    {"error": "Branch information not found for this user."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            branch = employee.branch_id

            branch_products = BranchProducts.objects.filter(
                branch_id=branch,
                quantity__gt=0
            ).select_related(
                'product_id__category_id',
                'product_id__phones__brand_id',
                'product_id__phones__color_id',
                'product_id__phones__camera_id'
            )

    
            product_ids = branch_products.values_list('product_id', flat=True)


            filtered_products = self.filterset_class(
                request.GET,
                queryset=Product.objects.filter(pk__in=product_ids)
            ).qs

            filtered_branch_products = branch_products.filter(
                product_id__in=filtered_products.values_list('pk', flat=True)
            )

            response_data = []
            for bp in filtered_branch_products:
                product = bp.product_id
                product_data = {
                    'product_id': product.product_id,
                    'product_name': product.product_name,
                    'category': product.category_id.category_name,
                    'main_price': float(product.main_price),
                    'sale_price': float(product.sale_price),
                    'branch_quantity': bp.quantity,
                }

                if hasattr(product, 'phone'):
                    phones = product.phone
                    product_data.update({
                        'brand': phones.brand_id.brand_name,
                        'color': phones.color_id.color_name,
                        'storage': phones.storage,
                        'battery': phones.battery,
                        'front_camera': phones.camera_id.front_camera,
                        'back_camera': phones.camera_id.back_camera,
                        'ram': phones.ram,
                        'display_size': float(phones.display_size)
                    })

                response_data.append(product_data)

            return Response(response_data)

        except AttributeError as e:
            return Response(
                {"error": "Employee record not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            


### make sale 



class MakeSaleView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSaleManager]

    @transaction.atomic
    def post(self, request):
        serializer = MakeSaleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            
            branch = request.user.employee.branch_id
            
        
            customer = get_object_or_404(Customer, pk=serializer.validated_data['customer_id'])

            
            products_data = []
            for item in serializer.validated_data['products']:
                product_id = item['product_id']
                quantity = item['quantity']

                try:
                    branch_product = BranchProducts.objects.select_for_update().get(
                        branch_id=branch,
                        product_id=product_id,
                        quantity__gte=quantity
                    )
                    products_data.append({
                        'branch_product': branch_product,
                        'product': branch_product.product_id,
                        'quantity': quantity,
                        'total_price': branch_product.product_id.sale_price * quantity
                    })
                except BranchProducts.DoesNotExist:
                    return Response(
                        {"error": f"Product ID {product_id} only has {branch_product.quantity} available (requested {quantity})"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            purchase = Purchase.objects.create(
                branch_id=branch,
                customer_id=customer,
                date_of_purchase=timezone.now()
            )

            sold_products = []
            grand_total = 0
            
            for product_info in products_data:
                
                SoldProduct.objects.create(
                    purchase_id=purchase,
                    product_id=product_info['product'],
                    quantity=product_info['quantity'],
                    main_price=product_info['product'].main_price,
                    selling_price=product_info['product'].sale_price
                )

                
                product_info['branch_product'].quantity -= product_info['quantity']
                product_info['branch_product'].save()

                sold_products.append({
                    'product_id': product_info['product'].product_id,
                    'product_name': product_info['product'].product_name,
                    'quantity': product_info['quantity'],
                    'unit_price': float(product_info['product'].sale_price),
                    'total_price': float(product_info['total_price'])
                })
                grand_total += product_info['total_price']

            return Response({
                'success': True,
                'purchase_id': purchase.purchase_id,
                'customer': {
                    'name': f"{customer.first_name} {customer.middle_name} {customer.last_name}",
                    'national_num': customer.national_num
                },
                'products': sold_products,
                'grand_total': float(grand_total),
                'branch': branch.location,
                'date': purchase.date_of_purchase.strftime('%Y-%m-%d %H:%M:%S')
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
        
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        full_name = request.query_params.get('full_name')
        national_num = request.query_params.get('national_num')

        queryset = Customer.objects.all()

        
        if national_num:
            queryset = queryset.filter(national_num=national_num)

        
        elif full_name:
            parts = full_name.strip().split()
            if len(parts) == 3:
                queryset = queryset.filter(
                    first_name__iexact=parts[0],
                    middle_name__iexact=parts[1],
                    last_name__iexact=parts[2]
                )
            else:
                return Response(
                    {"error": "Full name must include first, middle, and last name."},
                    status=400
                )

        serializer = CustomerSerializer(queryset, many=True)
        return Response(serializer.data)

class CustomerSearchView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    def get(self, request):
        
        search_query = request.query_params.get('q', '').strip()
        
        if len(search_query) < 3:
            return Response(
                {"error": "Search query must be at least 3 characters"},
                status=status.HTTP_400_BAD_REQUEST
            )

        customers = Customer.objects.filter(
            Q(first_name__icontains=search_query) |
            Q(middle_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(national_num__icontains=search_query)
        )[:10]  

        serializer = CustomerSearchSerializer(customers, many=True)
        return Response(serializer.data)

### add customer 
class AddCustomerView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def post(self, request):

        serializer = AddCustomerSerializer(data=request.data)
        if serializer.is_valid():
            try:
                
                national_num = serializer.validated_data['national_num']
                if Customer.objects.filter(national_num=national_num).exists():
                    return Response(
                        {"error": "Customer with this national number already exists"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                
                customer = serializer.save()
                
                return Response({
                    "success": True,
                    "customer_id": customer.customer_id,
                    "message": "Customer added successfully",
                    "customer": {
                        "full_name": f"{customer.first_name} {customer.middle_name} {customer.last_name}",
                        "national_num": customer.national_num,
                        "phone_num": customer.phone_num
                    }
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
    ### customer shows and crud 
class CustomerListView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def get(self, request):
        search_query = request.query_params.get('search', '').strip()
        
        customers = Customer.objects.all()
        
        if search_query:
            customers = customers.filter(
                models.Q(first_name__icontains=search_query) |
                models.Q(middle_name__icontains=search_query) |
                models.Q(last_name__icontains=search_query) |
                models.Q(national_num__icontains=search_query) |
                models.Q(phone_num__icontains=search_query)
            )
        
        serializer = CustomerSerializer(customers.order_by('-date_created')[:100], many=True)
        return Response(serializer.data)

class CustomerDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def get(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    
    def put(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        
        if serializer.is_valid():
            if 'national_num' in request.data and request.data['national_num'] != customer.national_num:
                if Customer.objects.filter(national_num=request.data['national_num']).exists():
                    return Response(
                        {"error": "Customer with this national number already exists"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        customer.delete()
        return Response(
            {"success": True, "message": "Customer deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
        
        
### customer sales log 

class CustomerSalesView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    serializer_class = CustomerSaleSerializer
    
    def get(self, request, customer_pk, purchase_pk=None):
        customer = get_object_or_404(Customer, pk=customer_pk)
        
        if purchase_pk:
            return self._get_sale_detail(customer, purchase_pk)
        return self._get_customer_sales(customer)
    
    def _get_sale_detail(self, customer, purchase_pk):
        try:
            purchase = Purchase.objects.get(
                pk=purchase_pk,
                customer_id=customer
            )
            
            sold_products = SoldProduct.objects.filter(
                purchase_id=purchase
            ).select_related(
                'product_id__category_id',
                'purchase_id__branch_id'
            )
            
            serializer = SaleDetailSerializer(sold_products, many=True)
            
            purchase_date = purchase.date_of_purchase.strftime('%Y-%m-%d')
            
            grand_total = sum(item.selling_price * item.quantity for item in sold_products)
            total_items = sum(item.quantity for item in sold_products)
            
            return Response({
                'purchase_id': purchase_pk,
                'customer_id': customer.customer_id,
                'date': purchase_date, 
                'branch': purchase.branch_id.location,
                'products': serializer.data,
                'grand_total': grand_total,
                'total_items': total_items
            })
            
        except Purchase.DoesNotExist:
            return Response(
                {"error": "Purchase not found for this customer"},
                status=status.HTTP_404_NOT_FOUND
            )

    def _get_customer_sales(self, customer):
        purchases = Purchase.objects.filter(
            customer_id=customer
        ).prefetch_related('soldproduct_set').order_by('-date_of_purchase')
        
        sales_data = []
        for purchase in purchases:
            sold_products = purchase.soldproduct_set.all()
            total_spent = sum(sp.selling_price * sp.quantity for sp in sold_products)
            total_products = sum(sp.quantity for sp in sold_products)
            
            sales_data.append({
                'purchase_id': purchase.purchase_id,
                'date_of_purchase': purchase.date_of_purchase.strftime('%Y-%m-%d'),
                'branch_id': purchase.branch_id.branch_id,
                'total_spent': total_spent,
                'total_products': total_products
            })
        
        return Response({
            'customer_id': customer.customer_id,
            'customer_name': f"{customer.first_name} {customer.last_name}",
            'national_num': customer.national_num,
            'total_purchases': purchases.count(),
            'sales': sales_data
        })
        
        
### sold products log

class SoldProductLogView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def get(self, request):
        
        branch = request.user.employee.branch_id
        
        
        search_query = request.query_params.get('search', '')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        purchases = Purchase.objects.filter(branch_id=branch)
        if search_query:
            purchases = purchases.filter(
                Q(purchase_id__icontains=search_query) |
                Q(customer_id__first_name__icontains=search_query) |
                Q(customer_id__last_name__icontains=search_query)
            )
        
        if date_from:
            purchases = purchases.filter(date_of_purchase__gte=date_from)
        
        if date_to:
            purchases = purchases.filter(date_of_purchase__lte=date_to)
        
        purchases = purchases.order_by('-date_of_purchase')
        ordering = self.request.query_params.get('ordering')
        if ordering:
            purchases = purchases.order_by(*ordering.split(','))
        else:
            purchases = purchases.order_by('-date_of_purchase')
        
        serializer = PurchaseLogSerializer(purchases, many=True)
        return Response(serializer.data)

class PurchaseDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def get(self, request, purchase_id):
        purchase = get_object_or_404(
            Purchase,
            purchase_id=purchase_id,
            branch_id=request.user.employee.branch_id
        )
        
        sold_products = SoldProduct.objects.filter(
            purchase_id=purchase
        ).select_related('product_id__category_id')
        
        products_serializer = SoldProductDetailSerializer(sold_products, many=True)
        

        grand_total = sum(item.selling_price * item.quantity for item in sold_products)
        total_items = sum(item.quantity for item in sold_products)
        
        return Response({
            'purchase_id': purchase.purchase_id,
            'date': purchase.date_of_purchase,
            'customer': {
                'id': purchase.customer_id.customer_id,
                'name': f"{purchase.customer_id.first_name} {purchase.customer_id.last_name}",
                'national_num': purchase.customer_id.national_num
            },
            'branch': purchase.branch_id.location,
            'products': products_serializer.data,
            'grand_total': grand_total,
            'total_items': total_items
        })

## sales manager bill 

class GenerateBillView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    filter_backends=[DjangoFilterBackend,OrderingFilter]
    ordering_fields = ['date_of_purchase', 'purchase_id'] 
    ordering = ['-date_of_purchase']
    
    def get(self, request, purchase_id):
        try:
            purchase = get_object_or_404(
                Purchase,
                purchase_id=purchase_id,
                branch_id=request.user.employee.branch_id
            )
            
            sold_products = SoldProduct.objects.filter(
                purchase_id=purchase
            ).select_related('product_id__category_id')
            
            products_data = []
            grand_total = 0
            
            for item in sold_products:
                product_total = item.selling_price * item.quantity
                grand_total += product_total
                
                products_data.append({
                    'name': item.product_id.product_name,
                    'category': item.product_id.category_id.category_name,
                    'quantity': item.quantity,
                    'unit_price': "{:.2f}".format(item.selling_price),
                    'total': "{:.2f}".format(product_total)
                })
            
            context = {
                'purchase_id': purchase.purchase_id,
                'date': purchase.date_of_purchase.strftime('%Y-%m-%d %H:%M:%S'),
                'branch': purchase.branch_id.location,
                'customer': {
                    'name': f"{purchase.customer_id.first_name} {purchase.customer_id.last_name}",
                    'national_num': purchase.customer_id.national_num
                },
                'products': products_data,
                'grand_total': "{:.2f}".format(grand_total)
            }
            
            return Response(context, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GenerateBillPDFView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def get(self, request, purchase_id):
        try:
            purchase = get_object_or_404(
                Purchase,
                purchase_id=purchase_id,
                branch_id=request.user.employee.branch_id
            )
            
            sold_products = SoldProduct.objects.filter(
                purchase_id=purchase
            ).select_related('product_id__category_id')
            
            products_data = []
            grand_total = 0
            
            for item in sold_products:
                product_total = item.selling_price * item.quantity
                grand_total += product_total
                
                products_data.append({
                    'name': item.product_id.product_name,
                    'category': item.product_id.category_id.category_name,
                    'quantity': item.quantity,
                    'unit_price': "{:.2f}".format(item.selling_price),
                    'total': "{:.2f}".format(product_total)
                })
            
            context = {
                'purchase_id': purchase.purchase_id,
                'date': purchase.date_of_purchase.strftime('%Y-%m-%d %H:%M:%S'),
                'branch': purchase.branch_id.location,
                'customer': {
                    'name': f"{purchase.customer_id.first_name} {purchase.customer_id.last_name}",
                    'national_num': purchase.customer_id.national_num
                },
                'products': products_data,
                'grand_total': "{:.2f}".format(grand_total)
            }
            
            template = get_template('bill_template.html')
            html = template.render(context)
            

            options = {
                'page-size': 'A5',
                'margin-top': '0mm',
                'margin-right': '0mm',
                'margin-bottom': '0mm',
                'margin-left': '0mm',
                'encoding': "UTF-8",
                'quiet': ''
            }
            config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe') 

            pdf = pdfkit.from_string(html, False, options=options, configuration=config)
            
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="bill_{purchase_id}.pdf"'
            return response
            
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
##Branch manager 

## branch manager statistics 

class BranchManagerStatisticsView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        try:

            employee = request.user.employee
            branch = employee.branch_id
        except AttributeError:
            return Response(
                {"error": "Employee record not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        period = request.query_params.get('period', 'all')  
        date_str = request.query_params.get('date', None)
        
        sold_products = SoldProduct.objects.filter(purchase_id__branch_id=branch)

        if period != 'all' and date_str:
            try:
                if period == 'daily':
                    filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    sold_products = sold_products.filter(
                        Q(purchase_id__date_of_purchase__year=filter_date.year) &
                        Q(purchase_id__date_of_purchase__month=filter_date.month)&
                        Q(purchase_id__date_of_purchase__month=filter_date.day)
                    )
                
                    start_datetime = datetime.combine(filter_date, datetime.min.time())
                    end_datetime = datetime.combine(filter_date, datetime.max.time())
                
                    date_filter = Q(purchase_id__date_of_purchase__range=(start_datetime, end_datetime))
                    customer_filter = Q(date_created__date=filter_date)
                elif period == 'monthly':
                    filter_date = datetime.strptime(date_str, '%Y-%m').date()
                    sold_products = sold_products.filter(
                        Q(purchase_id__date_of_purchase__year=filter_date.year) &
                        Q(purchase_id__date_of_purchase__month=filter_date.month)
                    )
                elif period == 'annual':
                    year = int(date_str)
                    sold_products = sold_products.filter(
                        purchase_id__date_of_purchase__year=year
                    )
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD for daily, YYYY-MM for monthly, YYYY for annual"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        total_sales = sold_products.aggregate(
            total=Sum(F('selling_price') * F('quantity'))
        )['total'] or 0

        total_profits = sold_products.aggregate(
            total=Sum((F('selling_price') - F('main_price')) * F('quantity'))
        )['total'] or 0

        total_products_sold = sold_products.aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        most_sold_product = sold_products.values(
            'product_id__product_id',
            'product_id__product_name',
            'product_id__category_id__category_name'
        ).annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum(F('selling_price') * F('quantity'))
        ).order_by('-total_sold').first()

        response_data = {
            "branch_id": branch.branch_id,
            "branch_location": branch.location,
            "period": period,
            "filter_date": date_str,
            "total_sales": float(total_sales),
            "total_profits": float(total_profits),
            "total_products_sold": total_products_sold,
            "most_sold_product": {
                "product_id": most_sold_product['product_id__product_id'] if most_sold_product else None,
                "product_name": most_sold_product['product_id__product_name'] if most_sold_product else None,
                "category": most_sold_product['product_id__category_id__category_name'] if most_sold_product else None,
                "quantity_sold": most_sold_product['total_sold'] if most_sold_product else 0,
                "total_revenue": float(most_sold_product['total_revenue']) if most_sold_product else 0
            }
        }

        return Response(response_data)
    
### products 
class BranchManagerProductsView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['product_id__product_name']

    def get(self, request):
        try:
        
            employee = request.user.employee
            if not employee or not employee.branch_id:
                return Response(
                    {"error": "Branch information not found for this user."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            branch = employee.branch_id

            
            branch_products = BranchProducts.objects.filter(
                branch_id=branch,
                quantity__gt=0
            ).select_related(
                'product_id__category_id',
                'product_id__phones__brand_id',
                'product_id__phones__color_id',
                'product_id__phones__camera_id'
            )

            # Get the product IDs first
            product_ids = branch_products.values_list('product_id', flat=True)

            # Apply filters to the Product queryset
            filtered_products = self.filterset_class(
                request.GET,
                queryset=Product.objects.filter(pk__in=product_ids)
            ).qs

            # Get the filtered branch products
            filtered_branch_products = branch_products.filter(
                product_id__in=filtered_products.values_list('pk', flat=True)
            )

            response_data = []
            for bp in filtered_branch_products:
                product = bp.product_id
                product_data = {
                    'product_id': product.product_id,
                    'product_name': product.product_name,
                    'category': product.category_id.category_name,
                    'main_price': float(product.main_price),
                    'sale_price': float(product.sale_price),
                    'branch_quantity': bp.quantity,
                }

                # Handle phone-specific data
                if hasattr(product, 'phone'):
                    phones = product.phone
                    product_data.update({
                        'brand': phones.brand_id.brand_name,
                        'color': phones.color_id.color_name,
                        'storage': phones.storage,
                        'battery': phones.battery,
                        'front_camera': phones.camera_id.front_camera,
                        'back_camera': phones.camera_id.back_camera,
                        'ram': phones.ram,
                        'display_size': float(phones.display_size)
                    })

                response_data.append(product_data)

            return Response(response_data)

        except AttributeError as e:
            return Response(
                {"error": "Employee record not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

            
            
            
class BranchManagerPhoneDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, pk):
        branch = request.user.employee.branch_id
        
        try:
            phone = Phone.objects.get(
                product_id=pk,
                product_id__branchproducts__branch_id=branch
            )
            serializer = PhoneSerializer(phone)
            return Response(serializer.data)
        except Phone.DoesNotExist:
            return Response(
                {"error": "Phone not found in your branch"}, 
                status=status.HTTP_404_NOT_FOUND
            )

class BranchManagerAccessoryDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, pk):
        branch = request.user.employee.branch_id
        
        try:
            accessory = Accessories.objects.get(
                product_id=pk,
                product_id__branchproducts__branch_id=branch
            )
            serializer = AccessoriesSerializer(accessory)
            return Response(serializer.data)
        except Accessories.DoesNotExist:
            return Response(
                {"error": "Accessory not found in your branch"}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
            
### order products 
class BranchManagerOrderProductsView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = CreateBranchOrderSerializer 
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['product_name']

    @transaction.atomic
    def post(self, request):
        
        try:
            branch = request.user.employee.branch_id
            
            # Validate input with our custom serializer
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            order = BranchOrder.objects.create(
                branch_id=branch, 
                note=serializer.validated_data.get('note', ''),
                date_of_order=timezone.now(), 
                is_done=False 
            )

            results = []
            for product_item in serializer.validated_data['products']:
                product_id = product_item['product_id']
                quantity = product_item['quantity']

                try:
                    product = Product.objects.get(pk=product_id)
                    
                    RequestedProducts.objects.create(
                        order_id=order,
                        product_id=product,
                        quantity=quantity,
                        status='P' 
                    )
                    
                    results.append({
                        "product_id": product_id,
                        "status": "success",
                        "quantity": quantity
                    })
                    
                except Product.DoesNotExist:
                    results.append({
                        "product_id": product_id,
                        "status": "failed",
                        "reason": "Product not found"
                    })
                except Exception as e:
                    results.append({
                        "product_id": product_id,
                        "status": "failed",
                        "reason": str(e)
                    })

            return Response({
                "success": True,
                "order_id": order.order_id,
                "branch_id": branch.branch_id,
                "products": results,
                "note": order.note,
                "date_ordered": order.date_of_order,
                "message": "Order created successfully"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
            
            try:
                queryset = Product.objects.filter(quantity__gt=0).select_related('category_id')
                queryset = self.filter_queryset(queryset)

                params = request.query_params
                category_name = params.get('category')
                min_price = params.get('min_price')
                max_price = params.get('max_price')

                if min_price:
                    queryset = queryset.filter(sale_price__gte=min_price)
                if max_price:
                    queryset = queryset.filter(sale_price__lte=max_price)

                if category_name:
                    queryset = queryset.filter(category_id__category_name__iexact=category_name)

                phone_filters = {}
                if params.get('brand'):
                    phone_filters['phones__brand_id__brand_name__iexact'] = params['brand']
                if params.get('color'):
                    phone_filters['phones__color_id__color_name__iexact'] = params['color']
                if params.get('min_storage'):
                    phone_filters['phones__storage__gte'] = params['min_storage']
                if params.get('max_storage'):
                    phone_filters['phones__storage__lte'] = params['max_storage']
                if params.get('min_ram'):
                    phone_filters['phones__ram__gte'] = params['min_ram']
                if params.get('has_sd_card'):
                    phone_filters['phones__sd_card'] = params['has_sd_card'].lower() == 'true'

                if phone_filters:
                    queryset = queryset.filter(
                        Q(category_id__category_name__iexact='phone') | 
                        Q(category_id__category_name__iexact='mobile'),
                        **phone_filters
                    )

                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                
                products_data = []
                for product in queryset:
                    product_data = {
                        'product_id': product.product_id,
                        'product_name': product.product_name,
                        'category': product.category_id.category_name,
                        'main_price': float(product.main_price),
                        'sale_price': float(product.sale_price),
                        'warehouse_quantity': product.quantity
                    }

                    if product.category_id.category_name.lower() in ['phone', 'mobile']:
                        try:
                            phone = Phone.objects.get(product_id=product.product_id)
                            product_data.update({
                                'brand': phone.brand_id.brand_name,
                                'color': phone.color_id.color_name,
                                'storage': phone.storage,
                                'ram': phone.ram,
                                'has_sd_card': phone.sd_card,
                                'display_size': float(phone.display_size)
                            })
                        except Phone.DoesNotExist:
                            pass

                    products_data.append(product_data)

                return Response(products_data)

            except Exception as e:
                return Response({
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
            
### branch manager requested product logs view 

class OrderLogsView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = OrderLogSerializer
    filter_backends=[DjangoFilterBackend,OrderingFilter]
    filterset_class=BranchOrderFilter
    pagination_class = PageNumberPagination
    ordering_fields = ['date_of_order', 'order_id', 'total_quantity']
    ordering = ['-date_of_order']

    def get_queryset(self):
        branch = self.request.user.employee.branch_id
        return BranchOrder.objects.filter(
        branch_id=branch
    ).annotate(
        total_items=Count('requestedproducts_set'),
        total_quantity=Sum('requestedproducts_set__quantity')
    ).select_related('branch_id').prefetch_related('requestedproducts_set')

    def get(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            sort_order = request.query_params.get('sort', 'desc').lower()
            sort_by = request.query_params.get('sort_by', 'date_of_order')
            
            valid_sort_fields = ['date_of_order', 'order_id', 'total_quantity']
            if sort_by not in valid_sort_fields:
                return Response(
                    {"error": f"Invalid sort field. Choose from: {valid_sort_fields}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if sort_order == 'asc':
                queryset = queryset.order_by(sort_by)
            else:
                queryset = queryset.order_by(f'-{sort_by}')

            # 
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OrderDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = OrderDetailSerializer

    def get(self, request, order_id):
        try:
            branch = request.user.employee.branch_id
            order = BranchOrder.objects.get(
                order_id=order_id,
                branch_id=branch
            )
            
            requested_products = order.requestedproducts_set.select_related(
                'product_id',
                'product_id__category_id'
            ).all()
            
            serializer = self.get_serializer(requested_products, many=True)
            
            return Response({
                "order_id": order.order_id,
                "branch": order.branch_id.location,
                "date": order.date_of_order,
                "note": order.note,
                "is_done": order.is_done,
                "products": serializer.data
            })
            
        except ObjectDoesNotExist:
            return Response(
                {"error": "Order not found or not accessible"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

### sold products for branch manager 
class SoldProductsLogView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    filter_backends = [SearchFilter]
    search_fields = ['customer_id__first_name', 'customer_id__last_name', 'customer_id__national_num']

    def get(self, request):
        branch = request.user.employee.branch_id
        
        order_by = request.query_params.get('order_by', '-date_of_purchase')
        search_query = request.query_params.get('search', None)
        
        purchases = Purchase.objects.filter(
            branch_id=branch
        ).annotate(
            total_price=Sum(F('soldproduct__selling_price') * F('soldproduct__quantity')),
            total_items=Sum('soldproduct__quantity')
        ).select_related('customer_id')
        
        if search_query:
            purchases = purchases.filter(
                Q(customer_id__first_name__icontains=search_query) |
                Q(customer_id__last_name__icontains=search_query) |
                Q(customer_id__national_num__exact=search_query)
            )
        
        purchases = purchases.order_by(order_by.replace('total_amount', 'total_price'))
        
        serializer = SoldProductsLogSerializer(purchases, many=True)
        return Response(serializer.data)

class SoldProductPurchaseDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, purchase_id):
        branch = request.user.employee.branch_id
        
        purchase = get_object_or_404(
            Purchase,
            branch_id=branch,
            purchase_id=purchase_id
        )
        
        sold_products = purchase.soldproduct_set.select_related(
            'product_id__category_id'
        ).all()
        
        serializer = SoldProductDetailSerializer(sold_products, many=True)
        
        response_data = {
            "purchase_id": purchase.purchase_id,
            "date_of_purchase": purchase.date_of_purchase,
            "customer_name": f"{purchase.customer_id.first_name} {purchase.customer_id.last_name}",
            "products": serializer.data,
            "grand_total": sum(item['total_price'] for item in serializer.data),
            "total_items": sum(item['quantity'] for item in serializer.data)
        }
        
        return Response(response_data)
    
    
### WareHOUSE


class WarehouseProductView(GenericAPIView):#used
    permission_classes = [IsWarehouseManager]
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter

    def get_queryset(self):
        return Product.objects.filter(quantity__gt=0)\
                             .select_related('category_id')\
                             .prefetch_related('phone')  

    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
class PhoneManagementView(GenericAPIView):#used
    permission_classes=[IsWarehouseManager]
    serializer_class=PhoneSerializer
    def get_phone(self,pk):
        try:
            return Phone.objects.get(product_id=pk)
        except Phone.DoesNotExist:
                return None

    def get(self, request,pk):
        phone =self.get_phone(pk)
        if not phone:
            return Response(
                {"error": "Phone not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(phone)
        return Response(serializer.data)
    

    def put(self,request,pk):
        phone=self.get_phone(pk)
        if not phone:
            return Response({"error":"phone not found"},status=status.HTTP_404_NOT_FOUND)
        serializer=PhoneSerializer(phone,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_404_NOT_FOUND)
    
    def delete(self,request,pk):
        phone=self.get_phone(pk)
        if not phone:
            return Response({"error":"phone not phound"},status=status.HTTP_404_NOT_FOUND)
        phone.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccessoryManagementView(GenericAPIView):#used
    permission_classes = [IsWarehouseManager]
    serializer_class = AccessoriesSerializer
    
    def get_accessory(self, pk):
        try:
            return Accessories.objects.get(product_id=pk)
        except Accessories.DoesNotExist:
            return None
    
    def get(self, request, pk):
        accessory = self.get_accessory(pk)
        if not accessory:
            return Response({"error": "Accessory not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(accessory)
        return Response(serializer.data)
    
    def put(self,request,pk):
            accessory=self.get_accessory(pk)
            if not accessory:
                return Response({"error":"accessory not found"},status=status.HTTP_404_NOT_FOUND)
            serializer=AccessoriesSerializer(accessory,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,status=status.HTTP_404_NOT_FOUND)
    
    
    def delete(self, request, pk):
        accessory = self.get_accessory(pk)
        if not accessory:
            return Response({"error": "Accessory not found"}, status=status.HTTP_404_NOT_FOUND)
        
        accessory.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddProduct(GenericAPIView):#used
    permission_classes = [IsWarehouseManager]
    serializer_class = ProductSerializer

    @transaction.atomic
    def post(self, request):
        try:
            data = request.data.copy()
            self._validate_base_product_data(data)

            if Product.objects.filter(product_name=data['product_name']).exists():
                raise ValidationError("Product with this name already exists")

            category = self._get_valid_category(data['category_id'])

            if category.category_name.lower() in ['phone', 'mobile']:
                phone_data = self._validate_phone_data(data)
            else:
                accessory_data = self._validate_accessory_data(data)

            product_serializer = self.get_serializer(data=data)
            product_serializer.is_valid(raise_exception=True)
            product = product_serializer.save()

            if category.category_name.lower() in ['phone', 'mobile']:
                phone_data['product_id'] = product.product_id
                phone_serializer = PhoneSerializer(data=phone_data)
                phone_serializer.is_valid(raise_exception=True)
                phone_serializer.save()
            else:
                accessory_data['product_id'] = product.product_id
                accessory_serializer = AccessoriesSerializer(data=accessory_data)
                accessory_serializer.is_valid(raise_exception=True)
                accessory_serializer.save()

            return Response(product_serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": e.detail if hasattr(e, 'detail') else str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _validate_base_product_data(self, data):
        required_fields = {
        'product_name': str,
        'category_id': int,
        'main_price': (int, float, Decimal),
        'sale_price': (int, float, Decimal),
        'quantity': int
    }

        errors = {}

        for field, field_type in required_fields.items():
            if field not in data:
                errors[field] = "This field is required"
                continue

            try:
                if isinstance(field_type, tuple):
                    data[field] = Decimal(str(data[field]))
                else:
                    data[field] = field_type(data[field])
            except (TypeError, ValueError):
                errors[field] = f"Invalid value. Expected {field_type if isinstance(field_type, type) else 'numeric'}"


            if 'main_price' in data and data['main_price'] <= 0:
                errors['main_price'] = "Price must be a positive number"
            if 'sale_price' in data and data['sale_price'] <= 0:
                errors['sale_price'] = "Price must be a positive number"
            if 'quantity' in data and data['quantity'] <= 0:
                errors['quantity'] = "Quantity must be a positive integer"

            if errors:
                raise ValidationError(errors)


    def _get_valid_category(self, category_id):
        try:
            category = ProductCategory.objects.get(pk=category_id)
            if category.category_name.lower() not in ['phone', 'mobile', 'accessory']:
                raise ValidationError("Invalid category type")
            return category
        except ProductCategory.DoesNotExist:
            raise ValidationError(f"Category with id {category_id} does not exist")

    def _validate_phone_data(self, data):
        if 'phone_specs' not in data:
            raise ValidationError("phone_specs are required for phone products")

        phone_data = data['phone_specs'].copy()
        required_fields = {
            'brand_id': int,
            'color_id': int,
            'camera_id': int,
            'storage': int,
            'battery': int,
            'ram': int,
            'display_size': float,
            'color_id':int,
            'processor':str
        }

        for field, field_type in required_fields.items():
            if field not in phone_data:
                raise ValidationError(f"Missing phone_specs field: {field}")
            try:
                phone_data[field] = field_type(phone_data[field])
            except (TypeError, ValueError):
                raise ValidationError(f"Invalid phone_specs.{field}. Expected {field_type.__name__}")

        return phone_data

    def _validate_accessory_data(self, data):
        if 'accessory_specs' not in data:
            raise ValidationError("accessory_specs are required for accessory products")

        accessory_data = data['accessory_specs'].copy()
        required_fields = {
            'description': str,
            'accessories_type': int
        }

        for field, field_type in required_fields.items():
            if field not in accessory_data:
                raise ValidationError(f"Missing accessory_specs field: {field}")
            try:
                accessory_data[field] = field_type(accessory_data[field])
            except (TypeError, ValueError):
                raise ValidationError(f"Invalid accessory_specs.{field}. Expected {field_type.__name__}")

        return accessory_data

class EditMultiple(GenericAPIView):#used
    permission_classes=[IsWarehouseManager]
    
    def put(self, request):
        try:
            updates = request.data.get('updates', [])
            if not updates:
                return Response({"error": "No updates provided"}, status=400)
        
            updated_ids = []
            for item in updates:
                try:
                    product = Product.objects.get(product_id=item['product_id'])
                    if 'quantity' in item:
                        item['quantity'] = product.quantity + int(item['quantity'])
                        
                    update_data = {}
                    if 'quantity' in item:
                        update_data['quantity'] = item['quantity']
                    if 'sale_price' in item:
                        update_data['sale_price'] = item['sale_price']
                    if 'main_price' in item:
                        update_data['main_price'] = item['main_price']
                    
                    rows_updated = Product.objects.filter(
                        product_id=item['product_id']
                    ).update(**update_data)
                    
                    if rows_updated > 0:
                        updated_ids.append(item['product_id'])
                        
                except Product.DoesNotExist:
                    continue
                except Exception as e:
                    print(f"Error updating product {item['product_id']}: {str(e)}")
                    continue
            
            return Response({
                "updated_products": updated_ids,
                "message": f"Successfully updated {len(updated_ids)} products"
            })
            
        except Exception as e:
            return Response({
                "error": str(e),
                "details": "Server error during bulk update"
            }, status=500)
## SEND PRODUCT TO BRANCH 



class WarehouseSendProductsView(GenericAPIView):##used
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    serializer_class = SendProductsSerializer
    def get(self, request):
        products = Product.objects.filter(quantity__gt=0).select_related('category_id')
        
        data = []
        for product in products:
            data.append({
                "product_id": product.product_id,
                "product_name": product.product_name,
                "quantity": product.quantity,
                "category": product.category_id.category_name if product.category_id else None,
                "main_price": product.main_price,
                "sale_price": product.sale_price,
            })

        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            branch_location = serializer.validated_data['branch_location']
            try:
                branch = Branch.objects.get(location__iexact=branch_location)
            except Branch.DoesNotExist:
                available_branches = Branch.objects.values_list('location', flat=True)
                raise ValueError(
                    f"Branch with location '{branch_location}' not found. "
                    f"Available branches: {list(available_branches)}"
                )

            product_transaction = ProductTransaction.objects.create(
                movement_type='sent',
                branch_id=branch,
                is_done=True,
                date_of_transaction=timezone.now()
            )

            results = []
            for item in serializer.validated_data['products']:
                try:
                    with transaction.atomic():
                        product_id = item['product_id']
                        product = Product.objects.select_for_update().get(pk=product_id)
                        
                        if product.quantity < item['quantity']:
                            raise ValueError(
                                f"Insufficient stock for product {product.product_id} ({product.product_name}). "
                                f"Available: {product.quantity}, Requested: {item['quantity']}"
                            )

                        product.quantity -= item['quantity']
                        product.save()

                        branch_product, created = BranchProducts.objects.get_or_create(
                            branch_id=branch,
                            product_id=product.pk,
                            defaults={'quantity': item['quantity']}
                        )
                        if not created:
                            branch_product.quantity += item['quantity']
                            branch_product.save()

                        TransportedProducts.objects.create(
                            transaction_id=product_transaction.pk,
                            product_id=product.pk,
                            main_price=product.main_price,
                            selling_price=product.sale_price,
                            quantity=item['quantity']
                        )

                        results.append({
                            "product_id": product.pk,
                            "product_name": product.product_name,
                            "status": "success",
                            "quantity_transferred": item['quantity'],
                            "remaining_warehouse_stock": product.quantity
                        })

                except Product.DoesNotExist:
                    results.append({
                        "product_id": product_id,
                        "status": "failed",
                        "error": f"Product with ID {product_id} not found"
                    })
                    product_transaction.is_done = False
                    product_transaction.save()
                except Exception as e:
                    results.append({
                        "product_id": product_id,
                        "status": "failed",
                        "error": str(e)
                    })
                    product_transaction.is_done = False
                    product_transaction.save()

            return Response({
                "transaction_id": product_transaction.pk,
                "branch_id": branch.branch_id,
                "branch_location": branch.location,
                "branch_number": branch.branch_number,
                "transaction_date": product_transaction.date_of_transaction,
                "status": "completed" if product_transaction.is_done else "partial",
                "results": results
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response
## retrieve from branch 
class WarehouseRetrieveProductsView(GenericAPIView):##used
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    filter_backends = [SearchFilter]
    search_fields = ['product_id__product_name']
    serializer_class = RetrieveProductsSerializer

    def get(self, request):
        branch_location = request.query_params.get('branch_location')
        search_query = request.query_params.get('search', '')
        
        if not branch_location:
            return Response(
                {"error": "branch_location parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            branch = Branch.objects.get(location__iexact=branch_location)
        except Branch.DoesNotExist:
            available_branches = Branch.objects.values_list('location', flat=True)
            return Response(
                {
                    "error": f"Branch with location '{branch_location}' not found",
                    "available_branches": list(available_branches)
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        products = BranchProducts.objects.filter(branch_id=branch)
        
        if search_query:
            products = products.filter(
                product_id__product_name__icontains=search_query
            )
            
        serializer = BranchProductSerializer(
            products.select_related('product_id__category_id'),
            many=True
        )
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        serializer = RetrieveProductsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        branch_location = serializer.validated_data['branch_location']
        products_data = serializer.validated_data['products']

        try:
            branch = Branch.objects.get(location__iexact=branch_location)
        except Branch.DoesNotExist:
            available_branches = Branch.objects.values_list('location', flat=True)
            return Response(
                {
                    "error": f"Branch with location '{branch_location}' not found",
                    "available_branches": list(available_branches)
                },
                status=status.HTTP_404_NOT_FOUND
            )

        retrieval_transaction = ProductTransaction.objects.create(
            movement_type='retrieved',
            branch_id=branch,
            is_done=True,
            date_of_transaction=timezone.now()
        )

        results = []
        for product_data in products_data:
            product_id = product_data['product_id']
            quantity = product_data['quantity']

            try:
                with transaction.atomic():
                    branch_product = BranchProducts.objects.select_for_update().get(
                        branch_id=branch,
                        product_id=product_id
                    )
                    
                    if branch_product.quantity < quantity:
                        results.append({
                            "product_id": product_id,
                            "status": "failed",
                            "reason": f"Insufficient branch stock (available: {branch_product.quantity}, requested: {quantity})"
                        })
                        continue

                    product = Product.objects.get(pk=product_id)
                    
                    branch_product.quantity -= quantity
                    branch_product.save()
                    
                    product.quantity += quantity
                    product.save()

                    TransportedProducts.objects.create(
                        transaction_id=retrieval_transaction.pk,
                        product_id=product.pk,
                        main_price=product.main_price,
                        selling_price=product.sale_price,
                        quantity=quantity
                    )

                    results.append({
                        "product_id": product_id,
                        "product_name": product.product_name,
                        "status": "success",
                        "quantity_retrieved": quantity,
                        "new_branch_stock": branch_product.quantity,
                        "new_warehouse_stock": product.quantity
                    })

            except BranchProducts.DoesNotExist:
                results.append({
                    "product_id": product_id,
                    "status": "failed",
                    "reason": f"Product not found in branch '{branch.location}'"
                })
            except Product.DoesNotExist:
                results.append({
                    "product_id": product_id,
                    "status": "failed",
                    "reason": "Product not found in warehouse"
                })
            except Exception as e:
                results.append({
                    "product_id": product_id,
                    "status": "failed",
                    "reason": str(e)
                })
                retrieval_transaction.is_done = False
                retrieval_transaction.save()

        return Response({
            "transaction_id": retrieval_transaction.pk,
            "branch_id": branch.branch_id,
            "branch_number": branch.branch_number,
            "branch_location": branch.location,
            "transaction_date": retrieval_transaction.date_of_transaction.strftime('%Y-%m-%d %H:%M:%S'),
            "status": "completed" if retrieval_transaction.is_done else "partial",
            "results": results
        }, status=status.HTTP_200_OK)
    

##manage requests 
class WarehouseManagerRequests(GenericAPIView):##used
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    serializer_class = BranchOrderSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BranchOrderRequestsFilter
    pagination_class = PageNumberPagination
    search_fields = ['requestedproducts_set__product_id__product_name']
    def get_queryset(self):
        return BranchOrder.objects.filter(is_done=False)\
            .select_related('branch_id')\
            .prefetch_related(
                Prefetch(
                    'requestedproducts_set',
                    queryset=RequestedProducts.objects.select_related(
                        'product_id',
                        'product_id__category_id'
                    )
                )
            ).order_by('-date_of_order')

    def get(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            # Paginate the queryset
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            # If no pagination, return all results
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": str(e), "detail": "Error fetching requests"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @transaction.atomic
    def post(self, request, order_id=None):
        try:
            order = BranchOrder.objects.select_for_update().get(
                order_id=order_id,
                is_done=False
            )
        except BranchOrder.DoesNotExist:
            return Response(
                {"error": "Order not found or already processed"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProcessRequestSerializer1(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action = serializer.validated_data['action']
        
        if action == 'approve':
            return self._approve_full_order(order)
        elif action == 'reject':
            return self._reject_full_order(
                order, 
                serializer.validated_data.get('rejection_reason', '')
            )
        elif action == 'partial':
            return self._process_partial_order(
                order,
                serializer.validated_data['products']
            )

    def _approve_full_order(self, order):



        requested_products = order.requestedproducts_set.select_related(
            'product_id'
        ).select_for_update()

        for rp in requested_products:
            if rp.product_id.quantity < rp.quantity:
                return Response(
                    {
                        "error": "Insufficient stock",
                        "product_id": rp.product_id.product_id,
                        "product_name": rp.product_id.product_name,
                        "requested": rp.quantity,
                        "available": rp.product_id.quantity
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        for rp in requested_products:
            self._transfer_product(rp, rp.quantity)
            rp.status = 'S'
            rp.processed_date = timezone.now()
            rp.save()

        order.is_done = True
        order.save()

        return Response({
            "status": "approved",
            "order_id": order.order_id,
            "transferred_products": RequestedProductsSerializer(
                requested_products,
                many=True
            ).data
        })

    def _reject_full_order(self, order, rejection_reason):
        requested_products = order.requestedproducts_set.all()

        for rp in requested_products:
            rp.status = 'R'
            rp.rejection_reason = rejection_reason
            rp.processed_date = timezone.now()
            rp.save()

        order.is_done = True
        order.save()

        return Response({
            "status": "rejected",
            "order_id": order.order_id,
            "reason": rejection_reason
        })

    def _process_partial_order(self, order, products_data):
        requested_products = order.requestedproducts_set.select_related(
            'product_id'
        ).select_for_update()

        results = {
            "approved": [],
            "rejected": [],
            "errors": []
        }

        for product_action in products_data:
            try:
                rp = requested_products.get(id=product_action['id'])
                
                if product_action['action'] == 'approve':
                    quantity = product_action.get('quantity', rp.quantity)
                    
                    if quantity > rp.product_id.quantity:
                        results['errors'].append({
                            "product_id": rp.product_id.product_id,
                            "error": f"Only {rp.product_id.quantity} available",
                            "requested": quantity
                        })
                        continue
                        
                    self._transfer_product(rp, quantity)
                    rp.status = 'S'
                    rp.processed_date = timezone.now()
                    results['approved'].append({
                        "product_id": rp.product_id.product_id,
                        "quantity": quantity
                    })
                
                elif product_action['action'] == 'reject':
                    rp.status = 'R'
                    rp.processed_date = timezone.now()
                    rp.rejection_reason = product_action.get('rejection_reason', '')
                    results['rejected'].append({
                        "product_id": rp.product_id.product_id,
                        "reason": rp.rejection_reason
                    })
                
                rp.save()
                
            except RequestedProducts.DoesNotExist:
                results['errors'].append({
                    "product_id": "unknown",
                    "error": f"Requested product {product_action['id']} not found"
                })

        order.is_done = True
        order.save()

        return Response({
            "status": "partially_processed",
            "order_id": order.order_id,
            "results": results
        })

    def _transfer_product(self, requested_product, quantity):
        Product.objects.filter(
            pk=requested_product.product_id.pk
        ).update(quantity=F('quantity') - quantity)

        branch = requested_product.order_id.branch_id

        branch_product, created = BranchProducts.objects.get_or_create(
            branch_id=branch,
            product_id=requested_product.product_id,
            defaults={'quantity': quantity}
        )

        if not created:
            branch_product.quantity += quantity
            branch_product.save()


class ColorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsWarehouseManager]
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

    def create(self, request, *args, **kwargs):
        # Ensure color_id is not in the request data
        request.data.pop('color_id', None)
        return super().create(request, *args, **kwargs)
class BrandViewSet(viewsets.ModelViewSet):
    permission_classes = [IsWarehouseManager]
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    def create(self, request, *args, **kwargs):
            # Ensure color_id is not in the request data
        request.data.pop('color_id', None)
        return super().create(request, *args, **kwargs)


class AccessoriesTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsWarehouseManager]
    queryset = AccessoriesType.objects.all()
    serializer_class = AccessoriesTypeSerializer
    def create(self, request, *args, **kwargs):
            # Ensure color_id is not in the request data
        request.data.pop('color_id', None)
        return super().create(request, *args, **kwargs)

class ProductTransactionListView(GenericAPIView):#used
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductTransactionFilter
    search_fields = ['branch_id__location']
    pagination_class = PageNumberPagination

    def get(self, request):
        try:
            transactions = ProductTransaction.objects.select_related(
                'branch_id'
            ).prefetch_related(
                Prefetch(
                    'transported_items',
                    queryset=TransportedProducts.objects.select_related(
                        'product',
                        'product__category_id'  
                    )
                )
            ).annotate(
                total_products=Count('transported_items'),
                total_quantity=Sum('transported_items__quantity')
            ).order_by('-date_of_transaction')

            transactions = self.filter_queryset(transactions)

            page = self.paginate_queryset(transactions)
            if page is not None:
                serializer = ProductTransactionListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = ProductTransactionListSerializer(transactions, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductTransactionDetailView(GenericAPIView):#used
    permission_classes = [IsAuthenticated, IsWarehouseManager]

    def get(self, request, pk):
        
        try:
            transaction = ProductTransaction.objects.select_related(
                'branch_id'
            ).prefetch_related(
                Prefetch(
                    'transported_items',
                    queryset=TransportedProducts.objects.select_related(
                        'product',
                        'product__category_id'  
                    )
                )
            ).get(pk=pk)

            transaction_data = {
                "transaction_id": transaction.process_id,
                "date": transaction.date_of_transaction,
                "branch_location": transaction.branch_id.location,
                "branch_number": transaction.branch_id.branch_number,
                "movement_type": transaction.movement_type,
                "is_done": transaction.is_done,
                "products": []
            }

            for item in transaction.transported_items.all():
                transaction_data["products"].append({
                    "product_id": item.product.product_id,
                    "product_name": item.product.product_name,
                    "category_name": item.product.category_id.category_name, 
                    "main_price": float(item.main_price),
                    "selling_price": float(item.selling_price)
                })

            return Response(transaction_data)

        except ProductTransaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            


class WareHouseRequestsLogView(GenericAPIView):##used
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter,OrderingFilter]
    filterset_class = BranchOrderRequestsFilter 
    pagination_class = PageNumberPagination
    search_fields = [ 'requestedproducts_set__product_id__product_name']
    ordering_fields = ['date_of_order', 'branch_id__location']
    ordering = ['-date_of_order']
    def get(self, request):
        try:
            queryset = BranchOrder.objects.select_related(
                'branch_id'
            ).prefetch_related(
                Prefetch(
                    'requestedproducts_set',
                    queryset=RequestedProducts.objects.select_related(
                        'product_id',
                        'product_id__category_id'
                    )
                )
            ).order_by('-date_of_order')

            
            print(str(queryset.query))

            
            filtered_queryset = self.filter_queryset(queryset)
            
            print(str(filtered_queryset.query))

        
            response_data = []
            for order in filtered_queryset:
                order_data = {
                    "order_id": order.order_id,
                    "date_of_order": order.date_of_order.strftime('%Y-%m-%d'),
                    "branch_location": order.branch_id.location,
                    "branch_number": order.branch_id.branch_number,
                    "total_requested_products": order.requestedproducts_set.count(),
                    "products": []
                }

                for item in order.requestedproducts_set.all():
                    product_data = {
                        "product_id": item.product_id.product_id,
                        "product_name": item.product_id.product_name,
                        "category": item.product_id.category_id.category_name,
                        "quantity": item.quantity,
                        "status": item.status,
                    }
                    order_data["products"].append(product_data)

                response_data.append(order_data)

            page = self.paginate_queryset(response_data)
            if page is not None:
                return self.get_paginated_response(page)

            return Response(response_data)

        except Exception as e:
            return Response(
                {"error": str(e), "detail": "Filter processing failed"},
                status=status.HTTP_400_BAD_REQUEST
            )
            

## logging 

class ActivityLogListView(generics.ListAPIView):
    queryset = ActivityLog.objects.all().order_by('-timestamp')
    serializer_class = ActivityLogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'action', 'model_name', 'timestamp']
    permission_classes = [IsAdminUser,IsActiveSuperAdmin]  
