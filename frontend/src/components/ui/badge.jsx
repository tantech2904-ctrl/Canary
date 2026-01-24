import React from 'react'
import { cn } from './cn'

export function Badge({ className, variant = 'default', ...props }) {
  const variants = {
    default: 'bg-slate-100 text-slate-800',
    danger: 'bg-rose-100 text-rose-800',
    warning: 'bg-amber-100 text-amber-900',
    success: 'bg-emerald-100 text-emerald-900',
  }

  return (
    <span
      className={cn('inline-flex items-center rounded-full px-2 py-1 text-xs font-medium', variants[variant], className)}
      {...props}
    />
  )
}
