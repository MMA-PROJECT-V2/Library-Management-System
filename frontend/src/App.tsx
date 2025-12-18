import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "next-themes";
import { AuthProvider } from "@/contexts/AuthContext";
import { PrivateRoute } from "@/components/auth/PrivateRoute";
import { DashboardLayout } from "@/components/layout/DashboardLayout";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import BrowseBooks from "./pages/BrowseBooks";
import MyLoans from "./pages/MyLoans";
import Profile from "./pages/Profile";
import Forbidden from "./pages/Forbidden";
import NotFound from "./pages/NotFound";

// Admin pages
import ManageBooks from "./pages/admin/ManageBooks";
import AllLoans from "./pages/admin/AllLoans";
import OverdueLoans from "./pages/admin/OverdueLoans";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem storageKey="bibliotech-theme">
      <AuthProvider>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/forbidden" element={<Forbidden />} />

              {/* Protected Routes */}
              <Route element={<PrivateRoute><DashboardLayout /></PrivateRoute>}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/books" element={<BrowseBooks />} />
                <Route path="/my-loans" element={<MyLoans />} />
                <Route path="/profile" element={<Profile />} />
              </Route>

              {/* Admin Routes */}
              <Route element={<PrivateRoute requiredPermission="can_add_book"><DashboardLayout /></PrivateRoute>}>
                <Route path="/admin/books" element={<ManageBooks />} />
              </Route>
              <Route element={<PrivateRoute requiredPermission="can_view_all_loans"><DashboardLayout /></PrivateRoute>}>
                <Route path="/admin/loans" element={<AllLoans />} />
                <Route path="/admin/overdue" element={<OverdueLoans />} />
              </Route>

              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </AuthProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
