import React from 'react'
import { cn } from './cn'

export function Card({ className, ...props }) {
  return <div className={cn('rounded-lg border bg-white p-4 shadow-sm', className)} {...props} />
}
