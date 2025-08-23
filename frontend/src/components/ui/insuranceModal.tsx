"use client"

import type React from "react"
import { useEffect, useRef } from "react"
import { X } from "lucide-react"
import Button from "./button"

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
}

export default function InsuranceModal({ isOpen, onClose, title, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<HTMLElement | null>(null)

  // Handle Escape key and focus trapping
  useEffect(() => {
    if (!isOpen) return

    // Store the element that triggered the modal
    triggerRef.current = document.activeElement as HTMLElement

    // Focus modal container only if focus is outside
    if (!modalRef.current?.contains(document.activeElement)) {
      modalRef.current?.focus()
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose()
      }
    }

    document.addEventListener("keydown", handleKeyDown)

    // Trap focus
    const focusableElements = modalRef.current?.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    )
    const firstElement = focusableElements?.[0] as HTMLElement
    const lastElement = focusableElements?.[focusableElements.length - 1] as HTMLElement

    const handleTab = (event: KeyboardEvent) => {
      if (event.key === "Tab" && focusableElements?.length) {
        const firstElement = focusableElements[0] as HTMLElement
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

        if (event.shiftKey && document.activeElement === firstElement) {
          event.preventDefault()
          lastElement?.focus()
        } else if (!event.shiftKey && document.activeElement === lastElement) {
          event.preventDefault()
          firstElement?.focus()
        }
      }
    }

    document.addEventListener("keydown", handleTab)

    return () => {
      document.removeEventListener("keydown", handleKeyDown)
      document.removeEventListener("keydown", handleTab)
      triggerRef.current?.focus() // restore focus
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={`${title} modal`}
    >
      <div
        className="w-full max-w-md bg-zinc-900 rounded-lg shadow-xl p-6 mx-4"
        onClick={(e) => e.stopPropagation()}
        ref={modalRef}
        tabIndex={-1}
      >
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-white" style={{ fontFamily: "'Creati Display Bold', sans-serif" }}>
            {title}
          </h2>
          <Button
            onClick={onClose}
            className="p-1 text-zinc-400 hover:text-white hover:bg-zinc-700 rounded-full"
            aria-label="Close modal"
          >
            <X size={20} />
          </Button>
        </div>
        <div className="text-zinc-400" style={{ fontFamily: "'Creati Display', sans-serif" }}>
          {children}
        </div>
      </div>
    </div>
  )
}
