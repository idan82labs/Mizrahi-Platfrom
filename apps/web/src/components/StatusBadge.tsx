import { CheckCircle2, Clock, FileText } from "lucide-react";

interface StatusBadgeProps {
  status: "active" | "development" | "specification";
}

const StatusBadge = ({ status }: StatusBadgeProps) => {
  if (status === "active") {
    return (
      <span className="status-active">
        <CheckCircle2 className="w-4 h-4" />
        פעיל
      </span>
    );
  }

  if (status === "specification") {
    return (
      <span className="status-specification">
        <FileText className="w-4 h-4" />
        באיפיון
      </span>
    );
  }

  return (
    <span className="status-development">
      <Clock className="w-4 h-4" />
      בפיתוח
    </span>
  );
};

export default StatusBadge;
