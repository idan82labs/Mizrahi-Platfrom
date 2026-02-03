import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, MessageCircle, Calendar, ZoomIn, CheckCircle2, Clock } from "lucide-react";
import TopBar from "@/components/TopBar";
import Footer from "@/components/Footer";
import StatusBadge from "@/components/StatusBadge";
import CheckTable from "@/components/CheckTable";
import LightboxModal from "@/components/LightboxModal";
import ImagePlaceholder from "@/components/ImagePlaceholder";

const checkItems = [
  {
    check: "עקביות בין תקופות",
    importance: "וידוא רציפות הנתונים",
    output: "תקין / אי-עקביות",
    notes: "השוואה רבעונית ושנתית",
  },
  {
    check: "בדיקת יתרות פתיחה",
    importance: "התאמה ליתרות סגירה קודמות",
    output: "פערים ביתרות",
    notes: "לכל סעיף בנפרד",
  },
  {
    check: "אימות סיכומים",
    importance: "נכונות חישובי סיכום",
    output: "סטיות בסיכומים",
    notes: "סכ״ה סעיפים ראשיים",
  },
  {
    check: "בדיקת סימנים",
    importance: "התאמת סימני חובה/זכות",
    output: "שגיאות סימנים",
    notes: "לפי סוג סעיף",
  },
  {
    check: "זיהוי דגלים אדומים",
    importance: "התראה על ערכים חריגים",
    output: "רשימת דגלים",
    notes: "לפי כללי סף",
  },
  {
    check: "בדיקת יחסים פיננסיים",
    importance: "עקביות יחסים עיקריים",
    output: "חריגות ביחסים",
    notes: "נזילות, מינוף, רווחיות",
  },
  {
    check: "אימות אחוזים",
    importance: "נכונות חישובי אחוזים",
    output: "שגיאות באחוזים",
    notes: "אחוז מסה״כ נכסים/התחייבויות",
  },
  {
    check: "השוואה לתקציב",
    importance: "מעקב ביצוע תקציבי",
    output: "סטיות מתקציב",
    notes: "אחוז סטייה לסעיף",
  },
  {
    check: "בדיקת עיגולים",
    importance: "עקביות בעיגול מספרים",
    output: "שגיאות עיגול",
    notes: "אלפי ש״ח / יחידות",
  },
  {
    check: "אימות הערות",
    importance: "שלמות הביאורים",
    output: "הערות חסרות",
    notes: "לפי דרישות רגולטוריות",
  },
];

const ToolFinancial = () => {
  const [isLightboxOpen, setIsLightboxOpen] = useState(false);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <TopBar />
      
      <main className="flex-1 py-8 md:py-12 animate-fade-in">
        <div className="container mx-auto px-4 md:px-6 max-w-5xl">
          {/* Back Link */}
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-6"
          >
            <ArrowRight className="w-4 h-4" />
            חזרה לפורטל
          </Link>

          {/* Header */}
          <div className="mb-8">
            <div className="flex flex-wrap items-center gap-4 mb-4">
              <h1 className="text-2xl md:text-3xl font-bold text-foreground">
                בדיקת דוח כספי אוטומטית
              </h1>
              <StatusBadge status="specification" />
            </div>
            <p className="text-lg text-muted-foreground mb-4">
              בקרה על עקביות בין תקופות ודגלים אדומים.
            </p>
            <div className="flex items-center gap-2 text-sm text-primary font-medium">
              <Clock className="w-4 h-4" />
              <span>יפותח במהלך Q1 2026</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-4 mb-10">
            <button
              disabled
              className="btn-disabled flex items-center gap-2 cursor-not-allowed"
            >
              לא זמין כרגע
            </button>
            <a
              href="https://tally.so/r/7RLvea"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-outline flex items-center gap-2"
            >
              <MessageCircle className="w-4 h-4" />
              דיווח תקלה / שאלה
            </a>
          </div>

          {/* Summary */}
          <section className="mb-10">
            <h2 className="text-xl font-semibold text-foreground mb-4">סקירה כללית</h2>
            <div className="card-portal">
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-muted-foreground flex-shrink-0 mt-0.5" />
                  <span className="text-muted-foreground">בדיקת עקביות אוטומטית בין תקופות דיווח</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-muted-foreground flex-shrink-0 mt-0.5" />
                  <span className="text-muted-foreground">זיהוי דגלים אדומים ואזהרות מבוססות כללים</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-muted-foreground flex-shrink-0 mt-0.5" />
                  <span className="text-muted-foreground">אימות יחסים פיננסיים ומגמות</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-muted-foreground flex-shrink-0 mt-0.5" />
                  <span className="text-muted-foreground">דוח מפורט עם ממצאים והמלצות</span>
                </li>
              </ul>
            </div>
          </section>

          {/* Check Table */}
          <section className="mb-10">
            <h2 className="text-xl font-semibold text-foreground mb-4">מה נבדק</h2>
            <CheckTable items={checkItems} />
          </section>

          {/* Schedule */}
          <section className="mb-10">
            <h2 className="text-xl font-semibold text-foreground mb-4">זמני ריצה אוטומטיים</h2>
            <div className="card-portal">
              <div className="flex items-center gap-3">
                <Calendar className="w-6 h-6 text-muted-foreground" />
                <div>
                  <p className="font-medium text-muted-foreground">בקרוב לאחר השקה</p>
                  <p className="text-sm text-muted-foreground">זמני הריצה ייקבעו עם השקת הכלי</p>
                </div>
              </div>
            </div>
          </section>

          {/* Sample Report */}
          <section className="mb-10">
            <h2 className="text-xl font-semibold text-foreground mb-4">דוח לדוגמה</h2>
            <div className="card-portal opacity-75">
              <ImagePlaceholder aspectRatio="video" />
              <button
                onClick={() => setIsLightboxOpen(true)}
                className="btn-outline flex items-center gap-2 mt-4"
              >
                <ZoomIn className="w-4 h-4" />
                הגדל
              </button>
            </div>
          </section>

          {/* Manual Run */}
          <section className="mb-10">
            <h2 className="text-xl font-semibold text-foreground mb-4">הפעלה ידנית</h2>
            <div className="card-portal">
              <p className="text-muted-foreground mb-4">
                כלי זה נמצא כרגע בפיתוח ויהיה זמין במהלך Q1 2026. לאחר ההשקה, ניתן יהיה להפעיל את הבדיקה באופן ידני בכל עת.
              </p>
              <button
                disabled
                className="btn-disabled flex items-center gap-2 cursor-not-allowed"
              >
                לא זמין כרגע
              </button>
            </div>
          </section>
        </div>
      </main>

      <Footer />
      
      <LightboxModal
        isOpen={isLightboxOpen}
        onClose={() => setIsLightboxOpen(false)}
        title="דוח כספי לדוגמה"
      />
    </div>
  );
};

export default ToolFinancial;
