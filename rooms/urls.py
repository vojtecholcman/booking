from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('pokoje/', views.room_list, name='room_list'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('room/<int:pk>/', views.room_detail, name='room_detail'),
    path('confirm/<int:pk>/', views.confirm, name='confirm'),
    path('menu/', views.menu, name='menu'),
]
