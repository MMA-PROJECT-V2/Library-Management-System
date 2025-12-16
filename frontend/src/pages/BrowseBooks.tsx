import { useState, useEffect } from 'react';
import { Search, Filter, X, BookOpen, Loader2, Star } from 'lucide-react';
import { BookCard } from '@/components/books/BookCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { BOOK_CATEGORIES, type Book } from '@/types/book.types';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { StarRating } from '@/components/common/StarRating';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { useBooks, useCreateBook, useCreateReview, useBookReviews } from '@/hooks/useBooks';
import { useCreateLoan } from '@/hooks/useLoans';
import { cn } from '@/lib/utils';

const BrowseBooks = () => {
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [category, setCategory] = useState<string>('');
  const [minRating, setMinRating] = useState([0]);
  const [yearFrom, setYearFrom] = useState('');
  const [yearTo, setYearTo] = useState('');
  const [showAvailableOnly, setShowAvailableOnly] = useState(false);

  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);

  // Rating State
  const [userRating, setUserRating] = useState(0);
  const [reviewComment, setReviewComment] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  const { toast } = useToast();
  const { user } = useAuth();

  const { data, isLoading, error } = useBooks({ page, page_size: 100 });

  // Fetch reviews for selected book
  const { data: reviews, isLoading: reviewsLoading } = useBookReviews(selectedBook?.id || 0, { page_size: 50 });

  const borrowMutation = useCreateLoan();
  const createReviewMutation = useCreateReview();

  // Check if current user has a review
  const existingReview = reviews?.results?.find((r: any) => r.user_id === user?.id);

  // Sync state when existing review is found
  useEffect(() => {
    if (existingReview) {
      setUserRating(existingReview.rating);
      setReviewComment(existingReview.comment || '');
      setIsEditing(false); // Hide form by default if review exists
    } else {
      // Reset if switching to a book with no review
      setUserRating(0);
      setReviewComment('');
      setIsEditing(true); // Show form if no review
    }
  }, [existingReview, selectedBook]);

  const books: Book[] = data?.results || [];
  const totalCount = data?.count || 0;

  // Filter books locally
  const filteredBooks = books.filter((book) => {
    const matchesSearch = !searchQuery ||
      book.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      book.author.toLowerCase().includes(searchQuery.toLowerCase()) ||
      book.isbn.includes(searchQuery);

    const matchesCategory = !category || category === 'ALL' || book.category === category;
    const matchesAvailability = !showAvailableOnly || book.is_available;

    // New filters from SearchBooks
    const bookRating = parseFloat(book.average_rating) || 0;
    const matchesRating = bookRating >= minRating[0];

    const matchesYearFrom = !yearFrom || book.publication_year >= parseInt(yearFrom);
    const matchesYearTo = !yearTo || book.publication_year <= parseInt(yearTo);

    return matchesSearch && matchesCategory && matchesAvailability && matchesRating && matchesYearFrom && matchesYearTo;
  });

  const clearFilters = () => {
    setSearchQuery('');
    setCategory('ALL');
    setShowAvailableOnly(false);
    setMinRating([0]);
    setYearFrom('');
    setYearTo('');
  };

  const hasActiveFilters = searchQuery || (category && category !== 'ALL') || showAvailableOnly || minRating[0] > 0 || yearFrom || yearTo;

  const handleBookClick = (book: Book) => {
    setSelectedBook(book);
  };

  const handleBorrow = (book: Book) => {
    if (!user) {
      toast({
        title: 'Please log in',
        description: 'You need to be logged in to borrow books',
        variant: 'destructive',
      });
      return;
    }
    borrowMutation.mutate(
      { user_id: user.id, book_id: book.id },
      {
        onSuccess: (response) => {
          toast({
            title: 'Book borrowed successfully!',
            description: `Due date: ${response.due_date}`,
          });
          // Don't close modal immediately so they see success, or close it?
          // Keeping it open allows them to rate it or see details.
        },
        onError: (error: any) => {
          const message = error.response?.data?.error || 'Failed to borrow book';
          toast({
            title: 'Borrow failed',
            description: message,
            variant: 'destructive',
          });
        },
      }
    );
  };

  const handleSubmitReview = (bookId: number) => {
    if (!user) {
      toast({
        title: 'Please log in',
        description: 'You need to be logged in to rate books',
        variant: 'destructive',
      });
      return;
    }
    if (userRating === 0) {
      toast({
        title: 'Rating required',
        description: 'Please select a star rating',
        variant: 'destructive',
      });
      return;
    }

    createReviewMutation.mutate(
      {
        id: bookId,
        data: {
          user_id: user.id,
          rating: userRating,
          comment: reviewComment
        }
      },
      {
        onSuccess: () => {
          toast({
            title: 'Review submitted',
            description: 'Thank you for your feedback!',
          });
          setUserRating(0);
          setReviewComment('');
        },
        onError: (error: any) => {
          const message = error.response?.data?.error || 'Failed to submit review';
          toast({
            title: 'Review failed',
            description: message,
            variant: 'destructive',
          });
        }
      }
    );
  };

  const FiltersContent = () => (
    <div className="space-y-6">
      <div className="space-y-2">
        <Label>Search Query</Label>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Title, author, or ISBN..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label>Category</Label>
        <Select value={category} onValueChange={setCategory}>
          <SelectTrigger>
            <SelectValue placeholder="All categories" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All categories</SelectItem>
            {BOOK_CATEGORIES.map((cat) => (
              <SelectItem key={cat.value} value={cat.value}>
                {cat.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label>Minimum Rating: {minRating[0]}</Label>
        <Slider
          value={minRating}
          onValueChange={setMinRating}
          max={5}
          step={0.1}
          className="mt-2"
        />
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-2">
          <Label htmlFor="yearFrom">Year From</Label>
          <Input
            id="yearFrom"
            type="number"
            placeholder="1900"
            value={yearFrom}
            onChange={(e) => setYearFrom(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="yearTo">Year To</Label>
          <Input
            id="yearTo"
            type="number"
            placeholder="2025"
            value={yearTo}
            onChange={(e) => setYearTo(e.target.value)}
          />
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <Checkbox
          id="available"
          checked={showAvailableOnly}
          onCheckedChange={(checked) => setShowAvailableOnly(checked as boolean)}
        />
        <Label htmlFor="available" className="cursor-pointer">
          Show available only
        </Label>
      </div>

      <div className="pt-2">
        <Button
          className="w-full mb-2 bg-primary text-primary-foreground hover:bg-primary/90"
        >
          Start Your Search
        </Button>

        {hasActiveFilters && (
          <Button variant="outline" className="w-full" onClick={clearFilters}>
            <X className="mr-2 h-4 w-4" />
            Clear filters
          </Button>
        )}
      </div>
    </div>
  );

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-foreground">Search Books</h1>
          <p className="mt-1 text-muted-foreground">
            Find books by title, author, ISBN, or use advanced filters
          </p>
        </div>

        {/* Mobile Filter Button */}
        <Sheet open={isFiltersOpen} onOpenChange={setIsFiltersOpen}>
          <SheetTrigger asChild>
            <Button variant="outline" className="md:hidden">
              <Filter className="mr-2 h-4 w-4" />
              Advanced Search
              {hasActiveFilters && (
                <Badge variant="secondary" className="ml-2">
                  Active
                </Badge>
              )}
            </Button>
          </SheetTrigger>
          <SheetContent side="right">
            <SheetHeader>
              <SheetTitle>Advanced Search</SheetTitle>
              <SheetDescription>
                Use filters to narrow down your search
              </SheetDescription>
            </SheetHeader>
            <div className="mt-6">
              <FiltersContent />
            </div>
          </SheetContent>
        </Sheet>
      </div>

      <div className="flex gap-8">
        {/* Desktop Filters Sidebar */}
        <aside className="hidden w-72 shrink-0 md:block">
          <div className="sticky top-24 rounded-xl border border-border/50 bg-card p-6 shadow-sm">
            <h3 className="mb-4 font-display font-semibold text-foreground flex items-center gap-2">
              <Filter className="h-4 w-4" />
              Advanced Search
            </h3>
            <p className="text-xs text-muted-foreground mb-4">Use filters to narrow down your search</p>
            <FiltersContent />
          </div>
        </aside>

        {/* Books Grid */}
        <div className="flex-1">
          {isLoading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <BookOpen className="h-16 w-16 text-muted-foreground/30 mb-4" />
              <h3 className="font-display text-xl font-semibold text-foreground mb-2">
                Failed to load books
              </h3>
              <p className="text-muted-foreground mb-4">
                Please check your connection and try again
              </p>
            </div>
          ) : filteredBooks.length > 0 ? (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {filteredBooks.map((book, index) => (
                <div
                  key={book.id}
                  className="animate-slide-up"
                  style={{ animationDelay: `${0.03 * index}s` }}
                >
                  <BookCard book={book} onClick={() => handleBookClick(book)} />
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <BookOpen className="h-16 w-16 text-muted-foreground/30 mb-4" />
              <h3 className="font-display text-xl font-semibold text-foreground mb-2">
                No books found
              </h3>
              <p className="text-muted-foreground mb-4">
                Try adjusting your filters or search query
              </p>
              <Button variant="outline" onClick={clearFilters}>
                Clear filters
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Book Details and Rating Dialog */}
      <Dialog open={!!selectedBook} onOpenChange={(open) => !open && setSelectedBook(null)}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          {selectedBook && (
            <>
              <DialogHeader>
                <DialogTitle className="font-display text-2xl">{selectedBook.title}</DialogTitle>
                <DialogDescription>by {selectedBook.author}</DialogDescription>
              </DialogHeader>

              <div className="grid gap-6 md:grid-cols-[200px_1fr]">
                {/* Cover and Borrow Button */}
                <div className="space-y-4">
                  <div className="aspect-[3/4] rounded-lg bg-muted overflow-hidden">
                    {selectedBook.cover_image_url ? (
                      <img
                        src={selectedBook.cover_image_url}
                        alt={selectedBook.title}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center bg-gradient-to-br from-primary/20 to-primary/5">
                        <BookOpen className="h-16 w-16 text-primary/30" />
                      </div>
                    )}
                  </div>

                  <Button
                    className="w-full"
                    disabled={!selectedBook.is_available || borrowMutation.isPending}
                    onClick={() => handleBorrow(selectedBook)}
                  >
                    {borrowMutation.isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Borrowing...
                      </>
                    ) : selectedBook.is_available ? (
                      'Borrow This Book'
                    ) : (
                      'Currently Unavailable'
                    )}
                  </Button>
                </div>

                {/* Details */}
                <div className="space-y-6">
                  {/* Metadata */}
                  <div className="space-y-4">
                    <div className="flex flex-wrap gap-2">
                      <Badge>{selectedBook.category.replace('_', ' ')}</Badge>
                      <Badge variant={selectedBook.is_available ? "default" : "secondary"}>
                        {selectedBook.is_available
                          ? `${selectedBook.available_copies} available`
                          : 'Unavailable'
                        }
                      </Badge>
                    </div>

                    <div className="flex items-center gap-2">
                      <StarRating rating={parseFloat(selectedBook.average_rating)} showValue />
                      <span className="text-sm text-muted-foreground">
                        ({selectedBook.times_borrowed} borrows)
                      </span>
                    </div>

                    <p className="text-muted-foreground">{selectedBook.description}</p>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Publisher:</span>
                        <p className="font-medium">{selectedBook.publisher}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Year:</span>
                        <p className="font-medium">{selectedBook.publication_year}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Pages:</span>
                        <p className="font-medium">{selectedBook.pages}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">ISBN:</span>
                        <p className="font-medium">{selectedBook.isbn}</p>
                      </div>
                    </div>
                  </div>

                  {/* Reviews Section */}
                  <div className="border-t pt-4">
                    <h4 className="font-semibold mb-4">Reviews</h4>

                    {/* Review List */}
                    <div className="space-y-4 mb-6 max-h-60 overflow-y-auto pr-2">
                      {reviewsLoading ? (
                        <div className="flex justify-center p-4">
                          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                        </div>
                      ) : reviews?.results?.length > 0 ? (
                        reviews.results.map((review: any) => (
                          <div key={review.id} className="bg-muted/50 p-3 rounded-lg space-y-2">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <StarRating rating={review.rating} showValue />
                                <span className="text-xs text-muted-foreground">
                                  by User #{review.user_id}
                                </span>
                              </div>
                              <span className="text-xs text-muted-foreground">
                                {new Date(review.created_at).toLocaleDateString()}
                              </span>
                            </div>
                            {review.comment && (
                              <p className="text-sm text-foreground/90">{review.comment}</p>
                            )}
                          </div>
                        ))
                      ) : (
                        <p className="text-sm text-muted-foreground text-center py-4">
                          No reviews yet. Be the first to rate this book!
                        </p>
                      )}
                    </div>

                    {/* Rating Form */}
                    <div className="border-t pt-4">
                      {existingReview && !isEditing ? (
                        <div className="bg-muted/30 p-4 rounded-lg text-center space-y-3">
                          <p className="text-sm text-muted-foreground">
                            You have already reviewed this book.
                          </p>
                          <Button
                            variant="outline"
                            onClick={() => setIsEditing(true)}
                            className="w-full"
                          >
                            Edit Your Review
                          </Button>
                        </div>
                      ) : (
                        <>
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold">
                              {existingReview ? 'Update Your Review' : 'Rate this Book'}
                            </h4>
                            {existingReview && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setIsEditing(false)}
                                className="h-auto p-0 text-muted-foreground hover:text-foreground"
                              >
                                Cancel
                              </Button>
                            )}
                          </div>
                          <div className="space-y-3">
                            <div className="flex items-center gap-1">
                              {[1, 2, 3, 4, 5].map((star) => (
                                <button
                                  key={star}
                                  type="button"
                                  onClick={() => setUserRating(star)}
                                  className="focus:outline-none transition-transform hover:scale-110"
                                >
                                  <Star
                                    className={cn(
                                      "h-6 w-6 transition-colors",
                                      star <= userRating
                                        ? "fill-yellow-400 text-yellow-400"
                                        : "text-muted-foreground"
                                    )}
                                  />
                                </button>
                              ))}
                              <span className="ml-2 text-sm text-muted-foreground">
                                {userRating > 0 ? `${userRating} Stars` : 'Select a rating'}
                              </span>
                            </div>
                            <Textarea
                              placeholder="Write your review here (optional)..."
                              value={reviewComment}
                              onChange={(e) => setReviewComment(e.target.value)}
                              className="resize-none"
                            />
                            <Button
                              onClick={() => handleSubmitReview(selectedBook.id)}
                              disabled={createReviewMutation.isPending}
                              variant="secondary"
                              className="w-full"
                            >
                              {createReviewMutation.isPending ? (
                                <>
                                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                  Submitting...
                                </>
                              ) : existingReview ? (
                                'Update Review'
                              ) : (
                                'Submit Review'
                              )}
                            </Button>
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default BrowseBooks;