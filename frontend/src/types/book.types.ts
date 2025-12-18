export type BookCategory = 
  | 'FICTION' 
  | 'NON_FICTION' 
  | 'SCIENCE' 
  | 'TECHNOLOGY' 
  | 'HISTORY' 
  | 'BIOGRAPHY' 
  | 'CHILDREN' 
  | 'EDUCATION' 
  | 'POETRY' 
  | 'OTHER';

export const BOOK_CATEGORIES: { value: BookCategory; label: string }[] = [
  { value: 'FICTION', label: 'Fiction' },
  { value: 'NON_FICTION', label: 'Non-Fiction' },
  { value: 'SCIENCE', label: 'Science' },
  { value: 'TECHNOLOGY', label: 'Technology' },
  { value: 'HISTORY', label: 'History' },
  { value: 'BIOGRAPHY', label: 'Biography' },
  { value: 'CHILDREN', label: 'Children' },
  { value: 'EDUCATION', label: 'Education' },
  { value: 'POETRY', label: 'Poetry' },
  { value: 'OTHER', label: 'Other' },
];

export interface Book {
  id: number;
  isbn: string;
  title: string;
  author: string;
  publisher: string;
  publication_year: number;
  category: BookCategory;
  description: string;
  cover_image_url: string;
  language: string;
  pages: number;
  total_copies: number;
  available_copies: number;
  times_borrowed: number;
  average_rating: string;
  is_available: boolean;
  created_at: string;
  updated_at: string;
}

export interface BookReview {
  id: number;
  book_id: number;
  user_id: number;
  rating: number;
  comment: string;
  created_at: string;
}

export interface CreateBookRequest {
  isbn: string;
  title: string;
  author: string;
  publisher: string;
  publication_year: number;
  category: BookCategory;
  description?: string;
  cover_image_url?: string;
  language?: string;
  pages: number;
  total_copies: number;
  available_copies: number;
}

export interface BooksResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Book[];
}

export interface SearchBooksResponse {
  query: string;
  count: number;
  results: Book[];
}

export interface CreateReviewRequest {
  user_id: number;
  rating: number;
  comment: string;
}
