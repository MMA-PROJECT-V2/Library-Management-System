import api, { LOANS_SERVICE_URL } from './api';
import { rabbitMQService } from './rabbitmq.service';
import type {
  Loan,
  CreateLoanRequest,
  CreateLoanResponse,
  ReturnLoanResponse,
  RenewLoanResponse,
  UserLoansResponse,
  ActiveLoansResponse,
  OverdueLoansResponse,
  LoanHistoryResponse
} from '@/types/loan.types';

export const loansService = {
  createLoan: (data: CreateLoanRequest) => {
    rabbitMQService.sendToExchange('loan.create_request', data);
    return Promise.resolve({ message: 'Loan creation queued' });
  },

  returnLoan: (id: number, userId: number) => {
    rabbitMQService.sendToExchange('loan.return_request', { loan_id: id, user_id: userId });
    return Promise.resolve({ message: 'Return queued' });
  },

  renewLoan: (id: number, userId: number) => {
    rabbitMQService.sendToExchange('loan.renew_request', { loan_id: id, user_id: userId });
    return Promise.resolve({ message: 'Renewal queued' });
  },

  getUserLoans: (userId: number) =>
    api.get<UserLoansResponse>(`${LOANS_SERVICE_URL}/user/${userId}/`),

  getUserActiveLoans: (userId: number) =>
    api.get<ActiveLoansResponse>(`${LOANS_SERVICE_URL}/user/${userId}/active/`),

  getAllLoans: () =>
    api.get<{ count: number; loans: Loan[] }>(`${LOANS_SERVICE_URL}/list/`),

  getActiveLoans: () =>
    api.get<ActiveLoansResponse>(`${LOANS_SERVICE_URL}/active/`),

  getOverdueLoans: () =>
    api.get<OverdueLoansResponse>(`${LOANS_SERVICE_URL}/overdue/`),

  getLoan: (id: number) =>
    api.get<Loan>(`${LOANS_SERVICE_URL}/${id}/`),

  getLoanHistory: (id: number) =>
    api.get<LoanHistoryResponse>(`${LOANS_SERVICE_URL}/${id}/history/`),

  healthCheck: () =>
    api.get<{ status: string; service: string; timestamp: string }>(`${LOANS_SERVICE_URL}/health/`),
};
