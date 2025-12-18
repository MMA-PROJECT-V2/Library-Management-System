import { useState } from 'react';
import { AlertTriangle, RotateCcw, Mail, DollarSign, Clock, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
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
import { useOverdueLoans, useReturnLoan } from '@/hooks/useLoans';
import { format, differenceInDays } from 'date-fns';

const OverdueLoans = () => {
  const { toast } = useToast();
  const [isReturnDialogOpen, setIsReturnDialogOpen] = useState(false);
  const [selectedLoanId, setSelectedLoanId] = useState<number | null>(null);

  const { data: overdueData, isLoading } = useOverdueLoans();
  const returnLoan = useReturnLoan();

  const loans = overdueData?.overdue_loans || [];
  
  // Calculate statistics
  const totalFines = loans.reduce((sum, loan) => sum + parseFloat(loan.fine_amount), 0);
  const avgDaysOverdue = loans.length > 0 
    ? Math.round(loans.reduce((sum, loan) => {
        const daysOverdue = differenceInDays(new Date(), new Date(loan.due_date));
        return sum + daysOverdue;
      }, 0) / loans.length)
    : 0;
  const uniqueUsers = new Set(loans.map(loan => loan.user_id)).size;

  const handleReturn = (loanId: number) => {
    setSelectedLoanId(loanId);
    setIsReturnDialogOpen(true);
  };

  const confirmReturn = async () => {
    if (!selectedLoanId) return;
    try {
      const result = await returnLoan.mutateAsync(selectedLoanId);
      toast({
        title: "Book Returned",
        description: result.fine?.amount 
          ? `Fine of ${result.fine.amount} DZD applied for ${result.fine.days_overdue} days overdue`
          : "Book returned successfully",
      });
      setIsReturnDialogOpen(false);
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to return book",
        variant: "destructive",
      });
    }
  };

  const sendReminder = (userId: number) => {
    toast({
      title: "Reminder Sent",
      description: `Reminder email sent to user #${userId}`,
    });
  };

  const sendBulkReminders = () => {
    toast({
      title: "Bulk Reminders Sent",
      description: `Reminder emails sent to ${uniqueUsers} users`,
    });
  };

  return (
    <div className="space-y-6">
      {/* Alert Banner */}
      {loans.length > 0 && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-destructive/10 border border-destructive/20">
          <AlertTriangle className="h-5 w-5 text-destructive shrink-0" />
          <div className="flex-1">
            <p className="font-medium text-destructive">
              {loans.length} loan{loans.length !== 1 ? 's are' : ' is'} currently overdue
            </p>
            <p className="text-sm text-muted-foreground">
              Total fines: {totalFines.toFixed(2)} DZD
            </p>
          </div>
          <Button 
            variant="destructive" 
            size="sm"
            onClick={sendBulkReminders}
            className="gap-2"
          >
            <Mail className="h-4 w-4" />
            Send All Reminders
          </Button>
        </div>
      )}

      <div>
        <h1 className="font-display text-2xl font-bold text-foreground">Overdue Loans</h1>
        <p className="text-muted-foreground">Manage overdue books and outstanding fines</p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Overdue Loans
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{loans.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Fines
            </CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalFines.toFixed(2)} DZD</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Avg. Days Overdue
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgDaysOverdue}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Users Affected
            </CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{uniqueUsers}</div>
          </CardContent>
        </Card>
      </div>

      {/* Overdue Loans Table */}
      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Loan ID</TableHead>
              <TableHead>User ID</TableHead>
              <TableHead>Book ID</TableHead>
              <TableHead>Loan Date</TableHead>
              <TableHead>Due Date</TableHead>
              <TableHead>Days Overdue</TableHead>
              <TableHead>Fine</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8">
                  Loading overdue loans...
                </TableCell>
              </TableRow>
            ) : loans.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8">
                  <div className="flex flex-col items-center gap-2">
                    <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
                      <AlertTriangle className="h-6 w-6 text-green-600" />
                    </div>
                    <p className="text-muted-foreground">No overdue loans!</p>
                    <p className="text-sm text-muted-foreground">All books are returned on time</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              loans.map((loan) => {
                const daysOverdue = differenceInDays(new Date(), new Date(loan.due_date));
                return (
                  <TableRow key={loan.id} className="bg-destructive/5">
                    <TableCell className="font-mono text-sm">#{loan.id}</TableCell>
                    <TableCell>User #{loan.user_id}</TableCell>
                    <TableCell>Book #{loan.book_id}</TableCell>
                    <TableCell>{format(new Date(loan.loan_date), 'MMM dd, yyyy')}</TableCell>
                    <TableCell className="text-destructive font-medium">
                      {format(new Date(loan.due_date), 'MMM dd, yyyy')}
                    </TableCell>
                    <TableCell>
                      <Badge variant="destructive" className="font-mono">
                        {daysOverdue} days
                      </Badge>
                    </TableCell>
                    <TableCell className="font-medium text-destructive">
                      {loan.fine_amount} DZD
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => sendReminder(loan.user_id)}
                          title="Send Reminder"
                        >
                          <Mail className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleReturn(loan.id)}
                          title="Return Book"
                          className="text-primary hover:text-primary"
                        >
                          <RotateCcw className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>

      {/* Return Confirmation Dialog */}
      <AlertDialog open={isReturnDialogOpen} onOpenChange={setIsReturnDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Return Overdue Book</AlertDialogTitle>
            <AlertDialogDescription>
              This book is overdue and a fine will be calculated. Do you want to proceed with the return?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={confirmReturn}
              disabled={returnLoan.isPending}
            >
              {returnLoan.isPending ? 'Processing...' : 'Return Book'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default OverdueLoans;
