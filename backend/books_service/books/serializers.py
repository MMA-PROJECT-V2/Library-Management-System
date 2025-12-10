from rest_framework import serializers
from .models import Book, BookReview

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"
        extra_kwargs = {
            'description': {'allow_blank': True, 'required': False},
        }

class BookReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookReview
        fields = "__all__"
