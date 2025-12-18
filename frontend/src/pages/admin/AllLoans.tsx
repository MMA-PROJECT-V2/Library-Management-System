import { useState } from 'react';
import { Search, Filter, History, RotateCcw, BookCheck } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { useAllLoans, useLoanHistory, useReturnLoan } from '@/hooks/useLoans';
import { StatusBadge } from '@/components/common/StatusBadge';
import { format } from 'date-fns';
import type { Loan, LoanStatus } from '@/types/loan.types';

const AllLoans = () => {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedLoanId, setSelectedLoanId] = useState<number | null>(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  const { data: loansData, isLoading } = useAllLoans();
  const { data: historyData, isLoading: historyLoading } = useLoanHistory(selectedLoanId || 0);
  const returnLoan = useReturnLoan();

  const loans = loansData?.loans || [];
  
  const filteredLoans = loans.filter(loan => {
    const matchesSearch = 
      loan.book_id.toString().includes(searchQuery) ||
      loan.user_id.toString().includes(searchQuery);
    const matchesStatus = statusFilter === 'all' || loan.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleViewHistory = (loanId: number) => {
    setSelectedLoanId(loanId);
    setIsHistoryOpen(true);
  };

  const handleReturn = async (loanId: number) => {
    try {
      const result = await returnLoan.mutateAsync(loanId);
      toast({
        title: "Book Returned",
        description: result.fine?.amount 
          ? `Fine of ${result.fine.amount} DZD applied for ${result.fine.days_overdue} days overdue`
          : "Book returned successfully",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to return book",
        variant: "destructive",
      });
    }
  };

  const getStatusColor = (status: LoanStatus) => {
    switch (status) {
      case 'ACTIVE':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
      case 'RETURNED':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      case 'OVERDUE':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      case 'RENEWED':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
      default:
        return '';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-foreground">All Loans</h1>
        <p className="text-muted-foreground">View and manage all library loans</p>
      </div>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search by user ID or book ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="ACTIVE">Active</SelectItem>
              <SelectItem value="RETURNED">Returned</SelectItem>
              <SelectItem value="OVERDUE">Overdue</SelectItem>
              <SelectItem value="RENEWED">Renewed</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Badge variant="secondary">{filteredLoans.length} loans</Badge>
      </div>

      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Loan ID</TableHead>
              <TableHead>User ID</TableHead>
              <TableHead>Book ID</TableHead>
              <TableHead>Loan Date</TableHead>
              <TableHead>Due Date</TableHead>
              <TableHead>Return Date</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Renewals</TableHead>
              <TableHead>Fine</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={10} className="text-center py-8">
                  Loading loans...
                </TableCell>
              </TableRow>
            ) : filteredLoans.length === 0 ? (
              <TableRow>
                <TableCell colSpan={10} className="text-center py-8">
                  <BookCheck className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-muted-foreground">No loans found</p>
                </TableCell>
              </TableRow>
            ) : (
              filteredLoans.map((loan) => (
                <TableRow key={loan.id} className={loan.is_overdue ? 'bg-destructive/5' : ''}>
                  <TableCell className="font-mono text-sm">#{loan.id}</TableCell>
                  <TableCell>User #{loan.user_id}</TableCell>
                  <TableCell>Book #{loan.book_id}</TableCell>
                  <TableCell>{format(new Date(loan.loan_date), 'MMM dd, yyyy')}</TableCell>
                  <TableCell>
                    <span className={loan.is_overdue ? 'text-destructive font-medium' : ''}>
                      {format(new Date(loan.due_date), 'MMM dd, yyyy')}
                    </span>
                  </TableCell>
                  <TableCell>
                    {loan.return_date 
                      ? format(new Date(loan.return_date), 'MMM dd, yyyy')
                      : '—'
                    }
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={loan.status} />
                  </TableCell>
                  <TableCell className="text-center">
                    {loan.renewal_count}/{loan.max_renewals}
                  </TableCell>
                  <TableCell>
                    {parseFloat(loan.fine_amount) > 0 ? (
                      <span className="text-destructive font-medium">
                        {loan.fine_amount} DZD
                      </span>
                    ) : '—'}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleViewHistory(loan.id)}
                        title="View History"
                      >
                        <History className="h-4 w-4" />
                      </Button>
                      {(loan.status === 'ACTIVE' || loan.status === 'OVERDUE' || loan.status === 'RENEWED') && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleReturn(loan.id)}
                          title="Return Book"
                          disabled={returnLoan.isPending}
                        >
                          <RotateCcw className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Loan History Modal */}
      <Dialog open={isHistoryOpen} onOpenChange={setIsHistoryOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Loan History #{selectedLoanId}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {historyLoading ? (
              <p className="text-center text-muted-foreground py-4">Loading history...</p>
            ) : historyData?.history?.length === 0 ? (
              <p className="text-center text-muted-foreground py-4">No history available</p>
            ) : (
              <div className="space-y-3">
                {historyData?.history?.map((entry) => (
                  <div 
                    key={entry.id} 
                    className="flex items-start gap-3 p-3 rounded-lg border bg-muted/30"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{entry.action_display}</Badge>
                        <span className="text-xs text-muted-foreground">
                          {format(new Date(entry.created_at), 'MMM dd, yyyy HH:mm')}
                        </span>
                      </div>
                      <p className="text-sm mt-1 text-muted-foreground">{entry.details}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AllLoans;
