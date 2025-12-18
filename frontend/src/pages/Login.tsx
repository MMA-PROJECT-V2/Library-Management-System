import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { BookOpen, Eye, EyeOff, Loader2, Sparkles } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import libraryBg from '@/assets/library-bg.jpg';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

const Login = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/dashboard';

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      await login({ email: data.email, password: data.password });
      toast({
        title: 'Welcome back!',
        description: 'You have successfully logged in.',
      });
      navigate(from, { replace: true });
    } catch (error: any) {
      const message = error.response?.data?.non_field_errors?.[0] || 
                     error.response?.data?.detail ||
                     'Invalid email or password';
      toast({
        title: 'Login failed',
        description: message,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Image Background */}
      <div 
        className="hidden lg:flex lg:flex-1 relative items-center justify-center p-12"
        style={{
          backgroundImage: `url(${libraryBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        {/* Overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/80 via-primary/60 to-accent/50 backdrop-blur-[2px]" />
        
        {/* Content */}
        <div className="relative z-10 max-w-lg text-center">
          <div className="mb-8 inline-flex h-24 w-24 items-center justify-center rounded-3xl bg-background/10 backdrop-blur-md border border-background/20 shadow-2xl">
            <BookOpen className="h-12 w-12 text-background" />
          </div>
          <h2 className="font-display text-4xl font-bold mb-6 text-background drop-shadow-lg">
            Your Personal Library Awaits
          </h2>
          <p className="text-xl text-background/90 leading-relaxed">
            Access thousands of books, track your reading progress, and discover new favorites in our carefully curated collection.
          </p>
          <div className="mt-10 flex items-center justify-center gap-8 text-background/80">
            <div className="text-center">
              <div className="text-3xl font-bold text-background">10K+</div>
              <div className="text-sm">Books</div>
            </div>
            <div className="w-px h-12 bg-background/30" />
            <div className="text-center">
              <div className="text-3xl font-bold text-background">5K+</div>
              <div className="text-sm">Members</div>
            </div>
            <div className="w-px h-12 bg-background/30" />
            <div className="text-center">
              <div className="text-3xl font-bold text-background">24/7</div>
              <div className="text-sm">Access</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-background relative overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-accent/5 rounded-full translate-y-1/2 -translate-x-1/2" />
        
        <div className="w-full max-w-md space-y-8 animate-fade-in relative z-10">
          <div className="text-center">
            <Link to="/" className="inline-flex items-center gap-3 mb-8 group">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl gradient-hero shadow-lg group-hover:shadow-xl transition-shadow">
                <BookOpen className="h-6 w-6 text-primary-foreground" />
              </div>
              <span className="font-display text-3xl font-semibold text-foreground">BiblioTech</span>
            </Link>
            <h1 className="font-display text-4xl font-bold text-foreground">Welcome back</h1>
            <p className="mt-3 text-lg text-muted-foreground">
              Sign in to continue to your library
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-base font-medium">Email address</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                {...register('email')}
                className={`h-12 text-base ${errors.email ? 'border-destructive focus-visible:ring-destructive' : ''}`}
              />
              {errors.email && (
                <p className="text-sm text-destructive">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-base font-medium">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  {...register('password')}
                  className={`h-12 text-base pr-12 ${errors.password ? 'border-destructive focus-visible:ring-destructive' : ''}`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
              {errors.password && (
                <p className="text-sm text-destructive">{errors.password.message}</p>
              )}
            </div>

            <Button type="submit" className="w-full h-12 text-base font-semibold shadow-lg hover:shadow-xl transition-all" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-5 w-5" />
                  Sign in
                </>
              )}
            </Button>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-background px-4 text-muted-foreground">New to BiblioTech?</span>
            </div>
          </div>

          <p className="text-center">
            <Link to="/register" className="inline-flex items-center gap-2 font-semibold text-primary hover:text-primary/80 transition-colors">
              Create an account
              <span className="text-lg">→</span>
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
