from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework import viewsets
from .serializers import *
from rest_framework import permissions
from  django.http import JsonResponse 
from django_filters.rest_framework import DjangoFilterBackend
from .filters import *
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from rest_framework import status
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
    # def city_delete(self, request, id):
    #     if request.method =='DELETE':
    #         city = City.objects.get(id=id)
    #         city.delete()
    #         return JsonResponse("success")
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

class AccessoriesTypeViewSet(viewsets.ModelViewSet):
    queryset = AccessoriesType.objects.all()
    serializer_class = AccessoriesTypeSerializer

class AccessoriesViewSet(viewsets.ModelViewSet):
    queryset = Accessories.objects.all()
    serializer_class = AccessoriesSerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

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
    serializer_class = BranchOrderSerializer

class RequestedProductsViewSet(viewsets.ModelViewSet):
    queryset = RequestedProducts.objects.all()
    serializer_class = RequestedProductsSerializer

class ProductTransactionViewSet(viewsets.ModelViewSet):
    queryset = ProductTransaction.objects.all()
    serializer_class = ProductTransactionSerializer

class TransportedProductsViewSet(viewsets.ModelViewSet):
    queryset = TransportedProducts.objects.all()
    serializer_class = TransportedProductsSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except AuthenticationFailed:
            return {
                'error': 'Invalid credentials',
                'detail': 'No active account found with the given credentials'
            }
        data.update({
            'user_id': self.user.id,
            'username': self.user.username,
            'is_staff': self.user.is_staff
        })
        return data

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

