import React, { useEffect, useRef } from "react";
import { X } from "lucide-react";
import Button from "./button";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export default function Modal({ isOpen, onClose, title, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLElement | null>(null);

  // Handle Escape key and focus trapping
  useEffect(() => {
    if (!isOpen) return;

    // Store the element that triggered the modal
    triggerRef.current = document.activeElement as HTMLElement;

    // Focus the modal
    modalRef.current?.focus();

    // Handle Escape key
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    // Trap focus within the modal
    const focusableElements = modalRef.current?.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements?.[0] as HTMLElement;
    const lastElement = focusableElements?.[focusableElements.length - 1] as HTMLElement;

    const handleTab = (event: KeyboardEvent) => {
      if (event.key === "Tab") {
        if (event.shiftKey && document.activeElement === firstElement) {
          event.preventDefault();
          lastElement?.focus();
        } else if (!event.shiftKey && document.activeElement === lastElement) {
          event.preventDefault();
          firstElement?.focus();
        }
      }
    };

    document.addEventListener("keydown", handleTab);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("keydown", handleTab);
      // Restore focus to the trigger element
      triggerRef.current?.focus();
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

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
          <h2
            className="text-2xl font-bold text-white"
            style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
          >
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
        <div
          className="text-zinc-400"
          style={{ fontFamily: "'Creati Display', sans-serif" }}
        >
          {children}
        </div>
        <div className="mt-6 flex justify-end gap-2">
          <Button
            onClick={onClose}
            className="border-zinc-600 text-zinc-300 hover:bg-zinc-700 hover:text-white hover:border-zinc-500"
            aria-label="Cancel and close modal"
          >
            Cancel
          </Button>
          <Button
            className="bg-[#87efff] border-[#87efff] text-zinc-900 hover:bg-[#6fe2f6] hover:border-[#6fe2f6]"
            aria-label="Confirm action"
          >
            Confirm
          </Button>
        </div>
      </div>
    </div>
  );
}