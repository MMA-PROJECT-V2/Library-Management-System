import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { BookOpen, Eye, EyeOff, Loader2, UserPlus, Check } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import libraryBg from '@/assets/library-bg.jpg';

const registerSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  phone: z.string().optional(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

type RegisterFormData = z.infer<typeof registerSchema>;

const Register = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const password = watch('password', '');
  const passwordStrength = {
    length: password.length >= 8,
    hasNumber: /\d/.test(password),
    hasLetter: /[a-zA-Z]/.test(password),
  };

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    try {
      await registerUser({
        email: data.email,
        password: data.password,
        first_name: data.first_name,
        last_name: data.last_name,
        phone: data.phone,
      });
      toast({
        title: 'Registration Queued',
        description: 'Your account creation request has been sent. You will receive an email shortly.',
      });
      navigate('/login');
    } catch (error: any) {
      const message = error.response?.data?.email?.[0] ||
        error.response?.data?.detail ||
        'Registration failed. Please try again.';
      toast({
        title: 'Registration failed',
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
        <div className="absolute inset-0 bg-gradient-to-br from-accent/80 via-primary/60 to-primary/50 backdrop-blur-[2px]" />

        {/* Content */}
        <div className="relative z-10 max-w-lg text-center">
          <div className="mb-8 inline-flex h-24 w-24 items-center justify-center rounded-3xl bg-background/10 backdrop-blur-md border border-background/20 shadow-2xl">
            <BookOpen className="h-12 w-12 text-background" />
          </div>
          <h2 className="font-display text-4xl font-bold mb-6 text-background drop-shadow-lg">
            Join Our Community
          </h2>
          <p className="text-xl text-background/90 leading-relaxed mb-10">
            Create your account and start exploring our vast collection of books today.
          </p>

          {/* Features */}
          <div className="space-y-4 text-left max-w-sm mx-auto">
            {[
              'Access to thousands of books',
              'Track your reading progress',
              'Personalized recommendations',
              'Reserve books in advance',
            ].map((feature, index) => (
              <div key={index} className="flex items-center gap-3 text-background/90">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-background/20">
                  <Check className="h-4 w-4" />
                </div>
                <span>{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-8 bg-background relative overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-accent/5 rounded-full -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-primary/5 rounded-full translate-y-1/2 -translate-x-1/2" />

        <div className="w-full max-w-md space-y-6 animate-fade-in relative z-10">
          <div className="text-center">
            <Link to="/" className="inline-flex items-center gap-3 mb-6 group">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl gradient-hero shadow-lg group-hover:shadow-xl transition-shadow">
                <BookOpen className="h-6 w-6 text-primary-foreground" />
              </div>
              <span className="font-display text-3xl font-semibold text-foreground">BiblioTech</span>
            </Link>
            <h1 className="font-display text-3xl sm:text-4xl font-bold text-foreground">Create an account</h1>
            <p className="mt-2 text-muted-foreground">
              Start your reading journey today
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label htmlFor="first_name">First name</Label>
                <Input
                  id="first_name"
                  placeholder="John"
                  {...register('first_name')}
                  className="h-11"
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="last_name">Last name</Label>
                <Input
                  id="last_name"
                  placeholder="Doe"
                  {...register('last_name')}
                  className="h-11"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="email">Email address</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                {...register('email')}
                className={`h-11 ${errors.email ? 'border-destructive focus-visible:ring-destructive' : ''}`}
              />
              {errors.email && (
                <p className="text-sm text-destructive">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="phone">Phone (optional)</Label>
              <Input
                id="phone"
                type="tel"
                placeholder="+213 555 123 456"
                {...register('phone')}
                className="h-11"
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="At least 8 characters"
                  {...register('password')}
                  className={`h-11 pr-12 ${errors.password ? 'border-destructive focus-visible:ring-destructive' : ''}`}
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
              {/* Password strength indicators */}
              {password && (
                <div className="flex gap-2 mt-2">
                  <div className={`h-1 flex-1 rounded-full transition-colors ${passwordStrength.length ? 'bg-accent' : 'bg-muted'}`} />
                  <div className={`h-1 flex-1 rounded-full transition-colors ${passwordStrength.hasLetter ? 'bg-accent' : 'bg-muted'}`} />
                  <div className={`h-1 flex-1 rounded-full transition-colors ${passwordStrength.hasNumber ? 'bg-accent' : 'bg-muted'}`} />
                </div>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="confirmPassword">Confirm password</Label>
              <Input
                id="confirmPassword"
                type={showPassword ? 'text' : 'password'}
                placeholder="Confirm your password"
                {...register('confirmPassword')}
                className={`h-11 ${errors.confirmPassword ? 'border-destructive focus-visible:ring-destructive' : ''}`}
              />
              {errors.confirmPassword && (
                <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>
              )}
            </div>

            <Button type="submit" className="w-full h-12 text-base font-semibold shadow-lg hover:shadow-xl transition-all mt-6" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Creating account...
                </>
              ) : (
                <>
                  <UserPlus className="mr-2 h-5 w-5" />
                  Create account
                </>
              )}
            </Button>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-background px-4 text-muted-foreground">Already a member?</span>
            </div>
          </div>

          <p className="text-center">
            <Link to="/login" className="inline-flex items-center gap-2 font-semibold text-primary hover:text-primary/80 transition-colors">
              Sign in to your account
              <span className="text-lg">→</span>
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
