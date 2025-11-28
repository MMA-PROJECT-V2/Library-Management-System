from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Book(models.Model):
    CATEGORY_CHOICES = [
        ('FICTION', 'Fiction'),
        ('NON_FICTION', 'Non-Fiction'),
        ('SCIENCE', 'Science'),
        ('TECHNOLOGY', 'Technologie'),
        ('HISTORY', 'Histoire'),
        ('BIOGRAPHY', 'Biographie'),
        ('CHILDREN', 'Enfants'),
        ('EDUCATION', 'Éducation'),
        ('POETRY', 'Poésie'),
        ('OTHER', 'Autre'),
    ]
    
    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    publication_year = models.IntegerField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    cover_image_url = models.URLField(blank=True)
    language = models.CharField(max_length=50, default='Français')
    pages = models.IntegerField(validators=[MinValueValidator(1)])
    total_copies = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    available_copies = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    times_borrowed = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'books'
        ordering = ['-created_at', '-id']
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.title} par {self.author}"
    
    def check_availability(self):
        return self.available_copies > 0
    
    def increment_copies(self, quantity=1):
        self.available_copies += quantity
        self.total_copies += quantity
        self.is_available = self.available_copies > 0
        self.save()
    
    def decrement_copies(self):
        if self.available_copies > 0:
            self.available_copies -= 1
            self.is_available = self.available_copies > 0
            self.times_borrowed += 1
            self.save()
            return True
        return False
    
    def return_copy(self):
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            self.is_available = True
            self.save()
            return True
        return False
    
    def get_availability_status(self):
        if self.available_copies == 0:
            return "Non disponible"
        elif self.available_copies < 3:
            return f"Peu disponible ({self.available_copies} copie(s))"
        else:
            return f"Disponible ({self.available_copies} copie(s))"


class BookReview(models.Model):
    book_id = models.IntegerField()
    user_id = models.IntegerField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'book_reviews'
        unique_together = ['book_id', 'user_id']
    
    def __str__(self):
        return f"Avis {self.rating}/5 sur livre {self.book_id}"
