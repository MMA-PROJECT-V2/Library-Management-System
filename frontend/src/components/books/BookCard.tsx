import { BookOpen } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { StarRating } from '@/components/common/StarRating';
import type { Book } from '@/types/book.types';
import { cn } from '@/lib/utils';

interface BookCardProps {
  book: Book;
  onClick?: () => void;
}

export const BookCard = ({ book, onClick }: BookCardProps) => {
  const rating = parseFloat(book.average_rating) || 0;
  
  return (
    <Card 
      className={cn(
        "group overflow-hidden transition-all duration-300 hover:shadow-lg hover:-translate-y-1 cursor-pointer border-border/50",
        !book.is_available && "opacity-75"
      )}
      onClick={onClick}
    >
      <div className="relative aspect-[3/4] overflow-hidden bg-muted">
        {book.cover_image_url ? (
          <img
            src={book.cover_image_url}
            alt={book.title}
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-primary/20 to-primary/5">
            <BookOpen className="h-16 w-16 text-primary/30" />
          </div>
        )}
        
        {/* Availability Badge */}
        <div className="absolute right-2 top-2">
          <Badge 
            variant={book.is_available ? "default" : "secondary"}
            className={cn(
              "text-xs",
              book.is_available 
                ? "bg-success text-success-foreground" 
                : "bg-muted text-muted-foreground"
            )}
          >
            {book.is_available ? `${book.available_copies} available` : 'Unavailable'}
          </Badge>
        </div>

        {/* Category Badge */}
        <div className="absolute left-2 top-2">
          <Badge variant="secondary" className="text-xs bg-card/90 backdrop-blur-sm">
            {book.category.replace('_', ' ')}
          </Badge>
        </div>
      </div>

      <CardContent className="p-4">
        <h3 className="font-display font-semibold text-foreground line-clamp-2 mb-1 group-hover:text-primary transition-colors">
          {book.title}
        </h3>
        <p className="text-sm text-muted-foreground mb-3 line-clamp-1">
          {book.author}
        </p>
        
        <div className="flex items-center justify-between">
          <StarRating rating={rating} size="sm" showValue />
          <span className="text-xs text-muted-foreground">
            {book.times_borrowed} borrows
          </span>
        </div>
      </CardContent>
    </Card>
  );
};
