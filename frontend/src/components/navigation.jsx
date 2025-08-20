// In src/components/navigation.jsx
"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { FileText, Menu, X, User, LogOut, DollarSign } from "lucide-react";
import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";
import { useRouter } from "next/navigation";
import { Label } from "@/components/ui/label";
import Logo from "./logo";

export function Navigation() {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();
  const [credits, setCredits] = useState(0);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check if user is logged in by checking for the access_token cookie
    const checkAuth = () => {
      const cookies = document.cookie.split(';').map(cookie => cookie.trim());
      const hasToken = cookies.some(cookie => cookie.startsWith('access_token='));
      setIsLoggedIn(hasToken);
    };

    checkAuth();
  }, []);



const fetchUser = async () => {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/me`, {
      headers: {
        'Authorization': `Bearer ${document.cookie
          .split('; ')
          .find(row => row.startsWith('access_token='))
          ?.split('=')[1]}`
      }
    });
    const data = await response.json();
    setCredits(data.credits);
    setUser(data.user[2]);
  } catch (error) {
    console.error('Failed to fetch user:', error);
  }
};

useEffect(() => {
  fetchUser();
}, []);

  const handleLogout = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${document.cookie
            .split('; ')
            .find(row => row.startsWith('access_token='))
            ?.split('=')[1]}`
        }
      });

      // Clear the cookie
      document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      setIsLoggedIn(false);
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Logo />

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {!isLoggedIn && <div className="flex items-center gap-6">
              <Link href="#features" className="text-sm font-medium hover:text-primary transition-colors">
                Features
              </Link>
              <Link href="#pricing" className="text-sm font-medium hover:text-primary transition-colors">
                Pricing
              </Link>
              <Link href="#benefits" className="text-sm font-medium hover:text-primary transition-colors">
                Benefits
              </Link>
              <Link href="#cta" className="text-sm font-medium hover:text-primary transition-colors">
                CTA
              </Link>
            </div>}
            
            <div className="flex items-center gap-4">
              <ThemeToggle />
              {isLoggedIn ? (
                <div className="relative group">
                  <Button variant="outline" className="flex items-center gap-2">
                    <User className="w-4 h-4" />
                    Hello, {user?.Value}
                  </Button>
                  <div className="absolute right-0 mt-2 w-48 bg-background border rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    

                    {/* credits */}
                    <Label href="/dashboard/credits" className="w-full text-left px-4 py-2 text-sm hover:bg-muted flex items-center gap-2">
                      Credits: {credits}
                    </Label>
                    
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-sm hover:bg-muted flex items-center gap-2"
                    >
                      <LogOut className="w-4 h-4" />
                      Sign Out
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <Button variant="ghost" asChild>
                    <Link href="/login">Sign In</Link>
                  </Button>
                  <Button asChild className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600">
                    <Link href="/signup">Get Started</Link>
                  </Button>
                </>
              )}
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-2">
            <ThemeToggle />
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsOpen(!isOpen)}
            >
              {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t py-4"
          >
            <div className="space-y-4">
              <Link
                href="#features"
                className="block text-sm font-medium hover:text-primary transition-colors"
                onClick={() => setIsOpen(false)}
              >
                Features
              </Link>
              <Link
                href="#pricing"
                className="block text-sm font-medium hover:text-primary transition-colors"
                onClick={() => setIsOpen(false)}
              >
                Pricing
              </Link>
              <Link
                href="#docs"
                className="block text-sm font-medium hover:text-primary transition-colors"
                onClick={() => setIsOpen(false)}
              >
                Docs
              </Link>
              <Link
                href="#support"
                className="block text-sm font-medium hover:text-primary transition-colors"
                onClick={() => setIsOpen(false)}
              >
                Support
              </Link>
              {isLoggedIn ? (
                <button
                  onClick={() => {
                    handleLogout();
                    setIsOpen(false);
                  }}
                  className="w-full text-left text-sm font-medium hover:text-primary transition-colors"
                >
                  Sign Out
                </button>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="block text-sm font-medium hover:text-primary transition-colors"
                    onClick={() => setIsOpen(false)}
                  >
                    Sign In
                  </Link>
                  <Button asChild className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600">
                    <Link href="/signup" onClick={() => setIsOpen(false)}>
                      Get Started
                    </Link>
                  </Button>
                </>
              )}
            </div>
          </motion.div>
        )}
      </div>
    </nav>
  );
}