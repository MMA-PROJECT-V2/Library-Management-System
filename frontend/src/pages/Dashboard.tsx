import { Link, useNavigate } from 'react-router-dom';
import { 
  BookOpen, 
  Library, 
  Calendar, 
  TrendingUp, 
  Clock, 
  AlertTriangle,
  ArrowRight,
  Plus,
  Loader2
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { StatusBadge } from '@/components/common/StatusBadge';
import { useUserActiveLoans, useActiveLoans, useOverdueLoans } from '@/hooks/useLoans';
import { useBooks } from '@/hooks/useBooks';

const Dashboard = () => {
  const { user, isLibrarianOrAdmin } = useAuth();
  const navigate = useNavigate();

  // Member data
  const { data: userActiveLoans, isLoading: isLoadingUserLoans } = useUserActiveLoans();
  const { data: booksData, isLoading: isLoadingBooks } = useBooks({ page: 1, page_size: 1 });

  // Admin data
  const { data: allActiveLoans, isLoading: isLoadingAllActive } = useActiveLoans();
  const { data: overdueLoansData, isLoading: isLoadingOverdue } = useOverdueLoans();

  const isLoading = isLibrarianOrAdmin 
    ? (isLoadingAllActive || isLoadingOverdue || isLoadingBooks)
    : (isLoadingUserLoans || isLoadingBooks);

  // Calculate member stats
  const activeLoans = userActiveLoans?.active_loans || [];
  const activeLoansCount = userActiveLoans?.count || 0;
  const totalBooks = booksData?.count || 0;
  
  const daysUntilDue = activeLoans.length > 0
    ? Math.min(...activeLoans.map((l: any) => l.days_until_due).filter((d: number) => d > 0))
    : 0;
  
  const overdueCount = activeLoans.filter((l: any) => l.is_overdue).length;

  // Admin stats
  const adminActiveLoansCount = allActiveLoans?.count || 0;
  const adminOverdueCount = overdueLoansData?.count || 0;

  const statsCards = [
    {
      title: 'Active Loans',
      value: activeLoansCount,
      description: 'Books currently borrowed',
      icon: Library,
      href: '/my-loans',
      color: 'text-info',
      bgColor: 'bg-info/10',
    },
    {
      title: 'Books Available',
      value: totalBooks,
      description: 'In our collection',
      icon: BookOpen,
      href: '/books',
      color: 'text-accent',
      bgColor: 'bg-accent/10',
    },
    {
      title: 'Next Due Date',
      value: daysUntilDue > 0 ? `${daysUntilDue} days` : 'N/A',
      description: daysUntilDue < 3 && daysUntilDue > 0 ? 'Return soon!' : 'You have time',
      icon: Calendar,
      href: '/my-loans',
      color: daysUntilDue < 3 && daysUntilDue > 0 ? 'text-warning' : 'text-primary',
      bgColor: daysUntilDue < 3 && daysUntilDue > 0 ? 'bg-warning/10' : 'bg-primary/10',
    },
    {
      title: 'Overdue',
      value: overdueCount,
      description: overdueCount > 0 ? 'Please return ASAP' : 'All good!',
      icon: AlertTriangle,
      href: '/my-loans',
      color: overdueCount > 0 ? 'text-destructive' : 'text-success',
      bgColor: overdueCount > 0 ? 'bg-destructive/10' : 'bg-success/10',
    },
  ];

  const adminStatsCards = [
    {
      title: 'Total Active Loans',
      value: adminActiveLoansCount,
      description: 'Across all members',
      icon: Library,
      href: '/admin/loans',
      color: 'text-info',
      bgColor: 'bg-info/10',
    },
    {
      title: 'Total Books',
      value: totalBooks,
      description: 'In the library',
      icon: BookOpen,
      href: '/admin/books',
      color: 'text-accent',
      bgColor: 'bg-accent/10',
    },
    {
      title: 'Active Members',
      value: '-',
      description: 'Registered users',
      icon: TrendingUp,
      href: '#',
      color: 'text-primary',
      bgColor: 'bg-primary/10',
    },
    {
      title: 'Overdue Loans',
      value: adminOverdueCount,
      description: 'Require attention',
      icon: AlertTriangle,
      href: '/admin/overdue',
      color: adminOverdueCount > 0 ? 'text-destructive' : 'text-success',
      bgColor: adminOverdueCount > 0 ? 'bg-destructive/10' : 'bg-success/10',
    },
  ];

  const displayStats = isLibrarianOrAdmin ? adminStatsCards : statsCards;
  const displayLoans = activeLoans.slice(0, 5);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Welcome Section */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-foreground">
            Welcome back, {user?.first_name || 'Reader'}!
          </h1>
          <p className="mt-1 text-muted-foreground">
            {isLibrarianOrAdmin 
              ? "Here's an overview of the library system" 
              : "Here's what's happening with your library account"
            }
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => navigate('/books')}>
            <BookOpen className="mr-2 h-4 w-4" />
            Browse Books
          </Button>
          {isLibrarianOrAdmin && (
            <Button onClick={() => navigate('/admin/books')}>
              <Plus className="mr-2 h-4 w-4" />
              Add Book
            </Button>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {displayStats.map((stat, index) => (
          <Card 
            key={stat.title}
            className="group cursor-pointer transition-all duration-300 hover:shadow-md hover:border-primary/30 animate-slide-up"
            style={{ animationDelay: `${0.05 * index}s` }}
            onClick={() => navigate(stat.href)}
          >
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <div className={`rounded-lg p-2 ${stat.bgColor}`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
              <p className="text-xs text-muted-foreground mt-1">{stat.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Loans Section */}
      <Card className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="font-display text-xl">Recent Loans</CardTitle>
            <CardDescription>Your currently borrowed books</CardDescription>
          </div>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/my-loans" className="group">
              View all
              <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </Button>
        </CardHeader>
        <CardContent>
          {displayLoans.length > 0 ? (
            <div className="space-y-4">
              {displayLoans.map((loan: any) => (
                <div 
                  key={loan.id}
                  className="flex items-center justify-between rounded-lg border border-border/50 p-4 transition-colors hover:bg-muted/50"
                >
                  <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                      <BookOpen className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <h4 className="font-medium text-foreground">Book #{loan.book_id}</h4>
                      <p className="text-sm text-muted-foreground">Loan ID: {loan.id}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-sm font-medium text-foreground">
                        Due: {new Date(loan.due_date).toLocaleDateString()}
                      </p>
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        {loan.days_until_due > 0 
                          ? `${loan.days_until_due} days left` 
                          : `${Math.abs(loan.days_until_due)} days overdue`
                        }
                      </div>
                    </div>
                    <StatusBadge status={loan.status} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Library className="h-12 w-12 text-muted-foreground/50 mb-4" />
              <h3 className="font-medium text-foreground">No active loans</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Start by browsing our book collection
              </p>
              <Button asChild>
                <Link to="/books">Browse Books</Link>
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;