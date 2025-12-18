import { Link } from "react-router-dom";
import { Home, ArrowLeft, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";

const NotFound = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="text-center animate-fade-in">
        <div className="mb-6 inline-flex h-20 w-20 items-center justify-center rounded-full bg-primary/10">
          <BookOpen className="h-10 w-10 text-primary" />
        </div>
        <h1 className="font-display text-6xl font-bold text-foreground mb-2">404</h1>
        <h2 className="text-xl font-medium text-foreground mb-4">Page Not Found</h2>
        <p className="text-muted-foreground mb-8 max-w-md mx-auto">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button variant="outline" onClick={() => window.history.back()}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Go Back
          </Button>
          <Button asChild>
            <Link to="/">
              <Home className="mr-2 h-4 w-4" />
              Home
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
