// src/components/ui/Card.tsx
// This is your new reusable UI Card component.

import React from 'react';

// Define the props for the Card component.
// It accepts standard div attributes, children to render inside the card,
// and an optional 'className' for custom styling.
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
}

export default function Card({ children, className = '', ...props }: CardProps) {
  // Base classes for the card styling.
  // It uses a semi-transparent, slightly lighter background than the main theme
  // with a subtle border to create a clean, modern container.
  const baseClasses = `
    bg-zinc-800/50 border border-zinc-700 
    rounded-2xl p-6
    transition-all duration-300 ease-in-out
  `;

  return (
    // Combine the base classes with any additional classes passed via props.
    <div className={`${baseClasses} ${className}`} {...props}>
      {children}
    </div>
  );
}
