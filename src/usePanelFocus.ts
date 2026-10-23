import { useEffect, useRef } from 'react'

const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

export function usePanelFocus<T extends HTMLElement>(onClose: () => void, trapFocus = false) {
  const panelRef = useRef<T | null>(null)
  const onCloseRef = useRef(onClose)

  useEffect(() => {
    onCloseRef.current = onClose
  }, [onClose])

  useEffect(() => {
    const panel = panelRef.current
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null
    if (!panel) return

    const appRoot = document.getElementById('root')
    const previousInert = appRoot?.inert ?? false
    const previousOverflow = document.body.style.overflow
    if (trapFocus && appRoot) {
      appRoot.inert = true
      document.body.style.overflow = 'hidden'
    }

    // The dialog itself takes focus so screen readers announce its title; Tab moves into its controls.
    panel.focus()
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault()
        onCloseRef.current()
        return
      }
      if (!trapFocus || event.key !== 'Tab') return

      const focusable = Array.from(panel.querySelectorAll<HTMLElement>(FOCUSABLE))
      if (!focusable.length) {
        event.preventDefault()
        panel.focus()
        return
      }
      const first = focusable[0]
      const last = focusable.at(-1)!
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }

    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      if (trapFocus && appRoot) {
        appRoot.inert = previousInert
        document.body.style.overflow = previousOverflow
      }
      previous?.focus()
    }
  }, [trapFocus])

  return panelRef
}
