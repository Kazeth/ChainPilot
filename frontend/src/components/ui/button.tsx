// src/components/ui/Button.tsx
// This is your reusable UI Button component.

import React from 'react';

// Define the props for the Button component.
// It accepts all standard HTML button attributes, so you can pass props like 'onClick', 'type', 'disabled', etc.
// It also accepts an optional 'className' prop to allow for additional custom styling.
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  className?: string;
}

export default function Button({ children, className = '', ...props }: ButtonProps) {
  // Base classes for the button styling
  const baseClasses = `
    px-6 py-2.5 rounded-lg font-semibold text-sm
    border-2 border-white text-white bg-transparent
    hover:bg-[#87efff] hover:text-zinc-900 hover:border-[#87efff]
    focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-zinc-900 focus:ring-[#87efff]
    transition-all duration-300 ease-in-out
    disabled:opacity-50 disabled:cursor-not-allowed
  `;

  return (
    // Combine the base classes with any additional classes passed via props
    <button className={`${baseClasses} ${className}`} {...props}>
      {children}
    </button>
  );
}