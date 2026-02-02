import { ExternalLink } from "lucide-react";

const Footer = () => {
  return (
    <footer className="py-6 border-t border-border bg-card/50">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex flex-col md:flex-row items-center justify-center gap-2 text-sm text-muted-foreground">
          <span>פותח על ידי</span>
          <a
            href="https://82labs.io"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 font-semibold text-primary hover:underline transition-colors"
          >
            82Labs
            <ExternalLink className="w-3 h-3" />
          </a>
          <span className="hidden md:inline mx-2">|</span>
          <span>כל הזכויות שמורות</span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
