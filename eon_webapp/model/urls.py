from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('index/', views.Index.as_view(), name='model_index'),
    url(r'CreateUserModel/', views.CreateUserModel.as_view(),name='Create-UserModel'),

    #url('DetailedUserModel', views.DetailedUserModel.as_view(),name='Detailed-UserModel'),
    # path(r'GraphSpecifyModel/<int:pk>/', views.GraphSpecifyDetailedUserModel.as_view(),name='Display-UserModel'),
    #path(r'Display_UserModel/<int:pk>/CreateModelViewForm/<int::editView>', views.DetailedUserModel.as_view(),name='Display-ModelGraphicalView'),
    path(r'UpdateUserModel/<int:pk>/', views.UpdateUserModel.as_view(),name='Update-UserModel'),
    path(r'DeleteUserModel/<int:pk>/', views.UserModelDelete.as_view(),name='Delete-UserModel'),
    path(r'UpdateGraphJson/<int:model_id>', views.update_graph_json, name='update_graph_json'),
    path(r'View/<int:pk>/', views.view_user_model, name='view_user_model'),
    path(r'PullGit/<int:model_id>',views.pull_from_git, name='pull_from_git')
]
