import { useState } from 'react';
import { BookOpen, Clock, RotateCcw, Check, AlertTriangle, History, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { StatusBadge } from '@/components/common/StatusBadge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useToast } from '@/hooks/use-toast';
import { useUserLoans, useUserActiveLoans, useReturnLoan, useRenewLoan, useLoanHistory } from '@/hooks/useLoans';
import type { Loan, LoanHistory as LoanHistoryType } from '@/types/loan.types';

const MyLoans = () => {
  const [selectedLoanId, setSelectedLoanId] = useState<number | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [confirmReturn, setConfirmReturn] = useState<Loan | null>(null);
  const { toast } = useToast();

  const { data: allLoansData, isLoading: isLoadingAll } = useUserLoans();
  const { data: activeLoansData, isLoading: isLoadingActive } = useUserActiveLoans();
  const { data: historyData } = useLoanHistory(selectedLoanId || 0);

  const returnMutation = useReturnLoan();
  const renewMutation = useRenewLoan();

  const isLoading = isLoadingAll || isLoadingActive;

  const allLoans: Loan[] = allLoansData?.loans || [];
  const activeLoans: Loan[] = activeLoansData?.active_loans || [];
  const overdueLoans = activeLoans.filter(l => l.is_overdue);
  const historyLog: LoanHistoryType[] = historyData?.history || [];

  const handleRenew = (loan: Loan) => {
    renewMutation.mutate(loan.id, {
      onSuccess: () => {
        toast({
          title: 'Renewal request sent',
          description: 'Your renewal request is being processed.',
        });
      },
      onError: (error: any) => {
        toast({
          title: 'Renewal failed',
          description: 'Failed to send renewal request',
          variant: 'destructive',
        });
      },
    });
  };

  const handleReturn = () => {
    if (!confirmReturn) return;
    returnMutation.mutate(confirmReturn.id, {
      onSuccess: () => {
        toast({
          title: 'Return request sent',
          description: 'Your return request is being processed.',
        });
        setConfirmReturn(null);
      },
      onError: (error: any) => {
        toast({
          title: 'Return failed',
          description: error.response?.data?.error || 'Failed to return book',
          variant: 'destructive',
        });
      },
    });
  };

  const LoanCard = ({ loan }: { loan: Loan }) => (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-xl border border-border/50 bg-card p-4 transition-all hover:shadow-md">
      <div className="flex items-start gap-4">
        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-lg bg-primary/10">
          <BookOpen className="h-7 w-7 text-primary" />
        </div>
        <div className="min-w-0">
          <h4 className="font-medium text-foreground truncate">Book #{loan.book_id}</h4>
          <p className="text-sm text-muted-foreground">Loan ID: {loan.id}</p>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <StatusBadge status={loan.status} />
            {loan.renewal_count > 0 && (
              <Badge variant="outline" className="text-xs">
                Renewed {loan.renewal_count}/{loan.max_renewals}
              </Badge>
            )}
          </div>
        </div>
      </div>

      <div className="flex flex-col sm:items-end gap-3">
        <div className="flex items-center gap-2 text-sm">
          <Clock className="h-4 w-4 text-muted-foreground" />
          <span className="text-muted-foreground">Due:</span>
          <span className={`font-medium ${loan.is_overdue ? 'text-destructive' : 'text-foreground'}`}>
            {new Date(loan.due_date).toLocaleDateString()}
          </span>
        </div>

        {loan.is_overdue && (
          <div className="flex items-center gap-1 text-sm text-destructive">
            <AlertTriangle className="h-4 w-4" />
            <span>Fine: {loan.fine_amount} DZD</span>
          </div>
        )}

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedLoanId(loan.id);
              setShowHistory(true);
            }}
          >
            <History className="mr-1 h-4 w-4" />
            History
          </Button>

          {loan.status !== 'RETURNED' && (
            <>
              <Button
                variant="outline"
                size="sm"
                disabled={!loan.can_renew || renewMutation.isPending}
                onClick={() => handleRenew(loan)}
              >
                {renewMutation.isPending ? (
                  <Loader2 className="mr-1 h-4 w-4 animate-spin" />
                ) : (
                  <RotateCcw className="mr-1 h-4 w-4" />
                )}
                Renew
              </Button>
              <Button
                size="sm"
                onClick={() => setConfirmReturn(loan)}
              >
                <Check className="mr-1 h-4 w-4" />
                Return
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="font-display text-3xl font-bold text-foreground">My Loans</h1>
        <p className="mt-1 text-muted-foreground">
          Manage your borrowed books and track due dates
        </p>
      </div>

      <Tabs defaultValue="active" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 lg:w-auto lg:inline-grid">
          <TabsTrigger value="active" className="gap-2">
            Active
            {activeLoans.length > 0 && (
              <Badge variant="secondary" className="ml-1">
                {activeLoans.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
          <TabsTrigger value="overdue" className="gap-2">
            Overdue
            {overdueLoans.length > 0 && (
              <Badge variant="destructive" className="ml-1">
                {overdueLoans.length}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="space-y-4">
          {activeLoans.length > 0 ? (
            activeLoans.map((loan) => <LoanCard key={loan.id} loan={loan} />)
          ) : (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                <BookOpen className="h-12 w-12 text-muted-foreground/50 mb-4" />
                <h3 className="font-medium text-foreground">No active loans</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Browse our collection to find your next read
                </p>
                <Button asChild>
                  <a href="/books">Browse Books</a>
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          {allLoans.length > 0 ? (
            allLoans.map((loan) => <LoanCard key={loan.id} loan={loan} />)
          ) : (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                <History className="h-12 w-12 text-muted-foreground/50 mb-4" />
                <h3 className="font-medium text-foreground">No loan history</h3>
                <p className="text-sm text-muted-foreground">
                  Your borrowing history will appear here
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="overdue" className="space-y-4">
          {overdueLoans.length > 0 ? (
            <>
              <Card className="border-destructive/30 bg-destructive/5">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-destructive">
                    <AlertTriangle className="h-5 w-5" />
                    Overdue Alert
                  </CardTitle>
                  <CardDescription>
                    You have {overdueLoans.length} overdue book(s). Please return them as soon as possible to avoid additional fines.
                  </CardDescription>
                </CardHeader>
              </Card>
              {overdueLoans.map((loan) => <LoanCard key={loan.id} loan={loan} />)}
            </>
          ) : (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                <Check className="h-12 w-12 text-success mb-4" />
                <h3 className="font-medium text-foreground">All clear!</h3>
                <p className="text-sm text-muted-foreground">
                  You have no overdue books
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* History Dialog */}
      <Dialog open={showHistory} onOpenChange={setShowHistory}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Loan History</DialogTitle>
            <DialogDescription>
              Loan #{selectedLoanId}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {historyLog.length > 0 ? (
              historyLog.map((entry) => (
                <div key={entry.id} className="flex gap-4 items-start">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                    {entry.action === 'CREATED' && <BookOpen className="h-4 w-4 text-primary" />}
                    {entry.action === 'RENEWED' && <RotateCcw className="h-4 w-4 text-info" />}
                    {entry.action === 'RETURNED' && <Check className="h-4 w-4 text-success" />}
                    {!['CREATED', 'RENEWED', 'RETURNED'].includes(entry.action) && <Clock className="h-4 w-4 text-muted-foreground" />}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{entry.action_display}</p>
                    <p className="text-sm text-muted-foreground">{entry.details}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(entry.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-center text-muted-foreground py-4">No history available</p>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Return Confirmation Dialog */}
      <AlertDialog open={!!confirmReturn} onOpenChange={(open) => !open && setConfirmReturn(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Return Book</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to return this book?
              {confirmReturn?.is_overdue && (
                <span className="block mt-2 text-destructive font-medium">
                  Note: A fine of {confirmReturn.fine_amount} DZD will be applied for the late return.
                </span>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={returnMutation.isPending}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleReturn} disabled={returnMutation.isPending}>
              {returnMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                'Confirm Return'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default MyLoans;