import React from 'react'
import { cn } from '../../utils/cn'

interface EnterpriseCardProps {
  title?: string
  subtitle?: string
  children: React.ReactNode
  actions?: React.ReactNode
  className?: string
  padding?: 'sm' | 'md' | 'lg'
  bordered?: boolean
}

const EnterpriseCard: React.FC<EnterpriseCardProps> = ({
  title,
  subtitle,
  children,
  actions,
  className,
  padding = 'md',
  bordered = true
}) => {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  }
  
  const baseClasses = 'bg-white rounded-lg shadow-sm'
  const borderClasses = bordered ? 'border border-gray-200' : ''
  
  return (
    <div className={cn(baseClasses, borderClasses, className)}>
      {(title || subtitle) && (
        <div className="border-b border-gray-200 pb-4 mb-4">
          {title && (
            <h3 className="text-lg font-semibold text-gray-900">
              {title}
            </h3>
          )}
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">
              {subtitle}
            </p>
          )}
        </div>
      )}
      
      <div className={paddingClasses[padding]}>
        {children}
      </div>
      
      {actions && (
        <div className="border-t border-gray-200 pt-4 mt-4">
          {actions}
        </div>
      )}
    </div>
  )
}

export default EnterpriseCard
