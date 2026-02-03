import { Link } from "react-router-dom";
import { ArrowLeft, Calendar, Play } from "lucide-react";
import StatusBadge from "./StatusBadge";

interface ToolCardProps {
  title: string;
  description: string;
  supportingText?: string;
  status: "active" | "development" | "specification";
  schedule?: string;
  note?: string;
  link: string;
  manualRunAvailable?: boolean;
  isAccessible?: boolean;
}

const ToolCard = ({ title, description, supportingText, status, schedule, note, link, manualRunAvailable = true, isAccessible }: ToolCardProps) => {
  const isNotReady = status === "development" || status === "specification";
  const isToolAccessible = isAccessible ?? !isNotReady;

  return (
    <div
      className={`card-portal flex flex-col h-full ${
        isNotReady && !isToolAccessible ? "opacity-60 grayscale-[30%]" : ""
      }`}
    >
      <div className="flex-1">
        {/* Status badge - anchored at top on mobile */}
        <div className="flex items-start justify-between gap-4 mb-3 md:mb-4">
          <h3 className="text-base md:text-lg font-semibold text-foreground leading-tight">{title}</h3>
          <StatusBadge status={status} />
        </div>
        
        <p className="text-muted-foreground text-xs md:text-sm mb-2 leading-relaxed">
          {description}
        </p>

        {supportingText && (
          <p className={`text-xs md:text-sm mb-3 md:mb-4 leading-relaxed ${isNotReady ? "text-muted-foreground/70" : "text-muted-foreground"}`}>
            {supportingText}
          </p>
        )}

        {schedule && (
          <div className="flex items-center gap-2 text-xs md:text-sm text-muted-foreground mb-3 md:mb-4">
            <Calendar className="w-3.5 md:w-4 h-3.5 md:h-4 flex-shrink-0" />
            <span>{schedule}</span>
          </div>
        )}

        {note && (
          <p className={`text-xs md:text-sm font-medium mb-3 md:mb-4 ${status === "specification" ? "text-destructive" : "text-primary"}`}>{note}</p>
        )}
        
        {/* Mobile-only manual run indicator */}
        {isToolAccessible && (
          <div className="md:hidden flex items-center gap-1.5 text-xs text-muted-foreground mb-3">
            <Play className={`w-3 h-3 ${manualRunAvailable ? 'text-primary' : 'text-muted-foreground'}`} />
            <span>{manualRunAvailable ? 'הרצה ידנית זמינה' : 'הרצה ידנית לא זמינה'}</span>
          </div>
        )}
      </div>

      {!isToolAccessible ? (
        <div className="inline-flex items-center justify-center gap-2 btn-outline w-full mt-auto opacity-50 cursor-not-allowed pointer-events-none text-sm">
          <span>לא זמין</span>
        </div>
      ) : (
        <Link
          to={link}
          className="inline-flex items-center justify-center gap-2 btn-primary w-full mt-auto text-sm"
        >
          <span>כניסה לכלי</span>
          <ArrowLeft className="w-4 h-4" />
        </Link>
      )}
    </div>
  );
};

export default ToolCard;
