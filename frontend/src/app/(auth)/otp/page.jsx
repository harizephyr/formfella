"use client"

import { useState, useRef, Suspense } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useSearchParams } from 'next/navigation'
import { toast } from "sonner"

export default function OtpScreen() {
  const [otp, setOtp] = useState(Array(6).fill(""))
  const inputRefs = useRef([])
  const searchParams = useSearchParams()
  const email = searchParams.get('email')
  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  const handleChange = (value, index) => {
    if (/^[0-9]$/.test(value)) {
      const newOtp = [...otp]
      newOtp[index] = value
      setOtp(newOtp)

      // Move to next input
      if (index < 5) inputRefs.current[index + 1]?.focus()
    }
  }

  const handleKeyDown = (e, index) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      const newOtp = [...otp]
      newOtp[index - 1] = ""
      setOtp(newOtp)
      inputRefs.current[index - 1]?.focus()
    }
  }

  const handleVerify = async() => {
    const response = await fetch(`${API_URL}/api/v1/confirm-sign-up`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username: email, confirmation_code: otp.join("") }),
    })
    const data = await response.json()
    console.log(data)
    if (data.success) {
      toast.success("OTP verified successfully")
      setTimeout(() => {
        window.location.href = "/login"
      }, 3000)
    }else {
      toast.error(data.error)
    }
  }

  return (
    <Suspense fallback={<div>Loading...</div>}>
    <div className="flex flex-col items-center justify-center min-h-screen gap-6">
      <h1 className="text-2xl font-semibold">Enter OTP</h1>
      <div className="flex gap-3">
        {otp.map((digit, index) => (
          <Input
            key={index}
            type="text"
            inputMode="numeric"
            maxLength={1}
            value={digit}
            onChange={(e) => handleChange(e.target.value, index)}
            onKeyDown={(e) => handleKeyDown(e, index)}
            ref={(el) => (inputRefs.current[index] = el)}
            className="w-12 h-12 text-center text-xl"
          />
        ))}
      </div>
      <Button onClick={handleVerify} className="w-40">Verify</Button>
    </div>
    </Suspense>
  )
}
