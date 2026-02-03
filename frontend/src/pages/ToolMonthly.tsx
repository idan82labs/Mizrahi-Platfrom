import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Play, MessageCircle, Calendar, ZoomIn, CheckCircle2 } from "lucide-react";
import TopBar from "@/components/TopBar";
import Footer from "@/components/Footer";
import StatusBadge from "@/components/StatusBadge";
import CheckTable from "@/components/CheckTable";
import LightboxModal from "@/components/LightboxModal";
import monthlyReportExample from "@/assets/monthly-report-example.png";

const checkItems = [
  {
    check: "בדיקת שלמות: הצלבת קרנות",
    importance: "וידוא התאמה בין דוח בנאב לדוח מנהל",
    output: "רשימת חוסרים / תקין",
    notes: "השוואה בין מקורות הנתונים",
  },
  {
    check: "זיהוי נכסים עם שווי קטן או שווה ל־0",
    importance: "איתור נכסים חריגים שעלולים להצביע על בעיה",
    output: "רשימת נכסים חריגים",
    notes: "סינון לפי ערך שווי",
  },
  {
    check: "איתור נכסים חריגים חדשים",
    importance: "מעקב אחר שינויים בתיק הנכסים",
    output: "רשימת נכסים חדשים",
    notes: "השוואה לחודש הקודם",
  },
  {
    check: "שינויים בכמות נכסים חריגים",
    importance: "זיהוי מגמות ושינויים בין חודשים",
    output: "אחוז שינוי / כמות",
    notes: "השוואה לחודש קודם",
  },
  {
    check: "בדיקות עקביות בכמויות נכסים חריגים",
    importance: "וידוא נכונות הנתונים לאורך זמן",
    output: "תקין / חריגות",
    notes: "בדיקת רצף נתונים",
  },
  {
    check: "בדיקת שילובים נדרשים של סוגי נכסים",
    importance: "עמידה בדרישות רגולטוריות",
    output: "תקין / חסר שילוב",
    notes: "כולל סעיף 214",
  },
  {
    check: "בדיקות סבירות מחירים",
    importance: "זיהוי תמחור חריג שעלול להעיד על טעות",
    output: "רשימת חריגות מחיר",
    notes: "סף התראה: 7.5%",
  },
];

const ToolMonthly = () => {
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
                בקרה אוטומטית על דוח חודשי
              </h1>
              <StatusBadge status="active" />
            </div>
            <p className="text-lg text-muted-foreground mb-4">
              בדיקה אוטומטית לאיתור חריגות, חוסרים ואי־עקביות בדוח החודשי של נכסי הנאמנות, לצורך תמיכה בתהליך הבקרה.
            </p>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="w-4 h-4" />
              <span>ריצה אוטומטית: בכל 5 לחודש ב-09:00</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-4 mb-10">
            <a
              href="https://n8n.82labs.io/form/fund-form"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              הפעל בדיקה עכשיו
            </a>
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
                  <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                  <span>ביצוע בדיקה מקיפה ואחידה של הדוח החודשי</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                  <span>זיהוי חריגות וחוסרים בצורה אוטומטית</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                  <span>השוואה בין נתוני חודשים עוקבים לאיתור שינויים</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                  <span>הפקת דוח ממצאים ברור ומובנה לצורך בדיקה מהירה</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                  <span>צמצום עבודה ידנית והפחתת סיכון לטעויות אנוש</span>
                </li>
              </ul>
            </div>
          </section>

          {/* Check Table - Hidden on mobile */}
          <section className="hidden md:block mb-10">
            <h2 className="text-xl font-semibold text-foreground mb-4">מה נבדק</h2>
            <CheckTable items={checkItems} />
          </section>

          {/* Schedule */}
          <section className="mb-10">
            <h2 className="text-xl font-semibold text-foreground mb-4">זמני ריצה אוטומטיים</h2>
            <div className="card-portal space-y-4">
              <div className="flex items-center gap-3">
                <Calendar className="w-6 h-6 text-primary" />
                <div>
                  <p className="font-medium text-foreground">בכל 5 לחודש בשעה 09:00</p>
                  <p className="text-sm text-muted-foreground">הבדיקה מופעלת אוטומטית ושולחת דוח לצוות הבקרה</p>
                </div>
              </div>
              <div className="border-t border-border pt-4 text-sm text-muted-foreground space-y-1">
                <p><span className="font-medium text-foreground">מקור נתונים:</span> מאי"ה</p>
                <p><span className="font-medium text-foreground">פורמט:</span> Excel</p>
                <p><span className="font-medium text-foreground">זמן ריצה משוער:</span> כ-3 דקות</p>
              </div>
            </div>
          </section>

          {/* Sample Report */}
          <section className="mb-10">
            <h2 className="text-xl font-semibold text-foreground mb-4">דוח לדוגמה</h2>
            <div className="card-portal">
              <img
                src={monthlyReportExample}
                alt="דוח חודשי לדוגמה"
                className="w-full rounded-lg border border-border cursor-pointer hover:opacity-90 transition-opacity"
                onClick={() => setIsLightboxOpen(true)}
              />
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
          <section id="run-monthly" className="mb-10">
            <h2 className="text-xl font-semibold text-foreground mb-4">הפעלה ידנית</h2>
            <div className="card-portal">
              <p className="text-muted-foreground mb-4">
                ניתן להפעיל את הבדיקה באופן ידני בכל עת. הבדיקה תרוץ על הנתונים העדכניים ותייצר דוח מיידי.
              </p>
              <a
                href="https://n8n.82labs.io/form/fund-form"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary inline-flex items-center gap-2"
              >
                <Play className="w-4 h-4" />
                הפעל בדיקה עכשיו
              </a>
            </div>
          </section>
        </div>
      </main>

      <Footer />
      
      <LightboxModal
        isOpen={isLightboxOpen}
        onClose={() => setIsLightboxOpen(false)}
        title="דוח חודשי לדוגמה"
        imageSrc={monthlyReportExample}
      />
    </div>
  );
};

export default ToolMonthly;
