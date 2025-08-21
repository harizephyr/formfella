"use client";

import { motion } from "framer-motion";
import { ArrowDown, ChevronDown, ChevronLeft } from "lucide-react";
import { useState, useRef } from "react";

export default function ComparisonSlider() {
  const [position, setPosition] = useState(3); // percentage
  const containerRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault(); // Prevent default drag behavior
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    let newPos = (x / rect.width) * 100;
    newPos = Math.max(0, Math.min(100, newPos));
    setPosition(newPos);
  };

  return (
    <section className="py-16 px-4 bg-background/50 relative">
      <div className="container mx-auto max-w-6xl">
        {/* Title */}
        <motion.div
          className="text-center mb-12"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={{
            hidden: { opacity: 0, y: 20 },
            visible: {
              opacity: 1,
              y: 0,
              transition: { duration: 0.6 },
            },
          }}
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-b from-black to-gray-800/80 bg-clip-text text-transparent">
            Transform Your Forms
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            See the difference our solution makes with this interactive comparison
          </p>
        </motion.div>

        {/* ask the user to drag the slider */}
        <motion.div
          className="text-center mb-12"
          initial="hidden"
          whileInView="visible"
          
        >
          <p className="flex gap-2 justify-center items-center text-muted-foreground max-w-2xl mx-auto animate-bounce ">
            <ArrowDown className="w-6 h-6"/>
            Drag the slider to see the difference
          </p>
        </motion.div>

        {/* Slider */}
        <motion.div
          className="relative max-w-4xl mx-auto rounded-xl overflow-hidden shadow-2xl border border-border/50"
          initial={{ opacity: 0, scale: 0.98 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div
            className="relative h-[500px] w-full cursor-ew-resize select-none"
            ref={containerRef}
            onMouseMove={(e) => {
              if (e.buttons === 1) handleDrag(e); // drag only while mouse is pressed
            }}
            onMouseDown={(e) => e.preventDefault()} // Prevent text selection on click down
            onClick={handleDrag}
          >
            {/* Before Image */}
            <div className="absolute inset-0 w-full h-full">
              <div className="absolute left-0 top-0 h-full w-full z-10">
              {position < 10 && <div className="absolute left-8 top-1/2 -translate-y-1/2 z-30">
                <span className="inline-block px-4 py-2 rounded-full bg-background/90 text-foreground text-sm font-medium border border-border shadow-lg backdrop-blur-sm">
                  Before
                </span>
              </div>}
              </div>
              <img
                src="/before.png"
                alt="Before using FormFella"
                className="w-full h-full object-cover"
              />
            </div>

            {/* After Image */}
            <div
              className="absolute inset-0 h-full overflow-hidden"
              style={{ width: `${position}%` }}
            >
             <div className="absolute right-8 top-1/2 -translate-y-1/2 z-30">
  <span className="inline-block px-4 py-2 rounded-full bg-background/90 text-foreground text-sm font-medium border border-border shadow-lg backdrop-blur-sm">
    After
  </span>
</div>
              <img
                src="/after.png"
                alt="After using FormFella"
                className="w-full h-full object-cover"
              />
            </div>

            {/* Slider Control */}
            <div
              className="absolute top-0 bottom-0 w-1 bg-gray-500/80 z-20 shadow-lg"
              style={{ left: `${position}%` }}
            >
              <div className="absolute -left-4 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-gray-500/80 flex items-center justify-center text-white shadow-lg border-2 border-white">
                <div className="flex space-x-0.5">
                  <span className="w-1 h-3 bg-white rounded-full"></span>
                  <span className="w-1 h-3 bg-white rounded-full"></span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
