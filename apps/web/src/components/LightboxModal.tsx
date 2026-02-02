import { useEffect } from "react";
import { X } from "lucide-react";

interface LightboxModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  imageSrc?: string;
}

const LightboxModal = ({ isOpen, onClose, title, imageSrc }: LightboxModalProps) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }

    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="modal-overlay animate-fade-in"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-label={title}
    >
      <div className="relative max-w-4xl w-full mx-4 animate-scale-in">
        <button
          onClick={onClose}
          className="absolute -top-12 left-0 p-2 rounded-lg bg-card/80 hover:bg-card transition-colors"
          aria-label="סגור"
        >
          <X className="w-6 h-6 text-foreground" />
        </button>
        
        <div className="bg-card rounded-2xl overflow-hidden shadow-modal">
          <div className="p-4 border-b border-border">
            <h3 className="font-semibold text-foreground">{title}</h3>
          </div>
          <div className="p-4">
            {imageSrc ? (
              <img src={imageSrc} alt={title} className="w-full rounded-lg" />
            ) : (
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center text-muted-foreground">
                אין תמונה
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LightboxModal;
