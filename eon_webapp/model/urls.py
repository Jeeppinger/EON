from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('index/', views.Index.as_view(), name='model_index'),
    url(r'CreateUserModel/', views.CreateUserModel.as_view(),name='Create-UserModel'),

    #url('DetailedUserModel', views.DetailedUserModel.as_view(),name='Detailed-UserModel'),
    path(r'DisplayUserModel/<int:pk>/', views.DetailedUserModel.as_view(),name='Display-UserModel'),
    path(r'DisplayUserModel/CreateModelView/', views.CreateModelViewForm,name='Display-UserModelView'),
    #path(r'Display_UserModel/<int:pk>/CreateModelViewForm/<int::editView>', views.DetailedUserModel.as_view(),name='Display-ModelGraphicalView'),
    path(r'UpdateUserModel/<int:pk>/', views.UpdateUserModel.as_view(),name='Update-UserModel'),
    path(r'DeleteUserModel/<int:pk>/', views.UserModelDelete.as_view(),name='Delete-UserModel'),
]