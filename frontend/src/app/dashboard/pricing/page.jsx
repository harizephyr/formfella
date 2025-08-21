"use client";
import React from 'react'
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check } from "lucide-react";
import { Button } from "@/components/ui/button";

const Pricing = () => {
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

      const handleUpgradeToPro = async () => {
        try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/checkout/create-session`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${document.cookie.split('; ')
            .find(row => row.startsWith('access_token='))
            ?.split('=')[1]}`,
          },
          body: JSON.stringify({
            "price_id": "price_1Ry2k3So9oKPE35ZeVng05Sy",
            "amount": 999,
            "currency": "usd",
            "customer_email": "test@gmail.com",
            "success_url": `${process.env.NEXT_PUBLIC_API_URL}/dashboard/pricing/success`,
            "cancel_url": `${process.env.NEXT_PUBLIC_API_URL}/dashboard/pricing/fail`,
            "mode": "payment"
          }),
        });
        // console.log(response);
        const data = await response.json();
        // new tab
        // save session id in cookie
        document.cookie = `payment_session_id=${data.session_id}; path=/; expires=${new Date(Date.now() + 60 * 60 * 24 * 7).toUTCString()}`;
        window.open(data.checkout_url, '_blank');
      } catch (error) {
        console.log(error);
      }
      }
  return (
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
        className="grid md:grid-cols-2 gap-8"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        variants={staggerChildren}
      >
        {[
        //   {
        //     name: "Free",
        //     price: "$0",
        //     period: "forever",
        //     description: "Perfect for getting started",
        //     features: [
        //       "5 PDF forms per month",
        //       "Basic field detection",
        //       "Standard processing",
        //       "Email support"
        //     ],
        //     buttonText: "Start Free",
        //     popular: false
        //   },
          {
            name: "Pro",
            price: "$9.99",
            period: "per month",
            description: "For professionals and small teams",
            features: [
              "500 credits per month",
              "Advanced AI analysis - coming soon",
              "Priority processing - coming soon",
              "Template library - coming soon",
              "API access - coming soon",
              "Priority support - coming soon"
            ],
            buttonText: "Upgrade to Pro",
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
                  if (plan.buttonText === "Upgrade to Pro") {
                    handleUpgradeToPro();
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
  )
}

export default Pricing;