from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register),  # 1
    path('verify/', views.verify_otp),  # 2
    path('login/', views.login_view),   # 3

    # User CRUD (Function Based)
    path('users/', views.user_list_create),       # 4
    path('users/<int:pk>/', views.user_detail),     

    # Group CRUD (Class Based)
    path('groups/', views.GroupListCreateView.as_view(), name='group-list-create'), #5
    path('groups/<int:pk>/', views.GroupDetailView.as_view(), name='group-detail'),

    path('groups/users/', views.users_by_group),                                # all groups/users 6
    path('groups/users/<int:group_id>/', views.users_by_group),                 # users in specific group

    path('groups/create-with-users/', views.add_users_to_group, name='create-group'),  # 7 create + assign users
 
    # Custom group actions
    path('groups/search/', views.get_groups, name='get-groups'),                # 8 search by name
    # path('groups/add-user/', views.add_user_to_group),                          # add user to group
    path('groups/with-users/', views.group_list_with_users),                    # all groups + users


]
