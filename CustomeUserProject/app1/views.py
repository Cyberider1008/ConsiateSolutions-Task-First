import random

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
# from django.core.mail import send_mail

from django_filters.rest_framework import DjangoFilterBackend, FilterSet, BooleanFilter

from rest_framework import status
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
# from rest_framework.authtoken.models import Token

from datetime import timedelta


from .models import (
    CustomUserModel,
    CustomGroupModel,
    PendingUser,
    ExpiringToken,
    Product,
    Category,
    ProductCategory
)


from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    # AddUsrToGrpSerializer,
    OTPVerifySerializer,
    UserSerializer,
    GroupWithUsersSerializer,
    GroupCreateSerializers,
    GroupSerializer,
    ProductSerializer,
    CategorySerializer,
    ProductCategorySerializer

)


#simple Registration and Login with API

# Handle user registration and send OTP to email
@api_view(["POST"])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']

        # Check if user is already waiting for OTP verification
        if PendingUser.objects.filter(username=username).exists():
            return Response({"error": "Email already registered for OTP."}, status=400)

        # Generate 4-digit OTP and save the temporary user
        otp = str(random.randint(1000, 9999))
        serializer.save(otp=otp)

        # Send OTP email to the user
        subject = 'Please verify your email with OTP'
        # message = f'Hi {username},\nYour OTP is: {otp}'

        from_email = 'abaranwal.it@gmail.com'
        to_email = [email]

        context = {'otp': otp, 'username' : username}
        html_content = render_to_string('app1/emails/otp.html', context)
        text_content = 'OTP  here!'


        # Send the email
        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send()

        #     subject,
        # send_mail(
        #     message,
        #     'abaranwal.it@gmail.com',
        #     [email],
        #     fail_silently=False,
        # )


        return Response({'message': 'OTP sent to email'}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Verify OTP and create the actual user account
@api_view(["POST"])
def verify_otp(request):
    serializer = OTPVerifySerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        # Fetch pending user based on email
        try:
            pending_user = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return Response({"error": "No pending user found."}, status=404)

        # Compare submitted OTP with saved one
        if pending_user.otp != otp:
            return Response({"error": "Incorrect OTP"}, status=400)

        # Create actual user from pending user data
        user = CustomUserModel.objects.create_user(
            username= pending_user.username,
            email= pending_user.email,
            password= pending_user.password,
            ph_no= pending_user.ph_no,
            post= pending_user.post,
        )
        user.set_password(pending_user.password)
        user.save()

        #clean up pending user
        pending_user.delete()
        return Response({"message": f"User {user.username} created successfully"}, status=201)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["POST"])
def login_view(request):
    serializer = LoginSerializer(data = request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']

        if user:
            token, created = ExpiringToken.objects.get_or_create(user=user)
            if created:
                token.expires = timezone.now() + timedelta(minutes=1)  # Set token to expire in 1 minute
                token.save()

        return Response({'message': f'Welcome, {user.username}!', 'token': token.key, 'user_id': user.id,'expires_at': token.created + timedelta(minutes=1),}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def add_users_to_group(request):
    serializer = GroupCreateSerializers(data=request.data)

    if serializer.is_valid():
        group_name = serializer.validated_data['name']
        user_ids = serializer.validated_data.get('users', [])

        # Check if the group exists
        group = CustomGroupModel.objects.filter(name=group_name).first()

        if not group:
            return Response({'detail': 'Group does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get users to add
        users = CustomUserModel.objects.filter(id__in=user_ids)
        
        added_users = 0
        for user in users:
            # Check if the user is already part of the group
            if group not in user.groups.all():
                user.groups.add(group)
                added_users += 1

        return Response({
            'detail': f"{added_users} user(s) added to the group '{group_name}'."
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




#################################################################3
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_list_create(request):
    if request.method == 'GET':
        users = CustomUserModel.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    try:
        user = CustomUserModel.objects.get(pk=pk)
    except CustomUserModel.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

##################################
#Create GET API to fetch all user groups and their users
@api_view(['GET'])
def group_list_with_users(request):
    groups = CustomGroupModel.objects.all()
    serializer = GroupWithUsersSerializer(groups, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#Modify the GET API to filter users based on group ID
@api_view(['GET'])
def users_by_group(request, group_id=None):
    print("-------",group_id)
    if group_id is not None:
        try:
            group = CustomGroupModel.objects.get(id=group_id)
            users = group.user_set.all()
            serializer = UserSerializer(users, many=True)
            return Response({'group': group.name, 'users': serializer.data})
        except CustomGroupModel.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Return all groups with users if no group_id is passed
    groups_data = []
    for group in CustomGroupModel.objects.all():
        users = group.user_set.all()
        serializer = UserSerializer(users, many=True)
        groups_data.append({'group': group.name, 'users': serializer.data})

    return Response(groups_data)


# fetch group data from name
@api_view(['GET'])
def get_groups(request):
    group_name = request.GET.get('name', None)

    groups = CustomGroupModel.objects.filter(name__icontains=group_name)
    if groups:
        
        users = set()
        for group in groups:
            for user in group.user_set.all():  
                users.add(user)
        serializer = UserSerializer(users, many = True)
    else:
        groups = CustomGroupModel.objects.all()
        serializer = GroupSerializer(groups, many=True)

    
    return Response(serializer.data, status=status.HTTP_200_OK)







# class based Group CRUD operations
# Create and List Groups
class GroupListCreateView(generics.ListCreateAPIView):
    queryset = CustomGroupModel.objects.all()
    serializer_class = GroupSerializer

# Retrieve, Update, Delete a Group
class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomGroupModel.objects.all()
    serializer_class = GroupSerializer



##########
# Product and Category here

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



class ProductFilter(FilterSet):
    is_active = BooleanFilter(field_name='is_active', lookup_expr='exact')

    class Meta:
        model = Product
        fields = ['is_active']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    # add both search and ordering
    filter_backends = [filters.SearchFilter, filters.OrderingFilter,  DjangoFilterBackend]


    # Add filter class
    filterset_class = ProductFilter


    #Fields that can be searched using ?search=...
    search_fields = ['name', 'description']         # we can use category__name double underscore

    # Fields that can be sorted using ?ordering=...
    ordering_fields = ['id', 'name', 'description']




class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer