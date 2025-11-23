from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Book
from django.db.models import Q
from .serializers import BookSerializer

# GET /books
@api_view(['GET'])
def list_books(request):
    paginator = PageNumberPagination()
    books = Book.objects.all()
    result_page = paginator.paginate_queryset(books, request)
    serializer = BookSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# GET /books/{id}
@api_view(['GET'])
def get_book(request, id):
    try:
        book = Book.objects.get(id=id)
    except Book.DoesNotExist:
        return Response({'error': 'Livre non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    serializer = BookSerializer(book)
    return Response(serializer.data)

# POST /books
@api_view(['POST'])
def create_book(request):
    serializer = BookSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# PUT /books/{id}
@api_view(['PUT'])
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

# DELETE /books/{id}
@api_view(['DELETE'])
def delete_book(request, id):
    try:
        book = Book.objects.get(id=id)
    except Book.DoesNotExist:
        return Response({'error': 'Livre non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    book.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def search_books(request):
    """
    Recherche simple de livres par titre, auteur ou ISBN
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return Response({'error': 'Le paramètre de recherche "q" est requis'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Recherche dans titre, auteur et ISBN
    books = Book.objects.filter(
        Q(title__icontains=query) |
        Q(author__icontains=query) |
        Q(isbn__icontains=query)
    ).order_by('title')
    
    serializer = BookSerializer(books, many=True)
    
    return Response({
        'query': query,
        'count': books.count(),
        'results': serializer.data
    }) 