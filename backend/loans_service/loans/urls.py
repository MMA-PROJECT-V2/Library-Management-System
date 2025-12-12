from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health-check'),
    
    # US7: Emprunter un livre
    path('', views.create_loan, name='loan-create'),
    
    # US8: Retourner un livre
    path('<int:pk>/return/', views.return_loan, name='loan-return'),
    
    # US9: Renouveler un emprunt
    path('<int:pk>/renew/', views.renew_loan, name='loan-renew'),
    
    # US9: Consulter emprunts
    path('user/<int:user_id>/', views.user_loans, name='user-loans'),
    path('user/<int:user_id>/active/', views.user_active_loans, name='user-active-loans'),
    path('active/', views.active_loans, name='active-loans'),
    
    # US10: Emprunts en retard
    path('overdue/', views.overdue_loans, name='overdue-loans'),
    
    # Endpoints génériques
    path('list/', views.loan_list, name='loan-list'),
    path('<int:pk>/', views.loan_detail, name='loan-detail'),
    path('<int:pk>/history/', views.loan_history, name='loan-history'),
    
     path('send-overdue-notifications/', views.send_overdue_notifications, name='send-overdue-notifications'),

]