import { ImageIcon } from "lucide-react";

interface ImagePlaceholderProps {
  className?: string;
  aspectRatio?: "video" | "square" | "wide" | "hero";
}

const ImagePlaceholder = ({ className = "", aspectRatio = "video" }: ImagePlaceholderProps) => {
  const aspectClasses = {
    video: "aspect-video",
    square: "aspect-square",
    wide: "aspect-[21/9]",
    hero: "aspect-[16/7]",
  };

  return (
    <div
      className={`${aspectClasses[aspectRatio]} w-full rounded-xl bg-gradient-to-br from-muted to-muted/60 flex flex-col items-center justify-center gap-3 border border-border ${className}`}
    >
      <ImageIcon className="w-10 h-10 text-muted-foreground/50" />
      <span className="text-sm text-muted-foreground font-medium">תמונה להחלפה</span>
    </div>
  );
};

export default ImagePlaceholder;
