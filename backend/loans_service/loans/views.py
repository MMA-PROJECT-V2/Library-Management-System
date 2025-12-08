# loans/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Loan, LoanHistory
from .serializers import LoanSerializer, LoanHistorySerializer
from django.shortcuts import get_object_or_404


class LoanViewSet(viewsets.ModelViewSet):
    """
    CRUD complet pour les emprunts
    """
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """
        Renouveler un emprunt
        """
        loan = self.get_object()
        if loan.renew():
            # Historique
            LoanHistory.objects.create(
                loan_id=loan.id,
                action='RENEWED',
                performed_by=request.data.get('user_id'),
                details=f"Loan renewed for 14 days"
            )
            return Response({'status': 'loan renewed', 'due_date': loan.due_date})
        return Response({'status': 'cannot renew'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def return_loan(self, request, pk=None):
        """
        Marquer l'emprunt comme retourné
        """
        loan = self.get_object()
        loan.mark_as_returned()
        LoanHistory.objects.create(
            loan_id=loan.id,
            action='RETURNED',
            performed_by=request.data.get('user_id'),
            details=f"Loan returned"
        )
        return Response({'status': 'loan returned', 'fine_amount': loan.fine_amount})


class LoanHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lecture seule pour l'historique des emprunts
    """
    queryset = LoanHistory.objects.all()
    serializer_class = LoanHistorySerializer
