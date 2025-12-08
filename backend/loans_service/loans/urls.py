from django.urls import path
from . import views

urlpatterns = [
    # Liste et création
    path('', views.create_loan, name='loan-create'),
    path('list/', views.loan_list, name='loan-list'),
    
    # Détail
    path('<int:pk>/', views.loan_detail, name='loan-detail'),
]