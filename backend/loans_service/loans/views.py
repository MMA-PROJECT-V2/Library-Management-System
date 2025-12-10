from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import logging

from .models import Loan, LoanHistory
from .serializers import LoanSerializer, LoanCreateSerializer
from .services.user_client import UserServiceClient
from .services.book_client import BookServiceClient
from rest_framework.generics import ListAPIView, RetrieveAPIView
logger = logging.getLogger(__name__)

class LoanCreateView(APIView):
    """
    Créer un emprunt de livre
    GET  /api/loans/  → instructions pour l'API
    POST /api/loans/  → création d'un emprunt
    """

    def get(self, request):
        return Response({
            "message": "Pour créer un emprunt, utilisez POST avec 'user_id' et 'book_id'.",
            "required_fields": ["user_id", "book_id", "notes (optionnel)"]
        })

    def post(self, request):
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

        user_client = UserServiceClient()
        book_client = BookServiceClient()

        # Vérification utilisateur
        if not user_client.is_user_active(user_id):
            return Response(
                {'error': 'Utilisateur introuvable ou inactif'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Vérification livre
        book_data = book_client.get_book(book_id)
        if not book_data:
            return Response(
                {'error': 'Livre introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )

        if book_data.get('available_copies', 0) <= 0:
            return Response(
                {'error': 'Livre indisponible', 'available_copies': 0},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérification quota utilisateur
        active_loans_count = Loan.objects.filter(
            user_id=user_id,
            status__in=['ACTIVE', 'RENEWED', 'OVERDUE']
        ).count()

        if active_loans_count >= 5:
            return Response(
                {'error': 'Quota d’emprunts dépassé', 'active_loans': active_loans_count, 'max_loans': 5},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérification livre déjà emprunté
        if Loan.objects.filter(
            user_id=user_id,
            book_id=book_id,
            status__in=['ACTIVE', 'RENEWED', 'OVERDUE']
        ).exists():
            return Response(
                {'error': 'Livre déjà emprunté'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Création de l'emprunt
        try:
            with transaction.atomic():
                loan = Loan.objects.create(
                    user_id=user_id,
                    book_id=book_id,
                    notes=notes,
                    status='ACTIVE'
                )

                if not book_client.decrement_stock(book_id):
                    raise Exception("Échec de la décrémentation du stock")

                LoanHistory.objects.create(
                    loan_id=loan.id,
                    action='CREATED',
                    performed_by=user_id,
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
                {'error': 'Erreur lors de la création de l’emprunt', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoanListView(ListAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

class LoanDetailView(RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer