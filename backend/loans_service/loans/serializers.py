from rest_framework import serializers
from .models import Loan, LoanHistory


class LoanSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Loan
    """
    # Champs en lecture seule
    loan_date = serializers.DateField(read_only=True)
    due_date = serializers.DateField(read_only=True)
    status = serializers.CharField(read_only=True)
    fine_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    renewal_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    # Champs calculés
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    can_renew = serializers.SerializerMethodField()
    
    class Meta:
        model = Loan
        fields = [
            'id',
            'user_id',
            'book_id',
            'loan_date',
            'due_date',
            'return_date',
            'status',
            'fine_amount',
            'fine_paid',
            'renewal_count',
            'max_renewals',
            'notes',
            'is_overdue',
            'days_until_due',
            'can_renew',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'loan_date',
            'due_date',
            'status',
            'fine_amount',
            'renewal_count',
            'created_at',
            'updated_at',
        ]
    
    def get_is_overdue(self, obj):
        """Vérifier si l'emprunt est en retard"""
        return obj.is_overdue()
    
    def get_days_until_due(self, obj):
        """Nombre de jours avant l'échéance"""
        from django.utils import timezone
        if obj.status == 'RETURNED':
            return 0
        delta = obj.due_date - timezone.now().date()
        return delta.days
    
    def get_can_renew(self, obj):
        """Vérifier si l'emprunt peut être renouvelé"""
        return obj.can_renew()


class LoanCreateSerializer(serializers.Serializer):
    """
    Serializer pour la création d'un emprunt
    """
    user_id = serializers.IntegerField(required=True, min_value=1)
    book_id = serializers.IntegerField(required=True, min_value=1)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate_user_id(self, value):
        """Valider que user_id est positif"""
        if value <= 0:
            raise serializers.ValidationError("L'ID utilisateur doit être positif")
        return value
    
    def validate_book_id(self, value):
        """Valider que book_id est positif"""
        if value <= 0:
            raise serializers.ValidationError("L'ID livre doit être positif")
        return value


class LoanHistorySerializer(serializers.ModelSerializer):
    """
    Serializer pour l'historique des emprunts
    """
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = LoanHistory
        fields = [
            'id',
            'loan_id',
            'action',
            'action_display',
            'performed_by',
            'details',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']