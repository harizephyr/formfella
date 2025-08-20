import React from 'react'
import Link from 'next/link'
import { FileText, Pen } from 'lucide-react'
import { Edu_NSW_ACT_Cursive,Merienda } from "next/font/google";

const eduNSWACTCursive = Edu_NSW_ACT_Cursive({ subsets: ["latin"], weight: ["400", "700"] });
const merienda = Merienda({ subsets: ["latin"], weight: ["400", "700"] });

const Logo = () => {
  return (
    <Link href="/" className="flex items-center gap-2 font-bold text-3xl">
            {/* <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
              <Pen className="w-5 h-5 text-white" />
            </div> */}
            <span className={`bg-gradient-to-r from-blue-500 via-blue-200 to-purple-500 bg-clip-text text-transparent ${merienda.className}`}>FormFella</span>
          </Link>
  )
}

export default Logo;