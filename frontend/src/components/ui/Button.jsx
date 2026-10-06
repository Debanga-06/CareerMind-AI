import { forwardRef } from 'react'
import { Link } from 'react-router-dom'

const VARIANTS = {
  primary:
    'bg-ink text-white hover:bg-[#182337] active:bg-[#0B1220] shadow-sm',
  accent:
    'bg-signal-500 text-white hover:bg-signal-600 active:bg-signal-700 shadow-sm',
  outline:
    'border border-line bg-white text-ink hover:border-ink/30 hover:bg-paper',
  ghost: 'text-ink hover:bg-ink/5',
}

const SIZES = {
  sm: 'h-9 px-3.5 text-sm gap-1.5',
  md: 'h-11 px-5 text-sm gap-2',
  lg: 'h-13 px-7 text-base gap-2.5',
}

/**
 * Button. Renders a <Link> when `to` is passed, an <a> when `href` is
 * passed, otherwise a native <button>.
 */
const Button = forwardRef(function Button(
  { variant = 'primary', size = 'md', to, href, className = '', children, icon: Icon, iconPosition = 'left', ...rest },
  ref
) {
  const classes = `inline-flex items-center justify-center rounded-full font-medium transition-colors duration-150 disabled:opacity-50 disabled:pointer-events-none ${VARIANTS[variant]} ${SIZES[size]} ${className}`

  const content = (
    <>
      {Icon && iconPosition === 'left' && <Icon className="h-4 w-4 shrink-0" strokeWidth={2.25} />}
      {children}
      {Icon && iconPosition === 'right' && <Icon className="h-4 w-4 shrink-0" strokeWidth={2.25} />}
    </>
  )

  if (to) {
    return (
      <Link ref={ref} to={to} className={classes} {...rest}>
        {content}
      </Link>
    )
  }

  if (href) {
    return (
      <a ref={ref} href={href} className={classes} {...rest}>
        {content}
      </a>
    )
  }

  return (
    <button ref={ref} className={classes} {...rest}>
      {content}
    </button>
  )
})

export default Button
