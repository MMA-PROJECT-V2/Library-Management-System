import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { User, Mail, Phone, MapPin, Calendar, Loader2, Camera } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';

const profileSchema = z.object({
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  phone: z.string().optional(),
  bio: z.string().max(500, 'Bio must be less than 500 characters').optional(),
  address: z.string().optional(),
  birth_date: z.string().optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

const Profile = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      phone: user?.phone || '',
      bio: '',
      address: '',
      birth_date: '',
    },
  });

  const onSubmit = async (data: ProfileFormData) => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast({
        title: 'Profile updated',
        description: 'Your profile has been updated successfully.',
      });
    } catch (error) {
      toast({
        title: 'Update failed',
        description: 'Failed to update profile. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getInitials = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    return user?.email?.[0]?.toUpperCase() || 'U';
  };

  const getRoleBadgeVariant = () => {
    switch (user?.role) {
      case 'ADMIN':
        return 'destructive';
      case 'LIBRARIAN':
        return 'default';
      default:
        return 'secondary';
    }
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      <div>
        <h1 className="font-display text-3xl font-bold text-foreground">Profile</h1>
        <p className="mt-1 text-muted-foreground">
          Manage your personal information and preferences
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-[280px_1fr]">
        {/* User Info Card */}
        <Card className="h-fit">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center text-center">
              <div className="relative group">
                <Avatar className="h-24 w-24 border-4 border-primary/20">
                  <AvatarImage src="" />
                  <AvatarFallback className="bg-primary text-primary-foreground text-2xl font-semibold">
                    {getInitials()}
                  </AvatarFallback>
                </Avatar>
                <button className="absolute bottom-0 right-0 flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-md transition-transform hover:scale-110">
                  <Camera className="h-4 w-4" />
                </button>
              </div>

              <h3 className="mt-4 font-display text-xl font-semibold">
                {user?.first_name} {user?.last_name}
              </h3>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
              
              <Badge variant={getRoleBadgeVariant()} className="mt-3">
                {user?.role}
              </Badge>

              <Separator className="my-4" />

              <div className="w-full space-y-3 text-left text-sm">
                <div className="flex items-center gap-3 text-muted-foreground">
                  <Mail className="h-4 w-4" />
                  <span className="truncate">{user?.email}</span>
                </div>
                {user?.phone && (
                  <div className="flex items-center gap-3 text-muted-foreground">
                    <Phone className="h-4 w-4" />
                    <span>{user.phone}</span>
                  </div>
                )}
                <div className="flex items-center gap-3 text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  <span>Member since {new Date(user?.date_joined || '').toLocaleDateString()}</span>
                </div>
              </div>

              <Separator className="my-4" />

              <div className="w-full rounded-lg bg-muted p-3 text-center">
                <p className="text-sm text-muted-foreground">Maximum Loans</p>
                <p className="text-2xl font-bold text-primary">{user?.max_loans || 5}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Edit Profile Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Edit Profile
            </CardTitle>
            <CardDescription>
              Update your personal information
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="first_name">First Name</Label>
                  <Input
                    id="first_name"
                    placeholder="John"
                    {...register('first_name')}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="last_name">Last Name</Label>
                  <Input
                    id="last_name"
                    placeholder="Doe"
                    {...register('last_name')}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Phone</Label>
                <Input
                  id="phone"
                  type="tel"
                  placeholder="+213 555 123 456"
                  {...register('phone')}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="birth_date">Birth Date</Label>
                <Input
                  id="birth_date"
                  type="date"
                  {...register('birth_date')}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="address">Address</Label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="address"
                    placeholder="123 Main Street, City"
                    className="pl-10"
                    {...register('address')}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="bio">Bio</Label>
                <Textarea
                  id="bio"
                  placeholder="Tell us about yourself..."
                  rows={4}
                  {...register('bio')}
                  className={errors.bio ? 'border-destructive' : ''}
                />
                {errors.bio && (
                  <p className="text-sm text-destructive">{errors.bio.message}</p>
                )}
              </div>

              <div className="flex justify-end gap-3">
                <Button type="button" variant="outline" disabled={isLoading}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading || !isDirty}>
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    'Save Changes'
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Profile;
