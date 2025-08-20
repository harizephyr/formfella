"use client"

import { Suspense } from 'react'
import OtpForm from '@/components/otp-form'

export default function OtpPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <OtpForm />
    </Suspense>
  )
}