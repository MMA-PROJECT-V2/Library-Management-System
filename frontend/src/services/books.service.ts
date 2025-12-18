import api, { BOOKS_SERVICE_URL } from './api';
import { rabbitMQService } from './rabbitmq.service';
import type { Book, BooksResponse, SearchBooksResponse, CreateBookRequest, BookReview, CreateReviewRequest } from '@/types/book.types';

interface BooksParams {
  page?: number;
  page_size?: number;
}

interface SearchParams {
  q: string;
  min_rating?: number;
}

interface ReviewsParams {
  page?: number;
  page_size?: number;
}

interface ReviewsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: BookReview[];
}

export const booksService = {
  getBooks: (params?: BooksParams) =>
    api.get<BooksResponse>(`${BOOKS_SERVICE_URL}/books/`, { params }),

  getBook: (id: number) =>
    api.get<Book>(`${BOOKS_SERVICE_URL}/books/${id}/`),

  createBook: (data: CreateBookRequest) => {
    rabbitMQService.sendToExchange('book.create_request', data);
    return Promise.resolve({ message: 'Creation queued' });
  },

  updateBook: (id: number, data: CreateBookRequest) => {
    rabbitMQService.sendToExchange('book.update_request', { book_id: id, data });
    return Promise.resolve({ message: 'Update queued' });
  },

  partialUpdateBook: (id: number, data: Partial<CreateBookRequest>) => {
    rabbitMQService.sendToExchange('book.update_request', { book_id: id, data });
    return Promise.resolve({ message: 'Update queued' });
  },

  deleteBook: (id: number) => {
    rabbitMQService.sendToExchange('book.delete_request', { book_id: id });
    return Promise.resolve({ message: 'Deletion queued' });
  },

  searchBooks: (params: SearchParams) =>
    api.get<SearchBooksResponse>(`${BOOKS_SERVICE_URL}/search/`, { params }),

  getReviews: (id: number, params?: ReviewsParams) =>
    api.get<ReviewsResponse>(`${BOOKS_SERVICE_URL}/books/${id}/reviews/`, { params }),

  createReview: (id: number, data: CreateReviewRequest) =>
    api.post<BookReview>(`${BOOKS_SERVICE_URL}/books/${id}/reviews/create/`, data),
};