class LogoutView(TokenBlacklistView):
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'error': 'Logout failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class BranchManagement(APIView):
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BranchFilter  
    search_fields = ['location']  

    def get(self, request):
        queryset = Branch.objects.all()
        filtered_queryset = self.filter_queryset(queryset)
        serializer = BranchSerializer(filtered_queryset, many=True)
        return Response(serializer.data)
    def get(self, request):
        branches = Branch.objects.all()
        serializer = BranchSerializer(branches, many=True)
        
        return Response(serializer.data)

    def post(self, request):
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BranchDetail(APIView):
    permission_classes = [IsAdminUser]

    # GET /admin/branches/<pk>
    def get(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
            serializer = BranchSerializer(branch)
            return Response(serializer.data)
        except Branch.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class BranchOperations(APIView):
    permission_classes = [IsAdminUser]

    # PUT /admin/branches/<pk>/detail
    def put(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
            serializer = BranchSerializer(branch, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Branch.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # DELETE /admin/branches/<pk>/detail
    def delete(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
            branch.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Branch.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        
###################settings###################################

class CityManagement(APIView):
    permission_classes = [IsAdminUser]
    def get(self,request):
        city = City.objects.all()
        serializer = CitySerializer(city, many=True)
        return Response(serializer.data)
    # POST /admin/settings/cities/add
    def post(self, request):
        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE /admin/settings/cities/delete/<pk>
    def delete(self, request, pk):
        try:
            city = City.objects.get(pk=pk)
            city.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except City.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class JobManagement(APIView):
    permission_classes = [IsAdminUser]
    def get(self,request):
        job = Job.objects.all() 
        serializer = JobSerializer(job, many=True)
        return Response(serializer.data)
    # POST /admin/settings/jobs/add
    def post(self, request):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE /admin/settings/jobs/delete/<pk>
    def delete(self, request, pk):
        try:
            job = Job.objects.get(pk=pk)
            job.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Job.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
##############################BranchStatistics####################################



class BranchStatisticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get filter parameters from query params
        period = request.query_params.get('period', 'all')
        date_str = request.query_params.get('date', None)
        
        sold_products = SoldProduct.objects.filter(purchase_id__branch_id=branch)

        # Date filtering logic
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

        # Calculate statistics
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
    
#################################################################################
class AdminStatisticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Get filter parameters
        period = request.query_params.get('period', 'all')
        date_str = request.query_params.get('date', None)

        # Initialize base querysets
        sold_products = SoldProduct.objects.all()
        customers = Customer.objects.all()

        # Date filtering logic
        if period != 'all' and date_str:
            try:
                if period == 'daily':
                    filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    date_filter = Q(purchase_id__date_of_purchase__date=filter_date)
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

        # Calculate statistics
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
################# Manages Employee ##########################################


class EmployeeListView(APIView):
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filtersets_class=EmployeeFilter
    search_fields = ['f_name']

    def get(self, request):
        queryset = Employee.objects.all()
        
        
        filtered_queryset = self.filter_queryset(queryset)
        
        serializer = EmployeeSerializer(filtered_queryset, many=True)
        return Response(serializer.data)
    def get(self,requset):
        queryset=Employee.objects.all()
        serializer=EmployeeSerializer(queryset,many=True)
        return Response(serializer.data)
class EmployeeDetailView(APIView):
    permission_classes = [IsAdminUser]

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

class AddEmployeeView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateEmployeeAccountView(APIView):
    permission_classes = [IsAdminUser]

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
        
        
        
        
#### ceo #####
class IsCeo(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        else:
            try:
                employee=request.user.employee
                return employee.job_id.job_name.lower()=="ceo"
            except AttributeError:
                    return False
                

##statistics ####
class CeoStatisticsView(APIView):
    permission_classes = [IsCeo]

    def get(self, request):
        # Get filter parameters
        period = request.query_params.get('period', 'all')
        date_str = request.query_params.get('date', None)

        # Initialize base querysets
        sold_products = SoldProduct.objects.all()
        customers = Customer.objects.all()

        # Date filtering logic (same as admin statistics)
        if period != 'all' and date_str:
            try:
                if period == 'daily':
                    filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    date_filter = Q(purchase_id__date_of_purchase__date=filter_date)
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

        # Calculate statistics (same as admin statistics)
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
# views.py
class CeoBranchStatisticsView(APIView):
    permission_classes = [IsCeo]

    def get(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get filter parameters from query params
        period = request.query_params.get('period', 'all')
        date_str = request.query_params.get('date', None)
        
        # Base queryset for the specific branch
        sold_products = SoldProduct.objects.filter(purchase_id__branch_id=branch)

        # Date filtering logic (same as admin version)
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

        # Calculate statistics
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
class CeoBranchManagement(APIView):
    permission_classes = [IsCeo]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BranchFilter  
    search_fields = ['location']  

    def get(self, request):
        queryset = Branch.objects.all()
        
        
        filtered_queryset = self.filter_queryset(queryset)
        
        serializer = BranchSerializer(filtered_queryset, many=True)
        return Response(serializer.data)
    def get(self, request):
        branches = Branch.objects.all()
        serializer = BranchSerializer(branches, many=True)
        
        return Response(serializer.data)

    def post(self, request):
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CeoBranchDetail(APIView):
    permission_classes = [IsCeo]

    # GET /admin/branches/<pk>
    def get(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
            serializer = BranchSerializer(branch)
            return Response(serializer.data)
        except Branch.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class CeoBranchOperations(APIView):
    permission_classes = [IsCeo]

    # PUT /admin/branches/<pk>/detail
    def put(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
            serializer = BranchSerializer(branch, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Branch.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # DELETE /admin/branches/<pk>/detail
    def delete(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
            branch.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Branch.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
## setting is add city 
class CeoCityManagement(APIView):
    permission_classes = [IsCeo]
    def get(self,request):
        city = City.objects.all()
        serializer = CitySerializer(city, many=True)
        return Response(serializer.data)
    # POST /admin/settings/cities/add
    def post(self, request):
        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE /admin/settings/cities/delete/<pk>
    def delete(self, request, pk):
        try:
            city = City.objects.get(pk=pk)
            city.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except City.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


## ceo browse employees 
class CeoEmployeeListView(APIView):
    permission_classes = [IsCeo]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filtersets_class=EmployeeFilter
    search_fields = ['f_name']

    def get(self, request):
        queryset = Employee.objects.all()
        
        
        filtered_queryset = self.filter_queryset(queryset)
        
        serializer = EmployeeSerializer(filtered_queryset, many=True)
        return Response(serializer.data)
    def get(self,requset):
        queryset=Employee.objects.all()
        serializer=EmployeeSerializer(queryset,many=True)
        return Response(serializer.data)
class CeoEmployeeDetailView(APIView):
    permission_classes = [IsCeo]

    def get(self, request, pk):
        employee =Employee.objects.get(pk=pk)
        if not employee:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)



## Hr PAGE###

class IsHr(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        else:
            try:
                employee=request.user.employee
                return employee.job_id.job_name.lower()=="hr"
            except AttributeError:
                    return False
                
                
class HrEmployeeListView(APIView):
    permission_classes = [IsHr]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filtersets_class=EmployeeFilter
    search_fields = ['f_name']

    def get(self, request):
        queryset = Employee.objects.all()
        
        
        filtered_queryset = self.filter_queryset(queryset)
        
        serializer = EmployeeSerializer(filtered_queryset, many=True)
        return Response(serializer.data)
    def get(self,requset):
        queryset=Employee.objects.all()
        serializer=EmployeeSerializer(queryset,many=True)
        return Response(serializer.data)
class HrEmployeeDetailView(APIView):
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

class HrAddEmployeeView(APIView):
    permission_classes = [IsHr]

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HrCreateEmployeeAccountView(APIView):
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
class HrJobManagement(APIView):
    permission_classes = [IsHr]
    def get(self,request):
        job = Job.objects.all() 
        serializer = JobSerializer(job, many=True)
        return Response(serializer.data)
    # POST /admin/settings/jobs/add
    def post(self, request):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE /admin/settings/jobs/delete/<pk>
    def delete(self, request, pk):
        try:
            job = Job.objects.get(pk=pk)
            job.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Job.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
#### WearHouse Manager Page ###
class IsWarehouseManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        else:
            try:
                employee=request.user.employee
                return employee.job_id.job_name.lower()=="warehouse manager"
            except AttributeError:
                return False
    
# class WarehouseProductView(APIView):
#     permission_classes=[IsWarehouseManager]
#     filter_backends=[DjangoFilterBackend]
#     filterset_class=ProductFilter
    
#     def get(self,request):
#         queryset = Product.objects.select_related('category_id').prefetch_related('phone_set').all()
#         filtered_queryset=self.filterset_class(request.GET,queryset=queryset).qs
#         serializer = ProductSerializer(filtered_queryset, many=True)
#         return Response(serializer.data)
# class PhoneManagementView(APIView):
#     permission_classes=[IsWarehouseManager]
#     def get_phone(self,pk):
#         try:
#             return Phone.objects.get(product_id=pk)
#         except Phone.DoesNotExist:
#                 return None
#     def put(self,request,pk):
#         phone=self.get_phone(pk)
#         if not phone:
#             return Response({"error":"phone not found"},status=status.HTTP_404_NOT_FOUND)
#         serializer=PhoneSerializer(phone,data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors,status=status.HTTP_404_NOT_FOUND)
    
#     def delete(self,request,pk):
#         phone=self.get_phone(pk)
#         if not phone:
#             return Response({"error":"phone not phound"},status=status.HTTP_404_NOT_FOUND)
#         phone.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class AccessoryManagementView(APIView):
#     permission_classes=[IsWarehouseManager]
    
    
#     def get_accessory(self,requset,pk):
#         try:
#             return Accessories.objects.get(product_id=pk)
#         except Accessories.DoesNotExist():
#             return None
    
#     def put(self,request,pk):
#         accessory=self.get_accessory(pk)
#         if not accessory:
#             return Response({"error":"not found"},status=status.HTTP_404_NOT_FOUND)
#         serializer=AccessoriesSerializer(accessory,data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
#     def delete(self,request,pk):
#         accessory=self.get_accessory(pk)
#         if not accessory:
#             return Response({"error":"not found"},status=status.HTTP_404_NOT_FOUND)
#         accessory.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class AddProduct(APIView):
#     permission_classes=[IsWarehouseManager]
    
#     def post(self,request):
#         serializer=ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             product=serializer.save()
#             if product.category_id.category_name.lower() in ['phone', 'mobile']:
#                     Phone.objects.create(product_id=product, **request.data.get('phone_specs', {}))
#             else:
#                 Accessories.objects.create(product_id=product, **request.data.get('accessory_specs', {}))
            
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class EditMultiple(APIView):
#     permission_classes=[IsWarehouseManager]
    
#     def put(self, request):
#         updates = request.data.get('updates', [])
#         if not updates:
#             return Response({"error": "No updates provided"}, status=400)
    
#         updated_ids = []
#         for item in updates:
#             product = Product.objects.filter(product_id=item['product_id']).update(
#                 quantity=item.get('quantity'),
#                 sale_price=item.get('sale_price')
#         )
#             if product:
#                 updated_ids.append(item['product_id'])
    
#         return Response({"updated_products": updated_ids})
    
    
    
    
# ### Branch products 
# class BranchManagerProductsView(APIView):
#     permission_classes = [IsAuthenticated, IsManager]
#     filter_backends = [DjangoFilterBackend]
#     filterset_class = ProductFilter

#     def get(self, request):
#         # Get the manager's branch
#         branch = request.user.employee.branch_id
        
#         # Get products with quantities in this branch
#         queryset = Product.objects.filter(
#             branchproducts__branch_id=branch
#         ).select_related('category_id').annotate(
#             branch_quantity=models.F('branchproducts__quantity')
#         ).distinct()

#         # Apply filters
#         filtered_queryset = self.filterset_class(request.GET, queryset=queryset).qs
        
#         # Custom response format
#         response_data = [{
#             'product_id': product.product_id,
#             'product_name': product.product_name,
#             'category': product.category_id.category_name,
#             'main_price': product.main_price,
#             'sale_price': product.sale_price,
#             'branch_quantity': product.branch_quantity
#         } for product in filtered_queryset]

#         return Response(response_data)


            
            
# ## order product 

# from django.db import transaction

# class BranchOrderView(APIView):
#     permission_classes = [IsAuthenticated, IsManager]

#     def get(self, request):
#         """Show available warehouse products"""
#         warehouse_products = Product.objects.filter(quantity__gt=0).select_related('category_id')
        
#         serializer = ProductSerializer(warehouse_products, many=True)
#         return Response([{
#             'product_id': p['product_id'],
#             'product_name': p['product_name'],
#             'category': p['category_id']['category_name'],
#             'warehouse_quantity': p['quantity'],
#             'main_price': p['main_price'],
#             'sale_price': p['sale_price']
#         } for p in serializer.data])

#     @transaction.atomic
#     def post(self, request):
#         """Create a new product order from warehouse"""
#         branch = request.user.employee.branch_id
#         products_data = request.data.get('products', [])
#         note = request.data.get('note', '')

#         if not products_data:
#             return Response(
#                 {"error": "At least one product is required"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Create the order
#         order = BranchOrder.objects.create(
#             branch_id=branch,
#             note=note,
#             is_done=False
#         )

#         results = []
#         for product_data in products_data:
#             product_id = product_data.get('product_id')
#             quantity = product_data.get('quantity')

#             if not product_id or not quantity:
#                 results.append({
#                     "product_id": product_id,
#                     "status": "failed",
#                     "reason": "Missing product_id or quantity"
#                 })
#                 continue

#             try:
#                 product = Product.objects.get(pk=product_id)
#                 if product.quantity < quantity:
#                     results.append({
#                         "product_id": product_id,
#                         "status": "failed",
#                         "reason": "Insufficient warehouse quantity"
#                     })
#                     continue

#                 # Create order item
#                 RequestedProducts.objects.create(
#                     order_id=order,
#                     product_id=product,
#                     quantity=quantity,
#                     status='P'  # Pending
#                 )

#                 results.append({
#                     "product_id": product_id,
#                     "status": "success",
#                     "quantity": quantity
#                 })

#             except Product.DoesNotExist:
#                 results.append({
#                     "product_id": product_id,
#                     "status": "failed",
#                     "reason": "Product not found"
#                 })

#         return Response({
#             "order_id": order.order_id,
#             "branch_id": branch.branch_id,
#             "note": note,
#             "products": results
#         }, status=status.HTTP_201_CREATED) 
        




# #### order log 
# from datetime import datetime
# from django.db.models import Q

# class BranchOrderHistoryView(APIView):
#     permission_classes = [IsAuthenticated, IsManager]
    
#     def get(self, request):
#         # Get orders for the manager's branch
#         branch = request.user.employee.branch_id
#         orders = BranchOrder.objects.filter(branch_id=branch)
        
#         # Ordering
#         date_order = request.query_params.get('date_order', 'desc').lower()
#         if date_order == 'asc':
#             orders = orders.order_by('date_of_order')
#         else:  # default to desc
#             orders = orders.order_by('-date_of_order')
        
#         # Status filtering
#         status = request.query_params.get('status', '').lower()
#         if status == 'completed':
#             orders = orders.filter(is_done=True)
#         elif status == 'pending':
#             orders = orders.filter(is_done=False)
        
#         # Date range filtering
#         start_date = request.query_params.get('start_date')
#         end_date = request.query_params.get('end_date')
        
#         if start_date:
#             try:
#                 start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
#                 orders = orders.filter(date_of_order__gte=start_date)
#             except ValueError:
#                 pass
                
#         if end_date:
#             try:
#                 end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
#                 orders = orders.filter(date_of_order__lte=end_date)
#             except ValueError:
#                 pass
        
#         serializer = BranchOrderLogSerializer(orders, many=True)
#         return Response(serializer.data)

# class BranchOrderDetailView(APIView):
#     permission_classes = [IsAuthenticated, IsManager]
    
#     def get(self, request, order_id):
#         try:
#             # Verify the order belongs to the manager's branch
#             order = BranchOrder.objects.get(
#                 order_id=order_id,
#                 branch_id=request.user.employee.branch_id
#             )
            
#             requested_products = RequestedProducts.objects.filter(order_id=order)
#             serializer = RequestedProductsDetailSerializer(requested_products, many=True)
            
#             return Response({
#                 'order_id': order.order_id,
#                 'date_of_order': order.date_of_order,
#                 'branch': order.branch_id.location,
#                 'note': order.note,
#                 'status': 'Completed' if order.is_done else 'Pending',
#                 'products': serializer.data
#             })
            
#         except BranchOrder.DoesNotExist:
#             return Response(
#                 {"error": "Order not found or not accessible"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
            
            
            
# ### solds logs 
# from django.db.models import Sum, F

# class SoldProductsLogView(APIView):
#     permission_classes = [IsAuthenticated, IsManager]

#     def get(self, request):
#         # Get the manager's branch
#         branch = request.user.employee.branch_id
#         purchases = Purchase.objects.filter(branch_id=branch)

#         # Ordering
#         date_order = request.query_params.get('date_order', 'desc').lower()
#         if date_order == 'asc':
#             purchases = purchases.order_by('date_of_purchase')
#         else:  # default to desc
#             purchases = purchases.order_by('-date_of_purchase')

#         # Date range filtering
#         start_date = request.query_params.get('start_date')
#         end_date = request.query_params.get('end_date')

#         if start_date:
#             try:
#                 start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
#                 purchases = purchases.filter(date_of_purchase__gte=start_date)
#             except ValueError:
#                 pass

#         if end_date:
#             try:
#                 end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
#                 purchases = purchases.filter(date_of_purchase__lte=end_date)
#             except ValueError:
#                 pass

#         serializer = SoldProductsLogSerializer(purchases, many=True)
#         return Response(serializer.data)

# class SoldProductsDetailView(APIView):
#     permission_classes = [IsAuthenticated, IsManager]

#     def get(self, request, purchase_id):
#         try:
#             # Verify the purchase belongs to the manager's branch
#             purchase = Purchase.objects.get(
#                 purchase_id=purchase_id,
#                 branch_id=request.user.employee.branch_id
#             )
            
#             sold_products = SoldProduct.objects.filter(purchase_id=purchase)
#             serializer = SoldProductsDetailSerializer(sold_products, many=True)

#             # Calculate grand total
#             grand_total = sum(item['total_price'] for item in serializer.data)

#             return Response({
#                 'purchase_id': purchase.purchase_id,
#                 'customer_name': f"{purchase.customer_id.first_name} {purchase.customer_id.middle_name} {purchase.customer_id.last_name}",
#                 'branch': purchase.branch_id.location,
#                 'date_of_purchase': purchase.date_of_purchase,
#                 'products': serializer.data,
#                 'grand_total': grand_total
#             })

#         except Purchase.DoesNotExist:
#             return Response(
#                 {"error": "Purchase not found or not accessible"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
            

## Sales Manager 
class IsSaleManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False 
        try:
            employee=self.user.employee
            return employee.job_id.job_name.lower()=="sales manager"
        except AttributeError:
                    return False
                


##  branch product 

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import BranchProducts
from .serializers import BranchProductSerializer

class SalesManagerProductsView(APIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def get(self, request):
        """
        Get all products available in the sales manager's branch
        Response includes: product_id, name, category, prices, and quantity
        """
        try:
            # Get the sales manager's branch
            branch = request.user.employee.branch_id
            
            # Get products with quantity > 0 in this branch
            branch_products = BranchProducts.objects.filter(
                branch_id=branch,
                quantity__gt=0
            ).select_related(
                'product_id__category_id'
            )
            
            serializer = BranchProductSerializer(branch_products, many=True)
            return Response(serializer.data)
            
        except AttributeError:
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


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Customer, Product, BranchProducts, Purchase, SoldProduct
from .serializers import CustomerSearchSerializer, MakeSaleSerializer

class MakeSaleView(APIView):
    permission_classes = [IsAuthenticated, IsSaleManager]

    @transaction.atomic
    def post(self, request):
        """
        Make a new sale
        1. Validate customer exists
        2. Check product availability
        3. Record sale and update inventory
        """
        serializer = MakeSaleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the sales manager's branch
            branch = request.user.employee.branch_id
            
            # Process customer
            customer_id = serializer.validated_data['customer_id']
            try:
                customer = Customer.objects.get(pk=customer_id)
            except Customer.DoesNotExist:
                return Response(
                    {"error": "Customer not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Create purchase record
            purchase = Purchase.objects.create(
                branch_id=branch,
                customer_id=customer,
                date_of_purchase=timezone.now()
            )

            # Process products
            sold_products = []
            grand_total = 0
            
            for item in serializer.validated_data['products']:
                product_id = item['product_id']
                quantity = item['quantity']

                # Check product availability
                try:
                    branch_product = BranchProducts.objects.select_for_update().get(
                        branch_id=branch,
                        product_id=product_id,
                        quantity__gte=quantity
                    )
                except BranchProducts.DoesNotExist:
                    return Response(
                        {"error": f"Product ID {product_id} not available in requested quantity"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                product = branch_product.product_id
                total_price = product.sale_price * quantity
                grand_total += total_price

                # Record sold product
                SoldProduct.objects.create(
                    purchase_id=purchase,
                    product_id=product,
                    quantity=quantity,
                    main_price=product.main_price,
                    selling_price=product.sale_price
                )

                # Update inventory
                branch_product.quantity -= quantity
                branch_product.save()

                sold_products.append({
                    'product_id': product_id,
                    'product_name': product.product_name,
                    'quantity': quantity,
                    'unit_price': float(product.sale_price),
                    'total_price': float(total_price)
                })

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

class CustomerSearchView(APIView):
    permission_classes = [IsAuthenticated, IsSaleManager]

    def get(self, request):
        """
        Search customers by name or national number
        Returns: customer_id, full_name, national_num
        """
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
        )[:10]  # Limit to 10 results

        serializer = CustomerSearchSerializer(customers, many=True)
        return Response(serializer.data)

### add customer 
class AddCustomerView(APIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def post(self, request):
        """
        Add a new customer
        Required fields: first_name, last_name, national_num, phone_num
        """
        serializer = AddCustomerSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Check if customer already exists
                national_num = serializer.validated_data['national_num']
                if Customer.objects.filter(national_num=national_num).exists():
                    return Response(
                        {"error": "Customer with this national number already exists"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Create the customer
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




class CustomerListView(APIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def get(self, request):
        """Get list of all customers with search capability"""
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

class CustomerDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def get(self, request, pk):
        """Get single customer details"""
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """Update customer details"""
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Check national_num uniqueness if being updated
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
        """Delete a customer"""
        customer = get_object_or_404(Customer, pk=pk)
        customer.delete()
        return Response(
            {"success": True, "message": "Customer deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
        
        
### customer sales log 

class CustomerSalesLogView(APIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def get(self, request, pk):
        """Get all sales for a specific customer"""
        customer = get_object_or_404(Customer, pk=pk)
        
        # Get all purchases for this customer
        purchases = Purchase.objects.filter(
            customer_id=customer
        ).prefetch_related('soldproduct_set').order_by('-date_of_purchase')
        
        serializer = CustomerSaleSerializer(purchases, many=True)
        
        return Response({
            'customer_id': customer.customer_id,
            'customer_name': f"{customer.first_name} {customer.last_name}",
            'national_num': customer.national_num,
            'total_purchases': purchases.count(),
            'sales': serializer.data
        })

class SaleDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def get(self, request, customer_pk, purchase_pk):
        """Get detailed information about a specific sale"""
        # Verify customer exists (even though we don't strictly need it for the query)
        get_object_or_404(Customer, pk=customer_pk)
        
        # Get all sold products for this purchase
        sold_products = SoldProduct.objects.filter(
            purchase_id=purchase_pk
        ).select_related(
            'product_id__category_id',
            'purchase_id__branch_id'
        )
        
        if not sold_products.exists():
            return Response(
                {"error": "Purchase not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SaleDetailSerializer(sold_products, many=True)
        
        # Calculate totals
        grand_total = sum(item.selling_price * item.quantity for item in sold_products)
        total_items = sum(item.quantity for item in sold_products)
        
        return Response({
            'purchase_id': purchase_pk,
            'customer_id': customer_pk,
            'date': sold_products[0].purchase_id.date_of_purchase,
            'branch': sold_products[0].purchase_id.branch_id.location,
            'products': serializer.data,
            'grand_total': grand_total,
            'total_items': total_items
        })
        
### sold products log

class SoldProductLogView(APIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def get(self, request):
        """Get all purchases with summary information"""
        # Get the sales manager's branch
        branch = request.user.employee.branch_id
        
        # Get filter parameters
        search_query = request.query_params.get('search', '')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Base query - only show purchases from manager's branch
        purchases = Purchase.objects.filter(branch_id=branch)
        
        # Apply filters
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
        
        # Order by most recent first
        purchases = purchases.order_by('-date_of_purchase')
        
        serializer = PurchaseLogSerializer(purchases, many=True)
        return Response(serializer.data)

class PurchaseDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def get(self, request, purchase_id):
        """Get detailed information about a specific purchase"""
        # Verify purchase exists and belongs to manager's branch
        purchase = get_object_or_404(
            Purchase,
            purchase_id=purchase_id,
            branch_id=request.user.employee.branch_id
        )
        
        # Get all sold products for this purchase
        sold_products = SoldProduct.objects.filter(
            purchase_id=purchase
        ).select_related('product_id__category_id')
        
        products_serializer = SoldProductDetailSerializer(sold_products, many=True)
        
        # Calculate totals
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
from django.template.loader import get_template
import pdfkit
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Purchase, SoldProduct

class GenerateBillView(APIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def get(self, request, purchase_id):
        """Generate a PDF bill for a purchase"""
        try:
            # Verify purchase exists and belongs to manager's branch
            purchase = get_object_or_404(
                Purchase,
                purchase_id=purchase_id,
                branch_id=request.user.employee.branch_id
            )
            
            # Get all sold products for this purchase
            sold_products = SoldProduct.objects.filter(
                purchase_id=purchase
            ).select_related('product_id__category_id')
            
            # Prepare data for template
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

class GenerateBillPDFView(APIView):
    permission_classes = [IsAuthenticated, IsSaleManager]
    
    def get(self, request, purchase_id):
        """Generate a PDF bill for a purchase"""
        try:
            # Verify purchase exists and belongs to manager's branch
            purchase = get_object_or_404(
                Purchase,
                purchase_id=purchase_id,
                branch_id=request.user.employee.branch_id
            )
            
            # Get all sold products for this purchase
            sold_products = SoldProduct.objects.filter(
                purchase_id=purchase
            ).select_related('product_id__category_id')
            
            # Prepare data for template
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
            
            # Render template
            template = get_template('bill_template.html')
            html = template.render(context)
            
            # PDF options
            options = {
                'page-size': 'A5',
                'margin-top': '0mm',
                'margin-right': '0mm',
                'margin-bottom': '0mm',
                'margin-left': '0mm',
                'encoding': "UTF-8",
                'quiet': ''
            }
            
            # Generate PDF
            pdf = pdfkit.from_string(html, False, options=options)
            
            # Create response
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="bill_{purchase_id}.pdf"'
            return response
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
##Branch manager 

## branch manager permisiion 
class IsManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        else:
            try:
                employee=request.user.employee
                return employee.job_id.job_name.lower()=="manager"
            except AttributeError:
                    return False

## branch manager statistics 

class BranchManagerStatisticsView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        try:
            # Get the manager's branch from their employee record
            employee = request.user.employee
            branch = employee.branch_id
        except AttributeError:
            return Response(
                {"error": "Employee record not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get filter parameters from query params
        period = request.query_params.get('period', 'all')  # 'daily', 'monthly', 'annual', or 'all'
        date_str = request.query_params.get('date', None)  # Format depends on period
        
        # Base queryset for the specific branch
        sold_products = SoldProduct.objects.filter(purchase_id__branch_id=branch)

        # Date filtering logic
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

        # Calculate statistics
        total_sales = sold_products.aggregate(
            total=Sum(F('selling_price') * F('quantity'))
        )['total'] or 0

        total_profits = sold_products.aggregate(
            total=Sum((F('selling_price') - F('main_price')) * F('quantity'))
        )['total'] or 0

        total_products_sold = sold_products.aggregate(
            total=Sum('quantity')
        )['total'] or 0

        # Get most sold product with details
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
class BranchManagerProductsView(APIView):
    permission_classes = [IsAuthenticated, IsManager]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get(self, request):
        """
        Get products available in the manager's branch with filtering options
        """
        try:
            # Get the manager's branch
            branch = request.user.employee.branch_id
            
            # Get products with quantity > 0 in this branch
            branch_products = BranchProducts.objects.filter(
                branch_id=branch,
                quantity__gt=0
            ).select_related(
                'product_id__category_id'
            ).prefetch_related(
                'product_id__phone_set'
            )
            
            # Apply filters from ProductFilter
            filtered_products = self.filterset_class(
                request.GET, 
                queryset=Product.objects.filter(
                    pk__in=[bp.product_id.pk for bp in branch_products]
                )
            ).qs
            
            # Prepare response data with branch quantity
            response_data = []
            for product in filtered_products:
                bp = branch_products.get(product_id=product)
                product_data = {
                    'product_id': product.product_id,
                    'product_name': product.product_name,
                    'category': product.category_id.category_name,
                    'main_price': float(product.main_price),
                    'sale_price': float(product.sale_price),
                    'branch_quantity': bp.quantity,
                }
                
                # Add phone specs if product is a mobile
                if product.category_id.category_name.lower() in ['phone', 'mobile']:
                    phone = product.phone_set.first()
                    if phone:
                        product_data.update({
                            'brand': phone.brand_id.brand_name,
                            'color': phone.color_id.color_name,
                            'storage': phone.storage,
                            'battery': phone.battery,
                            'front_camera': phone.camera_id.front_camera,
                            'back_camera': phone.camera_id.back_camera,
                            'ram': phone.ram,
                            'display_size': float(phone.display_size)
                        })
                
                response_data.append(product_data)
            
            return Response(response_data)
            
        except AttributeError:
            return Response(
                {"error": "Employee record not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
            
class BranchManagerPhoneDetailView(APIView):
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

class BranchManagerAccessoryDetailView(APIView):
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
class BranchManagerOrderProductsView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Show available warehouse products with quantity > 0 and search functionality"""
        search_query = request.query_params.get('search', '').strip()
        
        # Base queryset - only products with available quantity
        warehouse_products = Product.objects.filter(
            quantity__gt=0
        ).select_related('category_id').prefetch_related('phone_set')
        
        # Apply search filter if provided
        if search_query:
            warehouse_products = warehouse_products.filter(
                Q(product_name__icontains=search_query) |
                Q(product_id__icontains=search_query) |
                Q(category_id__category_name__icontains=search_query) |
                Q(phone_set__brand_id__brand_name__icontains=search_query) |
                Q(phone_set__color_id__color_name__icontains=search_query)
            ).distinct()
        
        serializer = ProductSerializer(warehouse_products, many=True)
        
        # Format response with warehouse quantity
        response_data = [{
            'product_id': p['product_id'],
            'product_name': p['product_name'],
            'category': p['category_id']['category_name'],
            'warehouse_quantity': p['quantity'],
            'main_price': float(p['main_price']),
            'sale_price': float(p['sale_price']),
            'specs': self._get_product_specs(p) if p['category_id']['category_name'].lower() in ['phone', 'mobile'] else None
        } for p in serializer.data]
        
        return Response(response_data)


    def _get_product_specs(self, product_data):
        """Helper method to get phone specs if product is a mobile"""
        if not product_data.get('phone_set'):
            return None
            
        phone = product_data['phone_set'][0]  # Get first phone entry
        return {
            'brand': phone['brand_id']['brand_name'],
            'color': phone['color_id']['color_name'],
            'storage': phone['storage'],
            'battery': phone['battery'],
            'front_camera': phone['camera_id']['front_camera'],
            'back_camera': phone['camera_id']['back_camera']
        }

    @transaction.atomic
    def post(self, request):
        """Create a new product order from warehouse"""
        try:
            branch = request.user.employee.branch_id
            products_data = request.data.get('products', [])
            note = request.data.get('note', '')

            if not products_data:
                return Response(
                    {"error": "At least one product is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the order
            order = BranchOrder.objects.create(
                branch_id=branch,
                note=note,
                date_of_order=timezone.now(),
                is_done=False  # Initially not fulfilled
            )

            results = []
            for product_data in products_data:
                product_id = product_data.get('product_id')
                quantity = product_data.get('quantity')

                if not product_id or not quantity:
                    results.append({
                        "product_id": product_id,
                        "status": "failed",
                        "reason": "Missing product_id or quantity"
                    })
                    continue

                try:
                    product = Product.objects.get(pk=product_id)
                    if product.quantity < quantity:
                        results.append({
                            "product_id": product_id,
                            "status": "failed",
                            "reason": f"Insufficient warehouse quantity (available: {product.quantity})"
                        })
                        continue

                    # Create order item
                    RequestedProducts.objects.create(
                        order_id=order,
                        product_id=product,
                        quantity=quantity,
                        status='P'  # Pending
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

            return Response({
                "order_id": order.order_id,
                "branch_id": branch.branch_id,
                "branch_location": branch.location,
                "date_of_order": order.date_of_order,
                "note": note,
                "products": results
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
### branch manager requested product logs view 

class RequestedProductsLogView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        # Get the manager's branch
        branch = request.user.employee.branch_id
        
        # Get ordering parameter (default to newest first)
        order_by = request.query_params.get('order_by', '-order_id__date_of_order')
        
        # Get requested products with related data
        requested_products = RequestedProducts.objects.filter(
            order_id__branch_id=branch
        ).select_related(
            'order_id__branch_id',
            'product_id__category_id'
        ).order_by(order_by)
        
        serializer = RequestedProductsLogSerializer(requested_products, many=True)
        return Response(serializer.data)

class RequestedProductDetailView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, pk):
        branch = request.user.employee.branch_id
        
        # Verify the requested product belongs to manager's branch
        requested_product = get_object_or_404(
            RequestedProducts.objects.select_related(
                'order_id__branch_id',
                'product_id__category_id'
            ),
            pk=pk,
            order_id__branch_id=branch
        )
        
        serializer = RequestedProductDetailSerializer(requested_product)
        return Response(serializer.data)


### sold products for branch manager 
class SoldProductsLogView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        # Get the manager's branch
        branch = request.user.employee.branch_id
        
        # Get ordering parameter (default to newest first)
        order_by = request.query_params.get('order_by', '-date_of_purchase')
        
        # Get purchases with calculated totals
        purchases = Purchase.objects.filter(
            branch_id=branch
        ).annotate(
            total_amount=Sum(F('soldproduct__selling_price') * F('soldproduct__quantity')),
            total_items=Sum('soldproduct__quantity')
        ).order_by(order_by)
        
        serializer = SoldProductsLogSerializer(purchases, many=True)
        return Response(serializer.data)

class SoldProductPurchaseDetailView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, purchase_id):
        branch = request.user.employee.branch_id
        
        # Verify purchase belongs to manager's branch
        purchase = get_object_or_404(
            Purchase,
            branch_id=branch,
            purchase_id=purchase_id
        )
        
        sold_products = purchase.soldproduct_set.select_related(
            'product_id__category_id'
        ).all()
        
        serializer = SoldProductDetailSerializer(sold_products, many=True)
        
        # Add purchase summary
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

### warehouse permission 
class IsWarehouseManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        else:
            try:
                employee=request.user.employee
                return employee.job_id.job_name.lower()=="warehouse manager"
            except AttributeError:
                return False
    
class WarehouseProductView(APIView):
    permission_classes=[IsWarehouseManager]
    filter_backends=[DjangoFilterBackend]
    filterset_class=ProductFilter
    
    def get(self,request):
        queryset = Product.objects.select_related('category_id').prefetch_related('phone_set').all()
        filtered_queryset=self.filterset_class(request.GET,queryset=queryset).qs
        serializer = ProductSerializer(filtered_queryset, many=True)
        return Response(serializer.data)
    
class PhoneManagementView(APIView):
    permission_classes=[IsWarehouseManager]
    def get_phone(self,pk):
        try:
            return Phone.objects.get(product_id=pk)
        except Phone.DoesNotExist:
                return None
    def put(self,request,pk):
        phone=self.get_phone(pk)
        if not phone:
            return Response({"error":"phone not found"},status=status.HTTP_404_NOT_FOUND)
        serializer=PhoneSerializer(phone,data=request.data)
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


class AccessoryManagementView(APIView):
    permission_classes=[IsWarehouseManager]
    
    
    def get_accessory(self,requset,pk):
        try:
            return Accessories.objects.get(product_id=pk)
        except Accessories.DoesNotExist():
            return None
    
    def put(self,request,pk):
        accessory=self.get_accessory(pk)
        if not accessory:
            return Response({"error":"not found"},status=status.HTTP_404_NOT_FOUND)
        serializer=AccessoriesSerializer(accessory,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk):
        accessory=self.get_accessory(pk)
        if not accessory:
            return Response({"error":"not found"},status=status.HTTP_404_NOT_FOUND)
        accessory.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AddProduct(APIView):
    permission_classes=[IsWarehouseManager]
    
    def post(self,request):
        serializer=ProductSerializer(data=request.data)
        if serializer.is_valid():
            product=serializer.save()
            if product.category_id.category_name.lower() in ['phone', 'mobile']:
                    Phone.objects.create(product_id=product, **request.data.get('phone_specs', {}))
            else:
                Accessories.objects.create(product_id=product, **request.data.get('accessory_specs', {}))
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EditMultiple(APIView):
    permission_classes=[IsWarehouseManager]
    
    def put(self, request):
        updates = request.data.get('updates', [])
        if not updates:
            return Response({"error": "No updates provided"}, status=400)
    
        updated_ids = []
        for item in updates:
            product = Product.objects.filter(product_id=item['product_id']).update(
                quantity=item.get('quantity'),
                sale_price=item.get('sale_price'),
                main_price=item.get('main_price')
        )
            if product:
                updated_ids.append(item['product_id'])
    
        return Response({"updated_products": updated_ids})
    
## SEND PRODUCT TO BRANCH 
from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

class WarehouseSendProductsView(APIView):
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    filter_backends = [SearchFilter]
    search_fields = ['product_name']

    def get(self, request):
        """List available warehouse products with search"""
        search_query = request.query_params.get('search', '')
        
        products = Product.objects.filter(quantity__gt=0)
        if search_query:
            products = products.filter(product_name__icontains=search_query)
            
        serializer = WarehouseProductSerializer(
            products.select_related('category_id').prefetch_related('phone_set'), 
            many=True
        )
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        """Send products to a branch"""
        serializer = SendProductsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        branch_name = serializer.validated_data['branch_name']
        products_data = serializer.validated_data['products']

        try:
            branch = Branch.objects.get( location__icontains=branch_name.strip())
        except Branch.DoesNotExist:
            return Response(
                {"error": f"Branch '{branch_name}' not found. Available branches: {list(Branch.objects.values_list('location', flat=True))}"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Branch.MultipleObjectsReturned:
            return Response(
                {"error": f"Multiple branches match '{branch_name}'. Please be more specific."},
                status=status.HTTP_400_BAD_REQUEST
            )

        results = []
        for product_data in products_data:
            product_id = product_data['product_id']
            quantity = product_data['quantity']

            try:
                product = Product.objects.select_for_update().get(pk=product_id)
                
                if product.quantity < quantity:
                    results.append({
                        "product_id": product_id,
                        "status": "failed",
                        "reason": f"Insufficient stock (available: {product.quantity})"
                    })
                    continue

                # Update warehouse stock
                product.quantity -= quantity
                product.save()

                # Update branch stock (create or update)
                branch_product, created = BranchProducts.objects.get_or_create(
                    branch_id=branch,
                    product_id=product,
                    defaults={'quantity': quantity}
                )
                if not created:
                    branch_product.quantity += quantity
                    branch_product.save()

                results.append({
                    "product_id": product_id,
                    "status": "success",
                    "quantity_sent": quantity,
                    "new_warehouse_stock": product.quantity,
                    "new_branch_stock": branch_product.quantity
                })

            except Product.DoesNotExist:
                results.append({
                    "product_id": product_id,
                    "status": "failed",
                    "reason": "Product not found"
                })

        return Response({
            "branch_id": branch.branch_id,
            "branch_name": branch.location,
            "products": results
        }, status=status.HTTP_201_CREATED)
        
## retrieve from branch 
from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

class WarehouseRetrieveProductsView(APIView):
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    filter_backends = [SearchFilter]
    search_fields = ['product_id__product_name']

    def get(self, request):
        """List products in a specific branch with search"""
        branch_id = request.query_params.get('branch_id')
        search_query = request.query_params.get('search', '')
        
        if not branch_id:
            return Response(
                {"error": "branch_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        products = BranchProducts.objects.filter(branch_id=branch_id)
        
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
        """Retrieve products from branch back to warehouse"""
        serializer = RetrieveProductsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        branch_id = serializer.validated_data['branch_id']
        products_data = serializer.validated_data['products']

        try:
            branch = Branch.objects.get(pk=branch_id)
        except Branch.DoesNotExist:
            return Response(
                {"error": "Branch not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        results = []
        for product_data in products_data:
            product_id = product_data['product_id']
            quantity = product_data['quantity']

            try:
                # Get branch product with lock
                branch_product = BranchProducts.objects.select_for_update().get(
                    branch_id=branch,
                    product_id=product_id
                )
                
                if branch_product.quantity < quantity:
                    results.append({
                        "product_id": product_id,
                        "status": "failed",
                        "reason": f"Insufficient branch stock (available: {branch_product.quantity})"
                    })
                    continue

                # Get or create warehouse product
                product = Product.objects.get(pk=product_id)
                
                # Update quantities
                branch_product.quantity -= quantity
                branch_product.save()
                
                product.quantity += quantity
                product.save()

                results.append({
                    "product_id": product_id,
                    "status": "success",
                    "quantity_retrieved": quantity,
                    "new_branch_stock": branch_product.quantity,
                    "new_warehouse_stock": product.quantity
                })

            except (BranchProducts.DoesNotExist, Product.DoesNotExist):
                results.append({
                    "product_id": product_id,
                    "status": "failed",
                    "reason": "Product not found in branch/warehouse"
                })

        return Response({
            "branch_id": branch.branch_id,
            "branch_name": branch.location,
            "products": results
        }, status=status.HTTP_200_OK)
    
### products log movement 

class WarehouseManagerProductsLog(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    serializer_class = ProductTransactionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductTransactionFilter
    
    def get_queryset(self):
        # Get all transactions with related data
        return ProductTransaction.objects.select_related(
            'branch_id'
        ).prefetch_related(
            'transportedproducts_set__product_id__category_id'
        ).order_by('-date_of_transaction')

class WarehouseManagerProductLogDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    serializer_class = ProductTransactionSerializer
    queryset = ProductTransaction.objects.all()
    lookup_field = 'process_id'

### manage requests from the branches 
class WarehouseManagerRequests(APIView):
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    
    def get(self, request):
        """
        Get all pending branch requests with detailed product information
        """
        orders = BranchOrder.objects.filter(
            is_done=False
        ).select_related(
            'branch_id',
            'branch_id__manager_id'
        ).prefetch_related(
            'requestedproducts_set__product_id__category_id',
            'requestedproducts_set__product_id'
        ).order_by('date_of_order')

        serializer = BranchOrderSerializer(orders, many=True)
        return Response({
            'count': orders.count(),
            'requests': serializer.data
        })

    @transaction.atomic
    def post(self, request, order_id=None):
        """
        Process a branch request (approve/reject/partial)
        """
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

        serializer = ProcessRequestSerializer(data=request.data)
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

        # Validate stock first
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

        # Process all products
        for rp in requested_products:
            self._transfer_product(rp, rp.quantity)
            rp.status = 'S'
            rp.save()

        order.is_done = True
        order.save()

        return Response({
            "status": "approved",
            "order_id": order.order_id,
            "transferred_products": RequestedProductSerializer(
                requested_products,
                many=True
            ).data
        })

    def _reject_full_order(self, order, rejection_reason):
        requested_products = order.requestedproducts_set.all()

        for rp in requested_products:
            rp.status = 'R'
            rp.rejection_reason = rejection_reason
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
                    results['approved'].append({
                        "product_id": rp.product_id.product_id,
                        "quantity": quantity
                    })
                
                elif product_action['action'] == 'reject':
                    rp.status = 'R'
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
        """Atomic transfer of products from warehouse to branch"""
        # Deduct from warehouse
        Product.objects.filter(
            pk=requested_product.product_id.pk
        ).update(quantity=F('quantity') - quantity)
        
        # Add to branch
        BranchProducts.objects.update_or_create(
            branch_id=requested_product.order_id.branch_id,
            product_id=requested_product.product_id,
            defaults={'quantity': F('quantity') + quantity}
        )
        
        
### Warehouse requests logs 
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import BranchOrder
from .serializers import BranchOrderLogSerializer
from .filters import BranchOrderFilter
from django.shortcuts import get_object_or_404

class WarehouseManagerRequestLogs(APIView):
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BranchOrderFilter
    pagination_class = PageNumberPagination

    def get(self, request):
        queryset = BranchOrder.objects.select_related(
            'branch_id__city_id',
            'branch_id__manager_id'
        ).prefetch_related(
            'requestedproducts_set__product_id__category_id'
        ).order_by('-date_of_order')

        # Apply filters
        filtered_queryset = self.filterset_class(request.GET, queryset=queryset).qs

        # Pagination
        page = self.pagination_class()
        page_queryset = page.paginate_queryset(filtered_queryset, request)
        
        serializer = BranchOrderLogSerializer(page_queryset, many=True)
        return page.get_paginated_response(serializer.data)

class WarehouseManagerRequestLogDetail(APIView):
    permission_classes = [IsAuthenticated, IsWarehouseManager]

    def get(self, request, order_id):
        order = get_object_or_404(
            BranchOrder.objects.select_related(
                'branch_id__city_id',
                'branch_id__manager_id'
            ).prefetch_related(
                'requestedproducts_set__product_id__category_id'
            ),
            order_id=order_id
        )
        serializer = BranchOrderLogSerializer(order)
        return Response(serializer.data)
##settings
# Phone Brand Views
class PhoneBrandListCreateView(generics.ListCreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    filterset_fields = ['is_active']
    search_fields = ['name']

class PhoneBrandRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    lookup_field = 'brand_id'

# Color Views
class ColorListCreateView(generics.ListCreateAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    filterset_fields = ['is_active']
    search_fields = ['name']

class ColorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    lookup_field = 'color_id'

# Accessory Type Views
class AccessoryTypeListCreateView(generics.ListCreateAPIView):
    queryset = AccessoriesType.objects.all()
    serializer_class = AccessoriesTypeSerializer
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    filterset_fields = ['is_active']
    search_fields = ['name']

class AccessoryTypeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccessoriesType.objects.all()
    serializer_class = AccessoriesTypeSerializer
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    lookup_field = 'accessory_type_id'