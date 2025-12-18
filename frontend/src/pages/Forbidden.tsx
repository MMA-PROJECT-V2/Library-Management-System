import { Link } from 'react-router-dom';
import { ShieldX, ArrowLeft, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';

const Forbidden = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="text-center animate-fade-in">
        <div className="mb-6 inline-flex h-20 w-20 items-center justify-center rounded-full bg-destructive/10">
          <ShieldX className="h-10 w-10 text-destructive" />
        </div>
        <h1 className="font-display text-4xl font-bold text-foreground mb-2">403</h1>
        <h2 className="text-xl font-medium text-foreground mb-4">Access Denied</h2>
        <p className="text-muted-foreground mb-8 max-w-md mx-auto">
          You don't have permission to access this page. Please contact an administrator if you believe this is an error.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button variant="outline" asChild>
            <Link to="/" onClick={() => window.history.back()}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Go Back
            </Link>
          </Button>
          <Button asChild>
            <Link to="/dashboard">
              <Home className="mr-2 h-4 w-4" />
              Dashboard
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Forbidden;
