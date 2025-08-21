"use client";

import { motion, useAnimation, useMotionValue, useTransform, PanInfo } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Upload, 
  Brain, 
  FileText, 
  Download, 
  Zap, 
  Shield, 
  Clock, 
  Star,
  ArrowRight,
  Check
} from "lucide-react";
import Link from "next/link";
import { Navigation } from "@/components/navigation";
import { ThemeToggle } from "@/components/theme-toggle";
import Logo from "@/components/logo";
import ComparisonSlider from "@/components/comparison-slider";

const fadeInUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
};

const staggerChildren = {
  visible: {
    transition: {
      staggerChildren: 0.1
    }
  }
};

export default function Home() {
  // Slider state and refs
  const sliderRef = useRef(null);
  const containerRef = useRef(null);
  const [sliderWidth, setSliderWidth] = useState(0);
  const controls = useAnimation();
  const x = useMotionValue(0);
  const width = useTransform(x, [0, 100], ['0%', '100%']);

  // Initialize slider width on mount and window resize
  useEffect(() => {
    const updateSliderWidth = () => {
      if (containerRef.current) {
        setSliderWidth(containerRef.current.offsetWidth);
      }
    };

    updateSliderWidth();
    window.addEventListener('resize', updateSliderWidth);
    return () => window.removeEventListener('resize', updateSliderWidth);
  }, []);

  // Handle drag on slider
  const handleDrag = (event, info) => {
    const newX = x.get();
    if (newX >= 0 && newX <= 100) {
      x.set(newX + (info.delta.x / sliderWidth) * 100);
    }
  };

  // Handle drag end to ensure slider stays within bounds
  const handleDragEnd = (event, info) => {
    let newX = x.get();
    if (newX < 0) newX = 0;
    if (newX > 100) newX = 100;
    x.set(newX);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-background/80">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] dark:bg-grid-slate-700/25" />
      
      <Navigation />

      {/* Hero Section */}
      <section className="relative overflow-hidden px-4 pt-24 pb-16">
        <div className="container mx-auto max-w-6xl">
          <motion.div 
            className="text-center space-y-8"
            initial="hidden"
            animate="visible"
            variants={staggerChildren}
          >
            <motion.div variants={fadeInUp} className="space-y-4">
              <Badge variant="secondary" className="mb-4 px-3 py-1">
                <Zap className="w-3 h-3 mr-1" />
                AI-Powered Form Processing
              </Badge>
              
              <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight">
                Fill PDF Forms with
                <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600 bg-clip-text text-transparent"> AI Magic</span>
              </h1>
              
              <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
                Upload any PDF form, let our AI extract and understand the fields, then fill them intelligently. 
                The future of document processing is here.
              </p>
            </motion.div>

            <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className="text-lg px-8 py-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                <Link href="/dashboard">
                  Get Started Free
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" className="text-lg px-8 py-6">
                Watch Demo
              </Button>
            </motion.div>

            <motion.div variants={fadeInUp} className="flex items-center justify-center gap-8 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Check className="w-4 h-4 text-green-500" />
                No credit card required
              </div>
              <div className="flex items-center gap-1">
                <Check className="w-4 h-4 text-green-500" />
                Process unlimited PDFs
              </div>
              <div className="flex items-center gap-1">
                <Check className="w-4 h-4 text-green-500" />
                Enterprise-grade security
              </div>
            </motion.div>
          </motion.div>

          {/* Hero Image/Demo */}
          <motion.div 
            className="mt-16"
            variants={fadeInUp}
            initial="hidden"
            animate="visible"
            transition={{ delay: 0.5 }}
          >
            <div className="relative mx-auto max-w-4xl">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-3xl blur-3xl" />
              <Card className="relative p-2 bg-background/50 backdrop-blur-sm border-0 shadow-2xl">
                <div className="aspect-video bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 rounded-2xl flex items-center justify-center">
                  <div className="text-center space-y-4">
                    <div className="w-20 h-20 mx-auto bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                      <FileText className="w-10 h-10 text-white" />
                    </div>
                    <p className="text-muted-foreground">Interactive Demo Coming Soon</p>
                  </div>
                </div>
              </Card>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Before & After Section */}
      <ComparisonSlider />

      {/* Features Section */}
      <section className="py-24 px-4" id="features">
        <div className="container mx-auto max-w-6xl">
          <motion.div 
            className="text-center mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerChildren}
          >
            <motion.h2 variants={fadeInUp} className="text-3xl md:text-4xl font-bold mb-4">
              How It Works
            </motion.h2>
            <motion.p variants={fadeInUp} className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Transform your PDF forms in just a few clicks with our intelligent processing pipeline
            </motion.p>
          </motion.div>

          <motion.div 
            className="grid md:grid-cols-4 gap-8"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerChildren}
          >
            {[
              {
                icon: Upload,
                title: "Upload PDF",
                description: "Drag & drop your PDF form or click to browse. We support all PDF formats.",
                color: "from-blue-500 to-blue-600"
              },
              {
                icon: Brain,
                title: "AI Analysis",
                description: "Our AI analyzes your form, extracts fields, and understands the context.",
                color: "from-purple-500 to-purple-600"
              },
              {
                icon: FileText,
                title: "Smart Filling",
                description: "Fill forms intelligently with our guided wizard and real-time preview.",
                color: "from-green-500 to-green-600"
              },
              {
                icon: Download,
                title: "Download",
                description: "Get your completed PDF instantly, ready for submission or printing.",
                color: "from-orange-500 to-orange-600"
              }
            ].map((feature, index) => (
              <motion.div key={index} variants={fadeInUp}>
                <Card className="p-6 h-full text-center group hover:shadow-lg transition-all duration-300 border-0 bg-background/50 backdrop-blur-sm">
                  <div className={`w-16 h-16 mx-auto mb-4 bg-gradient-to-r ${feature.color} rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                    <feature.icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-24 px-4 bg-muted/30" id="benefits">
        <div className="container mx-auto max-w-6xl">
          <motion.div 
            className="grid lg:grid-cols-2 gap-16 items-center"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerChildren}
          >
            <motion.div variants={fadeInUp} className="space-y-8">
              <div className="space-y-4">
                <h2 className="text-3xl md:text-4xl font-bold">
                  Why Choose Our Platform?
                </h2>
                <p className="text-xl text-muted-foreground">
                  Experience the next generation of document processing with features designed for efficiency and accuracy.
                </p>
              </div>

              <div className="space-y-6">
                {[
                  {
                    icon: Zap,
                    title: "Lightning Fast Processing",
                    description: "Process complex forms in seconds, not minutes."
                  },
                  {
                    icon: Shield,
                    title: "Bank-Grade Security",
                    description: "Your documents are encrypted and never stored permanently."
                  },
                  {
                    icon: Clock,
                    title: "Save Hours of Time",
                    description: "Automate repetitive form filling and focus on what matters."
                  }
                ].map((benefit, index) => (
                  <div key={index} className="flex gap-4">
                    <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
                      <benefit.icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg mb-1">{benefit.title}</h3>
                      <p className="text-muted-foreground">{benefit.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div variants={fadeInUp} className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-3xl blur-3xl" />
              <Card className="relative p-8 bg-background/80 backdrop-blur-sm border-0 shadow-2xl">
                <div className="space-y-6">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                      <Check className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold">Form Processing Complete</p>
                      <p className="text-sm text-muted-foreground">12 fields extracted and filled</p>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span>Processing Speed</span>
                      <span className="font-semibold">2.3s</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div className="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full w-[95%]"></div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-bold text-blue-600">99.7%</p>
                      <p className="text-sm text-muted-foreground">Accuracy Rate</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-purple-600">2.1s</p>
                      <p className="text-sm text-muted-foreground">Avg Process Time</p>
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-24 px-4" id="pricing">
        <div className="container mx-auto max-w-4xl">
          <motion.div 
            className="text-center mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerChildren}
          >
            <motion.h2 variants={fadeInUp} className="text-3xl md:text-4xl font-bold mb-4">
              Simple, Transparent Pricing
            </motion.h2>
            <motion.p variants={fadeInUp} className="text-xl text-muted-foreground">
              Start for free and scale as you grow. No hidden fees, no surprises.
            </motion.p>
          </motion.div>

          <motion.div 
            className="grid md:grid-cols-3 gap-8"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerChildren}
          >
            {[
              {
                name: "Free",
                price: "$0",
                period: "forever",
                description: "Perfect for getting started",
                features: [
                  "No credit card required",
                  "No hidden fees",
                  "50 credits for 1 month",
                  "Basic field detection",
                  "Standard processing",
                  "Email support"
                ],
                buttonText: "Start Free",
                popular: false
              },
              {
                name: "Pro",
                price: "$9.99",
                period: "per month",
                description: "For professionals and small teams",
                features: [
                  "500 credits for 1 month",
                  "Advanced AI analysis - coming soon",
                  "Priority processing - coming soon",
                  "Template library - coming soon",
                  "API access - coming soon",
                  "Priority support - coming soon"
                ],
                buttonText: "Start Pro Trial",
                popular: true
              },
              {
                name: "Enterprise",
                price: "Custom",
                period: "pricing",
                description: "For large organizations",
                features: [
                  "Everything in Pro",
                  "Custom integrations - coming soon",
                  "Dedicated support - coming soon",
                  "SLA guarantees - coming soon",
                  "On-premise deployment - coming soon",
                  "Advanced analytics - coming soon"
                ],
                buttonText: "Contact Sales",
                popular: false
              }
            ].map((plan, index) => (
              <motion.div key={index} variants={fadeInUp}>
                <Card className={`p-8 h-full relative ${plan.popular ? 'border-purple-500 border-2' : 'border-0 bg-background/50 backdrop-blur-sm'}`}>
                  {plan.popular && (
                    <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-purple-500 to-blue-500 text-white">
                      Most Popular
                    </Badge>
                  )}
                  
                  <div className="text-center mb-8">
                    <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                    <div className="mb-2">
                      <span className="text-4xl font-bold">{plan.price}</span>
                      {plan.period !== "pricing" && (
                        <span className="text-muted-foreground">/{plan.period}</span>
                      )}
                    </div>
                    <p className="text-muted-foreground">{plan.description}</p>
                  </div>

                  <div className="space-y-4 mb-8">
                    {plan.features.map((feature, featureIndex) => (
                      <div key={featureIndex} className="flex items-center gap-3">
                        <Check className="w-5 h-5 text-green-500 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </div>
                    ))}
                  </div>

                  <Button 
                    className={`w-full ${plan.popular ? 'bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600' : ''}`}
                    variant={plan.popular ? "default" : "outline"}
                    onClick={() => {
                      if (plan.buttonText === "Get Started Free") {
                        window.location.href = "/dashboard";
                      }else if (plan.buttonText === "Contact Sales") {
                        window.location.href = "mailto:thugaltechnologies@gmail.com";
                      }else {
                        window.location.href = "/signup";
                      }
                    }}
                  >
                    {plan.buttonText}
                  </Button>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-4 bg-gradient-to-r from-blue-600 to-purple-600" id="cta">
        <div className="container mx-auto max-w-4xl text-center text-white">
          <motion.div 
            className="space-y-8"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerChildren}
          >
            <motion.h2 variants={fadeInUp} className="text-3xl md:text-4xl font-bold">
              Ready to Transform Your PDF Workflow?
            </motion.h2>
            <motion.p variants={fadeInUp} className="text-xl opacity-90 max-w-2xl mx-auto">
              Join thousands of users who are already saving hours every week with our AI-powered form filling.
            </motion.p>
            <motion.div variants={fadeInUp}>
              <Button asChild size="lg" className="bg-white text-blue-600 hover:bg-white/90 text-lg px-8 py-6">
                <Link href="/signup">
                  Start Your Free Trial
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Link>
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 border-t bg-background/50 backdrop-blur-sm">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center gap-2">
              <Logo />
            </div>
            <p className="text-muted-foreground">
              &copy; 2024 FormFella. All rights reserved. Built for productivity.
            </p>
            <div className="flex items-center justify-center gap-6 text-sm text-muted-foreground">
              <Link href="/privacy" className="hover:text-foreground">Privacy Policy</Link>
              <Link href="/terms" className="hover:text-foreground">Terms of Service</Link>
              <Link href="/contact" className="hover:text-foreground">Contact</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}