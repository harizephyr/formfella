"use client";
import React from 'react'
import { useEffect } from 'react'

const Success = () => {

    // redirect to dashboard in 5 seconds
    useEffect(() => {
       checkSession();
    }, []);
    const checkSession = async () => {
        try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/checkout/session/${document.cookie.split('; ')
          .find(row => row.startsWith('payment_session_id='))
          ?.split('=')[1]}`, {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${document.cookie.split('; ')
            .find(row => row.startsWith('access_token='))
            ?.split('=')[1]}`,
            "Content-Type": "application/json",
          },
        });
        // console.log(response);
        const data = await response.json();
        if (data.payment_status === "paid") {
            window.location.href = "/dashboard";
        }
      } catch (error) {
        console.log(error);
      }
      }
  return (
    <>
    {/* Success Section */}
    <div className='py-24 px-4'>
        <div className='container mx-auto max-w-4xl'>
            <div className='text-center space-y-8'>
                <h1 className='text-4xl md:text-6xl lg:text-7xl font-bold tracking-tigh bg-gradient-to-r from-purple-500 to-blue-500 text-transparent bg-clip-text'>
                    Success
                </h1>
                <p className='text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed'>
                    Your payment was successful. Thank you for your purchase.
                </p>
            </div>
        </div>
    </div>
    </>
  )
}
  
export default Success