// src/components/ui/Input.tsx
// This is your new reusable UI Input component.

import React from 'react';

// Define the props for the Input component.
// It accepts all standard HTML input attributes, allowing you to use it for various types (text, email, password, number, etc.).
// An optional 'className' prop is included for any necessary style overrides.
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  className?: string;
}

export default function Input({ className = '', ...props }: InputProps) {
  // Base classes for the input styling, designed for a dark theme.
  const baseClasses = `
    w-full px-4 py-3 rounded-lg 
    bg-zinc-800 border-2 border-zinc-700 text-white placeholder-zinc-500
    focus:outline-none focus:border-[#87efff] focus:ring-2 focus:ring-[#87efff]/50
    transition-all duration-300 ease-in-out
    disabled:opacity-50 disabled:cursor-not-allowed
  `;

  return (
    // Combine the base classes with any additional classes passed via props.
    <input className={`${baseClasses} ${className}`} {...props} />
  );
}
