import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Loader2 } from 'lucide-react';

interface PrivateRouteProps {
  children: React.ReactNode;
  requiredPermission?: string;
  requireLibrarianOrAdmin?: boolean;
  requireAdmin?: boolean;
}

export const PrivateRoute = ({ 
  children, 
  requiredPermission,
  requireLibrarianOrAdmin,
  requireAdmin,
}: PrivateRouteProps) => {
  const { isAuthenticated, isLoading, hasPermission, isLibrarianOrAdmin, isAdmin } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredPermission && !hasPermission(requiredPermission)) {
    return <Navigate to="/forbidden" replace />;
  }

  if (requireLibrarianOrAdmin && !isLibrarianOrAdmin) {
    return <Navigate to="/forbidden" replace />;
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/forbidden" replace />;
  }

  return <>{children}</>;
};
