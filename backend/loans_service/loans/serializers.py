from rest_framework import serializers
from .models import Loan, LoanHistory

class LoanSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)  # ID généré automatiquement
    fine_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    status = serializers.CharField(read_only=True)
    renewal_count = serializers.IntegerField(read_only=True)
    return_date = serializers.DateField(read_only=True)
    
    class Meta:
        model = Loan
        fields = '__all__'


class LoanHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)  # ID généré automatiquement
    created_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = LoanHistory
        fields = '__all__'
