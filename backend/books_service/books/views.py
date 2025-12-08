from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Book, BookReview
from django.db.models import Q
from .serializers import BookSerializer, BookReviewSerializer
import html
from .permissions import (
    CanViewBooks, CanAddBook, CanEditBook, 
    CanDeleteBook, CanBorrowBook, IsLibrarianOrAdmin
)

# ============================================
#    PUBLIC ENDPOINTS (No authentication required)
# ============================================

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for monitoring."""
    return Response({'status': 'healthy', 'service': 'books'})


# GET /books
@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewBooks])
def list_books(request):
    paginator = PageNumberPagination()
    # allow client to set page size via ?page_size=
    paginator.page_size_query_param = 'page_size'
    books = Book.objects.all()
    result_page = paginator.paginate_queryset(books, request)
    serializer = BookSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# GET /books/{id}
@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewBooks])
def get_book(request, id):
    try:
        book = Book.objects.get(id=id)
    except Book.DoesNotExist:
        return Response({'error': 'Livre non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    serializer = BookSerializer(book)
    return Response(serializer.data)

# POST /books
@api_view(['POST'])
@permission_classes([IsAuthenticated, CanAddBook])
def create_book(request):
    serializer = BookSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# PUT /books/{id}
@api_view(['PUT'])
@permission_classes([IsAuthenticated, CanEditBook])
def update_book(request, id):
    try:
        book = Book.objects.get(id=id)
    except Book.DoesNotExist:
        return Response({'error': 'Livre non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    serializer = BookSerializer(book, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated, CanEditBook])
def partial_update_book(request, id):
    """
    Partially update a book.
    
    Required permission: can_edit_book
    Accessible by: Librarians and Admins
    """
    try:
        book = Book.objects.get(id=id)
    except Book.DoesNotExist:
        return Response({'error': 'Livre non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = BookSerializer(book, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DELETE /books/{id}
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, CanDeleteBook])
def delete_book(request, id):
    try:
        book = Book.objects.get(id=id)
    except Book.DoesNotExist:
        return Response({'error': 'Livre non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    book.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewBooks])
def search_books(request):
    """
    Recherche simple de livres par titre, auteur ou ISBN
    """
    query = request.GET.get('q', '').strip()
    if not query:
        return Response({'error': 'Le paramètre de recherche "q" est requis'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Validate optional min_rating
    min_rating = request.GET.get('min_rating')
    if min_rating is not None:
        try:
            min_rating_val = float(min_rating)
        except (TypeError, ValueError):
            return Response({'error': 'min_rating must be a number'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        min_rating_val = None

    # Basic search in title, author and ISBN
    qs = Book.objects.filter(
        Q(title__icontains=query) |
        Q(author__icontains=query) |
        Q(isbn__icontains=query)
    )

    if min_rating_val is not None:
        qs = qs.filter(average_rating__gte=min_rating_val)

    qs = qs.order_by('title')

    serializer = BookSerializer(qs, many=True)

    # sanitize query to avoid reflecting raw HTML
    safe_query = html.escape(query)

    return Response({
        'query': safe_query,
        'count': qs.count(),
        'results': serializer.data
    })


# --- Additional endpoints used by tests ---


@api_view(['POST'])
@permission_classes([IsAuthenticated, CanBorrowBook])
def borrow_book(request, id):
    try:
        book = Book.objects.get(id=id)
    except Book.DoesNotExist:
        return Response({'error': 'Livre non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    if not book.decrement_copies():
        return Response({'error': 'Aucun exemplaire disponible'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = BookSerializer(book)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, CanBorrowBook])
def return_book(request, id):
    try:
        book = Book.objects.get(id=id)
    except Book.DoesNotExist:
        return Response({'error': 'Livre non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    if not book.return_copy():
        return Response({'error': "Impossible de retourner: capacité atteinte"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = BookSerializer(book)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, id):
    # ensure book exists
    try:
        Book.objects.get(id=id)
    except Book.DoesNotExist:
        return Response({'error': 'Livre non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    data = dict(request.data)
    data['book_id'] = id
    serializer = BookReviewSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewBooks])
def list_reviews(request, id):
    try:
        Book.objects.get(id=id)
    except Book.DoesNotExist:
        return Response({'error': 'Livre non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    paginator = PageNumberPagination()
    paginator.page_size_query_param = 'page_size'
    reviews = BookReview.objects.filter(book_id=id).order_by('-created_at')
    result_page = paginator.paginate_queryset(reviews, request)
    serializer = BookReviewSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)
