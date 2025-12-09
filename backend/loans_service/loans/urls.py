from django.urls import path
from . import views
from .views import  create_loan

urlpatterns = [
    # Liste et création
    path('',create_loan, name='create-loan'),
    path('list/', views.loan_list, name='loan-list'),
    
    # Détail
    path('<int:pk>/', views.loan_detail, name='loan-detail'),
]