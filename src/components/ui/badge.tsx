import React from 'react';

export function Badge({ children, className = '', ...props }: React.HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={`inline-block text-xs font-semibold rounded-full px-3 py-1 ${className}`}
      {...props}
    >
      {children}
    </span>
  );
}
