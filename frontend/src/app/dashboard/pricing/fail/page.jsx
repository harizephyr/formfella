"use client";
import { CircleAlert } from 'lucide-react';
import React, { useEffect, useState } from 'react'

const page = () => {
    // redirect to dashboard
    const [time, setTime] = useState(5);
    useEffect(() => {
        const timer = setInterval(() => {
            setTime(time - 1);
        }, 1000);
        return () => clearInterval(timer);
    }, [time]);
    if (time === 0) {
        window.location.href = "/dashboard/pricing";
    }
  return (
    <div className='py-24 px-4'>
    <div className='container mx-auto max-w-4xl'>
        <div className='text-center space-y-8'>
            <h1 className='text-4xl md:text-4xl lg:text-4xl font-bold tracking-tigh bg-gradient-to-b from-rose-500 to-rose-800 text-transparent bg-clip-text'>
                <CircleAlert className='w-12 h-12 inline mr-2 text-red-500' />Payment Failed
            </h1>
            <p className='text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed'>
                Your payment failed. Please try again.
            </p>
            <p className='text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed'>
                Redirecting to pricing page in {time} seconds...
            </p>
        </div>
    </div>
</div>
  )
}

export default page