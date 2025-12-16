import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { loansService } from '@/services/loans.service';
import { useAuth } from '@/contexts/AuthContext';
import type { CreateLoanRequest } from '@/types/loan.types';

export const useUserLoans = (userId?: number) => {
  const { user } = useAuth();
  const id = userId || user?.id;

  return useQuery({
    queryKey: ['loans', 'user', id],
    queryFn: async () => {
      const response = await loansService.getUserLoans(id!);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useUserActiveLoans = (userId?: number) => {
  const { user } = useAuth();
  const id = userId || user?.id;

  return useQuery({
    queryKey: ['loans', 'active', id],
    queryFn: async () => {
      const response = await loansService.getUserActiveLoans(id!);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useAllLoans = () => {
  return useQuery({
    queryKey: ['loans', 'all'],
    queryFn: async () => {
      const response = await loansService.getAllLoans();
      return response.data;
    },
  });
};

export const useActiveLoans = () => {
  return useQuery({
    queryKey: ['loans', 'all-active'],
    queryFn: async () => {
      const response = await loansService.getActiveLoans();
      return response.data;
    },
  });
};

export const useOverdueLoans = () => {
  return useQuery({
    queryKey: ['loans', 'overdue'],
    queryFn: async () => {
      const response = await loansService.getOverdueLoans();
      return response.data;
    },
  });
};

export const useLoan = (id: number) => {
  return useQuery({
    queryKey: ['loan', id],
    queryFn: async () => {
      const response = await loansService.getLoan(id);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useLoanHistory = (id: number) => {
  return useQuery({
    queryKey: ['loan-history', id],
    queryFn: async () => {
      const response = await loansService.getLoanHistory(id);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateLoan = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateLoanRequest) => {
      // loansService.createLoan now returns a direct object, not Axios response
      const response = await loansService.createLoan(data);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['loans'] });
      queryClient.invalidateQueries({ queryKey: ['books'] });
    },
  });
};

export const useReturnLoan = () => {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  return useMutation({
    mutationFn: async (id: number) => {
      if (!user?.id) throw new Error("User not valid");
      const response = await loansService.returnLoan(id, user.id);
      return response; // Returns { message: '...' }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['loans'] });
      queryClient.invalidateQueries({ queryKey: ['books'] });
    },
  });
};

export const useRenewLoan = () => {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  return useMutation({
    mutationFn: async (id: number) => {
      if (!user?.id) throw new Error("User not valid");
      const response = await loansService.renewLoan(id, user.id);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['loans'] });
    },
  });
};
