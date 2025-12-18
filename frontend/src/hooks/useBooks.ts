import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { booksService } from '@/services/books.service';
import type { CreateBookRequest } from '@/types/book.types';

interface BooksParams {
  page?: number;
  page_size?: number;
}

interface SearchParams {
  q: string;
  min_rating?: number;
}

export const useBooks = (params?: BooksParams) => {
  return useQuery({
    queryKey: ['books', params],
    queryFn: async () => {
      const response = await booksService.getBooks(params);
      return response.data;
    },
  });
};

export const useBook = (id: number) => {
  return useQuery({
    queryKey: ['book', id],
    queryFn: async () => {
      const response = await booksService.getBook(id);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useSearchBooks = (params: SearchParams) => {
  return useQuery({
    queryKey: ['books', 'search', params],
    queryFn: async () => {
      const response = await booksService.searchBooks(params);
      return response.data;
    },
    enabled: !!params.q,
  });
};

export const useCreateBook = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateBookRequest) => {
      const response = await booksService.createBook(data);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] });
    },
  });
};

export const useUpdateBook = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: CreateBookRequest }) => {
      const response = await booksService.updateBook(id, data);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] });
    },
  });
};

export const useDeleteBook = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await booksService.deleteBook(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] });
    },
  });
};

export const useBookReviews = (bookId: number, params?: { page?: number; page_size?: number }) => {
  return useQuery({
    queryKey: ['book-reviews', bookId, params],
    queryFn: async () => {
      const response = await booksService.getReviews(bookId, params);
      return response.data;
    },
    enabled: !!bookId,
  });
};

export const useCreateReview = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: import('@/types/book.types').CreateReviewRequest }) => {
      const response = await booksService.createReview(id, data);
      return response;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['books'] });
      queryClient.invalidateQueries({ queryKey: ['book', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['book-reviews', variables.id] });
    },
  });
};
