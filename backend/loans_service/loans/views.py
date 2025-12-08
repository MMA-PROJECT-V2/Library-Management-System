from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
import logging

from .models import Loan, LoanHistory
from .serializers import (
    LoanSerializer,
    LoanCreateSerializer,
)
from .services.user_client import UserServiceClient
from .services.book_client import BookServiceClient

logger = logging.getLogger(__name__)


@api_view(['POST'])
def create_loan(request):
    """
    Créer un emprunt de livre
    
    POST /loans/
    Body: {
        "user_id": 1,
        "book_id": 5,
        "notes": "optionnel"
    }
    """
    # Validation des données d'entrée
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
    
    # Initialiser les clients de services
    user_client = UserServiceClient()
    book_client = BookServiceClient()
    
    # Vérification 1 : L'utilisateur existe et est actif
    logger.info(f"🔍 Vérification utilisateur {user_id}...")
    if not user_client.is_user_active(user_id):
        return Response(
            {
                'error': 'Utilisateur introuvable ou inactif',
                'message': f"L'utilisateur avec l'ID {user_id} n'existe pas ou est désactivé"
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérification 2 : Le livre existe et est disponible
    logger.info(f"🔍 Vérification livre {book_id}...")
    book_data = book_client.get_book(book_id)
    if not book_data:
        return Response(
            {
                'error': 'Livre introuvable',
                'message': f"Le livre avec l'ID {book_id} n'existe pas"
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    available_copies = book_data.get('available_copies', 0)
    if available_copies <= 0:
        return Response(
            {
                'error': 'Livre indisponible',
                'message': f"Le livre '{book_data.get('title')}' n'est pas disponible actuellement",
                'available_copies': 0
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérification 3 : L'utilisateur n'a pas dépassé le quota d'emprunts actifs (max 5)
    logger.info(f"🔍 Vérification quota emprunts pour user {user_id}...")
    active_loans_count = Loan.objects.filter(
        user_id=user_id,
        status__in=['ACTIVE', 'RENEWED', 'OVERDUE']
    ).count()
    
    if active_loans_count >= 5:
        return Response(
            {
                'error': 'Quota d\'emprunts dépassé',
                'message': f'Vous avez déjà {active_loans_count} emprunt(s) actif(s). Maximum autorisé : 5',
                'active_loans': active_loans_count,
                'max_loans': 5
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérification 4 : L'utilisateur n'a pas déjà emprunté ce livre
    existing_loan = Loan.objects.filter(
        user_id=user_id,
        book_id=book_id,
        status__in=['ACTIVE', 'RENEWED', 'OVERDUE']
    ).first()
    
    if existing_loan:
        return Response(
            {
                'error': 'Livre déjà emprunté',
                'message': f'Vous avez déjà emprunté ce livre (Emprunt #{existing_loan.id})',
                'loan_id': existing_loan.id
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Tout est OK : créer l'emprunt avec transaction atomique
    try:
        with transaction.atomic():
            # Créer l'emprunt
            loan = Loan.objects.create(
                user_id=user_id,
                book_id=book_id,
                notes=notes,
                status='ACTIVE'
            )
            
            # Décrémenter le stock du livre
            if not book_client.decrement_stock(book_id):
                raise Exception("Échec de la décrémentation du stock")
            
            # Créer l'entrée dans l'historique
            LoanHistory.objects.create(
                loan_id=loan.id,
                action='CREATED',
                performed_by=user_id,
                details=f"Emprunt créé pour le livre '{book_data.get('title')}'"
            )
            
            logger.info(f"✅ Emprunt #{loan.id} créé avec succès")
            
            # Retourner la réponse
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
        logger.error(f"❌ Erreur lors de la création de l'emprunt: {e}")
        return Response(
            {
                'error': 'Erreur lors de la création de l\'emprunt',
                'message': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def loan_list(request):
    """
    Liste de tous les emprunts (pour tests)
    
    GET /loans/
    """
    loans = Loan.objects.all()
    serializer = LoanSerializer(loans, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def loan_detail(request, pk):
    """
    Détails d'un emprunt
    
    GET /loans/{id}/
    """
    try:
        loan = Loan.objects.get(pk=pk)
    except Loan.DoesNotExist:
        return Response(
            {'error': 'Emprunt non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = LoanSerializer(loan)
    return Response(serializer.data)