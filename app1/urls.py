from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"categories", views.CategoryViewSet)
router.register(r"products", views.ProductViewSet)
router.register(r"product-categories", views.ProductCategoryViewSet)
# placeorder
router.register(r'orders', views.PlaceOrderViewSet, basename='order')
router.register(r'payments', views.PaymentViewSet, basename='payment')

urlpatterns = [
    # Auth
    path("register/", views.register),
    path("verify/", views.verify_otp),
    path("login/", views.login_view),
    # User CRUD (Function Based)
    path("users/", views.user_list_create),
    path("users/<int:pk>/", views.user_detail),
    # Group CRUD (Class Based)
    path("groups/", views.GroupListCreateView.as_view(), name="group-list-create"),
    path("groups/<int:pk>/", views.GroupDetailView.as_view(), name="group-detail"),
    path("groups/users/", views.users_by_group),  # all groups/users
    
    path(
        "groups/users/<int:group_id>/", views.users_by_group
    ),  # users in specific group
    
    path(
        "groups/create-with-users/", views.add_users_to_group, name="create-group"
    ),  #  create + assign users
    
    # Custom group actions
    path("groups/search/", views.get_groups, name="get-groups"),  # 8 search by name
    path("groups/with-users/", views.group_list_with_users),  # all groups + users

    # order list view 
    path('orders_list/', views.order_list_view, name='order-list'),

    path("", include(router.urls)),
]
