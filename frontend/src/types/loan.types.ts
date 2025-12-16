export type LoanStatus = 'ACTIVE' | 'RETURNED' | 'OVERDUE' | 'RENEWED';

export interface Loan {
  id: number;
  user_id: number;
  book_id: number;
  loan_date: string;
  due_date: string;
  return_date: string | null;
  status: LoanStatus;
  fine_amount: string;
  fine_paid: boolean;
  renewal_count: number;
  max_renewals: number;
  notes: string;
  is_overdue: boolean;
  days_until_due: number;
  can_renew: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoanWithBook extends Loan {
  book_title?: string;
  book_author?: string;
  book_cover?: string;
}

export interface LoanHistory {
  id: number;
  loan_id: number;
  action: 'CREATED' | 'RENEWED' | 'RETURNED' | 'OVERDUE' | 'FINE_CALCULATED' | 'FINE_PAID';
  action_display: string;
  performed_by: number;
  details: string;
  created_at: string;
}

export interface CreateLoanRequest {
  user_id: number;
  book_id: number;
  notes?: string;
}

export interface CreateLoanResponse {
  message: string;
  loan: Loan;
  book_title: string;
  due_date: string;
}

export interface ReturnLoanResponse {
  message: string;
  loan: Loan;
  fine?: {
    amount: number;
    days_overdue: number;
    message: string;
  };
}

export interface RenewLoanResponse {
  message: string;
  loan: Loan;
  new_due_date: string;
  renewals_remaining: number;
}

export interface UserLoansResponse {
  count: number;
  loans: Loan[];
}

export interface ActiveLoansResponse {
  count: number;
  active_loans: Loan[];
}

export interface OverdueLoansResponse {
  count: number;
  overdue_loans: Loan[];
}

export interface LoanHistoryResponse {
  loan_id: number;
  history: LoanHistory[];
}
