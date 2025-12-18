import { Link, Navigate } from 'react-router-dom';
import { BookOpen, Library, Users, Clock, ArrowRight, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Header } from '@/components/layout/Header';
import { useAuth } from '@/contexts/AuthContext';

const features = [
  {
    icon: BookOpen,
    title: 'Extensive Collection',
    description: 'Access thousands of books across all genres and categories',
  },
  {
    icon: Clock,
    title: 'Easy Borrowing',
    description: 'Borrow books with just a click, track due dates automatically',
  },
  {
    icon: Library,
    title: 'Digital Management',
    description: 'Manage your reading history and preferences in one place',
  },
  {
    icon: Users,
    title: 'Community Reviews',
    description: 'Read and share reviews with fellow book enthusiasts',
  },
];

const Landing = () => {
  const { isAuthenticated, isLoading } = useAuth();

  // Redirect authenticated users to dashboard
  if (!isLoading && isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,hsl(var(--primary)/0.1),transparent_50%)]" />
          <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
        </div>

        <div className="container mx-auto px-4 py-20 md:py-32">
          <div className="mx-auto max-w-4xl text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm font-medium text-primary">
              <Sparkles className="h-4 w-4" />
              Welcome to BiblioTech
            </div>
            
            <h1 className="font-display text-4xl font-bold tracking-tight text-foreground sm:text-5xl md:text-6xl lg:text-7xl animate-fade-in">
              Your Digital
              <span className="block text-primary">Library Experience</span>
            </h1>
            
            <p className="mt-6 text-lg text-muted-foreground md:text-xl max-w-2xl mx-auto animate-slide-up" style={{ animationDelay: '0.1s' }}>
              Discover, borrow, and manage books with ease. Join our community of readers 
              and explore a world of knowledge at your fingertips.
            </p>

            <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row animate-slide-up" style={{ animationDelay: '0.2s' }}>
              <Button size="lg" asChild className="group w-full sm:w-auto">
                <Link to="/register">
                  Get Started
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild className="w-full sm:w-auto">
                <Link to="/login">
                  Sign In
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="border-t border-border/50 bg-muted/30 py-20 md:py-28">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="font-display text-3xl font-bold text-foreground sm:text-4xl">
              Everything You Need
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              A complete library management solution designed for the modern reader
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            {features.map((feature, index) => (
              <div
                key={feature.title}
                className="group relative rounded-2xl border border-border/50 bg-card p-6 shadow-sm transition-all duration-300 hover:shadow-md hover:border-primary/30 animate-slide-up"
                style={{ animationDelay: `${0.1 * index}s` }}
              >
                <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="mb-2 font-display text-xl font-semibold text-foreground">
                  {feature.title}
                </h3>
                <p className="text-muted-foreground">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="border-t border-border/50 py-20 md:py-28">
        <div className="container mx-auto px-4">
          <div className="relative mx-auto max-w-4xl overflow-hidden rounded-3xl gradient-hero p-8 md:p-16 text-center shadow-xl">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,hsl(35_80%_60%/0.3),transparent_70%)]" />
            
            <div className="relative">
              <h2 className="font-display text-3xl font-bold text-primary-foreground sm:text-4xl md:text-5xl">
                Ready to Start Reading?
              </h2>
              <p className="mt-4 text-lg text-primary-foreground/80 max-w-xl mx-auto">
                Join thousands of members who have discovered their next favorite book through BiblioTech.
              </p>
              <div className="mt-8">
                <Button size="lg" variant="secondary" asChild className="group">
                  <Link to="/register">
                    Create Free Account
                    <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/50 bg-muted/20 py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg gradient-hero">
                <BookOpen className="h-4 w-4 text-primary-foreground" />
              </div>
              <span className="font-display text-lg font-semibold text-foreground">BiblioTech</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2025 BiblioTech. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;