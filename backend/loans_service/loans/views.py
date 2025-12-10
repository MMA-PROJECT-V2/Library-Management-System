from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Loan, LoanHistory
from .serializers import LoanSerializer, LoanCreateSerializer, LoanHistorySerializer
from .services.user_client import UserServiceClient
from .services.book_client import BookServiceClient
from .permissions import (
    IsAuthenticated, CanBorrowBook, CanViewLoans, 
    CanViewAllLoans, CanManageLoans, IsLibrarianOrAdmin
)

logger = logging.getLogger(__name__)


# ============================================
#    HEALTH CHECK
# ============================================

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({
        'status': 'healthy',
        'service': 'loans',
        'timestamp': timezone.now()
    })


# ============================================
#    US7: EMPRUNTER UN LIVRE
# ============================================

@api_view(['POST'])
@permission_classes([IsAuthenticated, CanBorrowBook])
def create_loan(request):
    """
    Create a new loan (borrow a book).
    
    POST /api/loans/
    
    Required permissions: can_borrow_book
    """
    create_serializer = LoanCreateSerializer(data=request.data)
    if not create_serializer.is_valid():
        return Response(
            {
                'error': 'Données invalides',
                'details': create_serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user_id = create_serializer.validated_data['user_id']
    book_id = create_serializer.validated_data['book_id']
    notes = create_serializer.validated_data.get('notes', '')
    
    # Verify user can only borrow for themselves (unless librarian/admin)
    if not request.user.is_librarian() and not request.user.is_admin():
        if user_id != request.user.id:
            return Response(
                {'error': 'Vous ne pouvez emprunter que pour vous-même'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    user_client = UserServiceClient()
    book_client = BookServiceClient()
    
    # 1. Verify user exists and is active
    if not user_client.is_user_active(user_id):
        return Response(
            {'error': 'Utilisateur introuvable ou inactif'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # 2. Verify book exists and is available
    book_data = book_client.get_book(book_id)
    if not book_data:
        return Response(
            {'error': 'Livre introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if book_data.get('available_copies', 0) <= 0:
        return Response(
            {
                'error': 'Livre indisponible',
                'available_copies': 0,
                'book_title': book_data.get('title')
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 3. Verify user has less than 5 active loans
    active_loans_count = Loan.objects.filter(
        user_id=user_id,
        status__in=['ACTIVE', 'RENEWED', 'OVERDUE']
    ).count()
    
    if active_loans_count >= 5:
        return Response(
            {
                'error': 'Quota d\'emprunts dépassé',
                'active_loans': active_loans_count,
                'max_loans': 5
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 4. Verify user doesn't already have this book
    if Loan.objects.filter(
        user_id=user_id,
        book_id=book_id,
        status__in=['ACTIVE', 'RENEWED', 'OVERDUE']
    ).exists():
        return Response(
            {'error': 'Vous avez déjà emprunté ce livre'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 5. Create loan with transaction
    try:
        with transaction.atomic():
            # Calculate due_date (loan_date + 14 days)
            loan_date = timezone.now().date()
            due_date = loan_date + timedelta(days=14)
            
            loan = Loan.objects.create(
                user_id=user_id,
                book_id=book_id,
                loan_date=loan_date,
                due_date=due_date,
                notes=notes,
                status='ACTIVE'
            )
            
            # 6. Decrement book stock
            if not book_client.decrement_stock(book_id):
                raise Exception("Échec de la décrémentation du stock")
            
            # 7. Create audit log
            LoanHistory.objects.create(
                loan_id=loan.id,
                action='CREATED',
                performed_by=request.user.id,
                details=f"Emprunt créé pour le livre '{book_data.get('title')}'"
            )
            
            serializer = LoanSerializer(loan)
            return Response(
                {
                    'message': 'Emprunt créé avec succès',
                    'loan': serializer.data,
                    'book_title': book_data.get('title'),
                    'due_date': loan.due_date.strftime('%d/%m/%Y')
                },
                status=status.HTTP_201_CREATED
            )
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'emprunt: {e}")
        return Response(
            {'error': 'Erreur lors de la création de l\'emprunt'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================
#    US8: RETOURNER UN LIVRE
# ============================================

@api_view(['PUT'])
@permission_classes([IsAuthenticated, CanBorrowBook])
def return_loan(request, pk):
    """
    Return a borrowed book.
    
    PUT /api/loans/{id}/return/
    
    Required permissions: can_borrow_book
    """
    try:
        loan = Loan.objects.get(id=pk)
    except Loan.DoesNotExist:
        return Response(
            {'error': 'Emprunt non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verify user can only return their own loans (unless librarian/admin)
    if not request.user.is_librarian() and not request.user.is_admin():
        if loan.user_id != request.user.id:
            return Response(
                {'error': 'Vous ne pouvez retourner que vos propres emprunts'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    # Verify loan is active or overdue
    if loan.status not in ['ACTIVE', 'OVERDUE', 'RENEWED']:
        return Response(
            {'error': f'Ce livre a déjà été retourné (statut: {loan.status})'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    book_client = BookServiceClient()
    
    try:
        with transaction.atomic():
            # Mark as returned and calculate fine if overdue
            return_date = timezone.now().date()
            loan.return_date = return_date
            loan.status = 'RETURNED'
            
            # Calculate fine if overdue (50 DZD per day)
            fine_amount = 0
            if return_date > loan.due_date:
                days_overdue = (return_date - loan.due_date).days
                fine_amount = days_overdue * 50
                loan.fine_amount = fine_amount
            
            loan.save()
            
            # Increment book stock
            if not book_client.increment_stock(loan.book_id):
                raise Exception("Échec de l'incrémentation du stock")
            
            # Create audit log
            details = f"Livre retourné"
            if fine_amount > 0:
                details += f" avec {days_overdue} jour(s) de retard. Amende: {fine_amount} DZD"
            
            LoanHistory.objects.create(
                loan_id=loan.id,
                action='RETURNED',
                performed_by=request.user.id,
                details=details
            )
            
            serializer = LoanSerializer(loan)
            response_data = {
                'message': 'Livre retourné avec succès',
                'loan': serializer.data
            }
            
            if fine_amount > 0:
                response_data['fine'] = {
                    'amount': fine_amount,
                    'days_overdue': days_overdue,
                    'message': f'Amende de {fine_amount} DZD pour {days_overdue} jour(s) de retard'
                }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Erreur lors du retour: {e}")
        return Response(
            {'error': 'Erreur lors du retour du livre'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================
#    US9: RENOUVELER UN EMPRUNT
# ============================================

@api_view(['PUT'])
@permission_classes([IsAuthenticated, CanBorrowBook])
def renew_loan(request, pk):
    """
    Renew a loan (extend due date by 14 days).
    
    PUT /api/loans/{id}/renew/
    
    Max 2 renewals. Cannot renew if overdue.
    Required permissions: can_borrow_book
    """
    try:
        loan = Loan.objects.get(id=pk)
    except Loan.DoesNotExist:
        return Response(
            {'error': 'Emprunt non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verify user can only renew their own loans (unless librarian/admin)
    if not request.user.is_librarian() and not request.user.is_admin():
        if loan.user_id != request.user.id:
            return Response(
                {'error': 'Vous ne pouvez renouveler que vos propres emprunts'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    # Verify loan status is ACTIVE (not OVERDUE, not RETURNED)
    if loan.status != 'ACTIVE' and loan.status != 'RENEWED':
        return Response(
            {'error': f'Impossible de renouveler: statut {loan.status}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify not overdue
    if loan.is_overdue():
        return Response(
            {'error': 'Impossible de renouveler un emprunt en retard'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify renewal count < max_renewals (2)
    if loan.renewal_count >= loan.max_renewals:
        return Response(
            {
                'error': 'Nombre maximum de renouvellements atteint',
                'renewal_count': loan.renewal_count,
                'max_renewals': loan.max_renewals
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Renew loan
    loan.due_date = loan.due_date + timedelta(days=14)
    loan.renewal_count += 1
    loan.status = 'RENEWED'
    loan.save()
    
    # Create audit log
    LoanHistory.objects.create(
        loan_id=loan.id,
        action='RENEWED',
        performed_by=request.user.id,
        details=f"Renouvellement #{loan.renewal_count}. Nouvelle date de retour: {loan.due_date}"
    )
    
    serializer = LoanSerializer(loan)
    return Response(
        {
            'message': 'Emprunt renouvelé avec succès',
            'loan': serializer.data,
            'new_due_date': loan.due_date.strftime('%d/%m/%Y'),
            'renewals_remaining': loan.max_renewals - loan.renewal_count
        },
        status=status.HTTP_200_OK
    )


# ============================================
#    US9: CONSULTER EMPRUNTS
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewLoans])
def user_loans(request, user_id):
    """
    Get all loans for a specific user (history).
    
    GET /api/loans/user/{user_id}/
    
    Required permissions: can_view_loans
    """
    # Verify user can only view their own loans (unless librarian/admin)
    if not request.user.is_librarian() and not request.user.is_admin():
        if user_id != request.user.id:
            return Response(
                {'error': 'Vous ne pouvez consulter que vos propres emprunts'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    loans = Loan.objects.filter(user_id=user_id).order_by('-created_at')
    serializer = LoanSerializer(loans, many=True)
    
    return Response({
        'count': loans.count(),
        'loans': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewLoans])
def user_active_loans(request, user_id):
    """
    Get active loans for a specific user.
    
    GET /api/loans/user/{user_id}/active/
    
    Required permissions: can_view_loans
    """
    # Verify user can only view their own loans (unless librarian/admin)
    if not request.user.is_librarian() and not request.user.is_admin():
        if user_id != request.user.id:
            return Response(
                {'error': 'Vous ne pouvez consulter que vos propres emprunts'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    loans = Loan.objects.filter(
        user_id=user_id,
        status__in=['ACTIVE', 'RENEWED', 'OVERDUE']
    ).order_by('-created_at')
    
    serializer = LoanSerializer(loans, many=True)
    
    return Response({
        'count': loans.count(),
        'active_loans': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewAllLoans])
def active_loans(request):
    """
    Get all active loans (LIBRARIAN only).
    
    GET /api/loans/active/
    
    Required permissions: can_view_all_loans
    """
    loans = Loan.objects.filter(
        status__in=['ACTIVE', 'RENEWED', 'OVERDUE']
    ).order_by('-created_at')
    
    serializer = LoanSerializer(loans, many=True)
    
    return Response({
        'count': loans.count(),
        'active_loans': serializer.data
    })


# ============================================
#    US10: EMPRUNTS EN RETARD
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewAllLoans])
def overdue_loans(request):
    """
    Get all overdue loans (LIBRARIAN/ADMIN only).
    
    GET /api/loans/overdue/
    
    Required permissions: can_view_all_loans
    """
    today = timezone.now().date()
    loans = Loan.objects.filter(
        due_date__lt=today,
        status__in=['ACTIVE', 'RENEWED', 'OVERDUE']
    ).order_by('due_date')
    
    serializer = LoanSerializer(loans, many=True)
    
    return Response({
        'count': loans.count(),
        'overdue_loans': serializer.data
    })


# ============================================
#    GENERIC ENDPOINTS
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewAllLoans])
def loan_list(request):
    """
    Get all loans (LIBRARIAN/ADMIN only).
    
    GET /api/loans/list/
    
    Required permissions: can_view_all_loans
    """
    loans = Loan.objects.all().order_by('-created_at')
    serializer = LoanSerializer(loans, many=True)
    
    return Response({
        'count': loans.count(),
        'loans': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewLoans])
def loan_detail(request, pk):
    """
    Get loan details.
    
    GET /api/loans/{id}/
    
    Required permissions: can_view_loans
    """
    try:
        loan = Loan.objects.get(id=pk)
    except Loan.DoesNotExist:
        return Response(
            {'error': 'Emprunt non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verify user can only view their own loans (unless librarian/admin)
    if not request.user.is_librarian() and not request.user.is_admin():
        if loan.user_id != request.user.id:
            return Response(
                {'error': 'Vous ne pouvez consulter que vos propres emprunts'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    serializer = LoanSerializer(loan)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewLoans])
def loan_history(request, pk):
    """
    Get loan history (audit log).
    
    GET /api/loans/{id}/history/
    
    Required permissions: can_view_loans
    """
    try:
        loan = Loan.objects.get(id=pk)
    except Loan.DoesNotExist:
        return Response(
            {'error': 'Emprunt non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verify user can only view their own loans (unless librarian/admin)
    if not request.user.is_librarian() and not request.user.is_admin():
        if loan.user_id != request.user.id:
            return Response(
                {'error': 'Vous ne pouvez consulter que vos propres emprunts'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    history = LoanHistory.objects.filter(loan_id=pk).order_by('-created_at')
    serializer = LoanHistorySerializer(history, many=True)
    
    return Response({
        'loan_id': pk,
        'history': serializer.data
    })