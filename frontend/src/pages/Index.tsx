import TopBar from "@/components/TopBar";
import Footer from "@/components/Footer";
import ToolCard from "@/components/ToolCard";
import { RefreshCw, FileCheck, CheckCircle, Lock, ChevronDown, Target, FileText, Clock } from "lucide-react";
const tools = [{
  title: "בקרה אוטומטית על דוח חודשי",
  description: "איתור חריגות ואימות שלמות נתונים לדוח החודשי.",
  supportingText: "מדגיש חריגות מרכזיות ומרכז ממצאים לבדיקה.",
  status: "active" as const,
  schedule: "ריצה אוטומטית: בכל 5 לחודש ב-09:00",
  link: "/tool-monthly"
}, {
  title: "בקרה אוטומטית על דוח עסקאות מתואמות ועסקאות מחוץ לבורסה",
  description: "זיהוי התאמות, כפילויות ופערים בין מקורות.",
  supportingText: "מאחד תמונת מצב ומסמן פערים בין מקורות.",
  status: "development" as const,
  schedule: "ריצה אוטומטית: לא פעיל",
  link: "/tool-matched",
  manualRunAvailable: false,
  isAccessible: true
}, {
  title: "בדיקת דוח כספי אוטומטית",
  description: "בקרה על עקביות בין תקופות ודגלים אדומים.",
  supportingText: "בקרות עומק חשבונאיות ודגלים אדומים.",
  status: "specification" as const,
  note: "יפותח במהלך Q1 2026",
  link: "/tool-financial"
}, {
  title: "אוטומציית בדיקת דמי ניהול משתנים",
  description: "אוטומציה לריכוז נתוני מדדים וקרנות ממספר מקורות והפקת דוח אקסל יומי מובנה.",
  supportingText: "",
  status: "specification" as const,
  note: "יפותח במהלך Q1 2026",
  link: "/tool-financial"
}, {
  title: "אוטומציית דוח גילוי נאות ק.303",
  description: "אוטומציה לניתוח דוח גילוי נאות והפקת דוח אקסל יומי מובנה.",
  supportingText: "",
  status: "specification" as const,
  note: "יפותח במהלך Q1 2026",
  link: "/tool-financial"
}];
const Index = () => {
  return <div className="min-h-screen flex flex-col bg-background">
      <TopBar />
      
      <main className="flex-1 flex flex-col">
        {/* Hero Section - Mobile: ~80% viewport height, centered content */}
        <section className="relative min-h-[80vh] md:min-h-0 md:py-16 lg:py-24 overflow-hidden flex items-center md:block">
          {/* Background Pattern */}
          <div className="absolute inset-0 -z-10">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5" />
            <div className="absolute top-0 left-0 w-96 h-96 bg-primary/10 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2" />
            <div className="absolute bottom-0 right-0 w-96 h-96 bg-secondary/10 rounded-full blur-3xl translate-x-1/2 translate-y-1/2" />
          </div>

          <div className="container mx-auto px-6 md:px-8 lg:px-12 py-8 md:py-0">
            <div className="max-w-4xl mx-auto text-center">
              {/* H1 - Mobile: larger, dominant, 2 lines max */}
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-6 md:mb-6 animate-slide-up leading-relaxed md:leading-snug tracking-tight">
                פורטל כלי בקרה חכמים של חברת הנאמנות
              </h1>
              
              {/* Desktop subtitle */}
              <p className="hidden md:block text-base lg:text-lg text-muted-foreground mb-10 animate-slide-up leading-relaxed max-w-2xl mx-auto" style={{
              animationDelay: "0.1s"
            }}>
                מערכת בדיקות אוטומטיות שמאתרת חריגות, מאמתת שלמות נתונים ומפיקה ממצאים ברורים לבדיקה מהירה - לצורך הגדלת דיוקים ומניעת עבודה ידנית
              </p>
              
              {/* Mobile subtitle - shortened, prominent */}
              <p className="md:hidden text-base text-muted-foreground mb-6 animate-slide-up leading-loose" style={{
              animationDelay: "0.1s"
            }}>
                מערכת בדיקות אוטומטיות לאיתור חריגות ולשיפור דיוק הבקרה
              </p>
              
              {/* Value line - Hidden on mobile, visible on desktop */}
              
              
              {/* Chips - Desktop only, hidden on mobile */}
              <div className="hidden md:flex md:flex-wrap md:items-center md:justify-center md:gap-4 animate-slide-up" style={{
              animationDelay: "0.2s"
            }}>
                <span className="chip flex items-center gap-2 py-2.5 px-4">
                  <RefreshCw className="w-4 h-4 text-primary" />
                  ריצה אוטומטית
                </span>
                <span className="chip flex items-center gap-2 py-2.5 px-4">
                  <FileCheck className="w-4 h-4 text-primary" />
                  תיעוד ממצאים והחרגות
                </span>
                <span className="chip flex items-center gap-2 py-2.5 px-4">
                  <CheckCircle className="w-4 h-4 text-primary" />
                  בדיקות עקביות ושלמות
                </span>
                <span className="chip flex items-center gap-2 py-2.5 px-4">
                  <Lock className="w-4 h-4 text-primary" />
                  ללא התחברות - שימוש פנימי
                </span>
              </div>

              {/* Summary Card - Mobile: generous spacing and padding */}
              <div className="mt-8 md:mt-12 animate-slide-up" style={{
              animationDelay: "0.25s"
            }}>
                {/* Mobile card - spacious */}
                <div className="md:hidden bg-card/90 border border-border/40 rounded-xl p-5 text-right max-w-sm mx-auto shadow-sm">
                  <div className="space-y-4 text-sm text-muted-foreground leading-relaxed">
                    <div className="flex items-center gap-3">
                      <Target className="w-4 h-4 text-primary flex-shrink-0" />
                      <span><strong className="text-foreground">מטרה:</strong> שיפור איכות ויעילות הבקרה</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <FileText className="w-4 h-4 text-primary flex-shrink-0" />
                      <span><strong className="text-foreground">כלים פעילים:</strong> דוח חודשי + עסקאות מתואמות</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Clock className="w-4 h-4 text-primary flex-shrink-0" />
                      <span><strong className="text-foreground">אוטומציה:</strong> ​ה-5 לכל חודש בשעות הבוקר    </span>
                    </div>
                  </div>
                </div>
                
                {/* Desktop full card */}
                <div className="hidden md:block bg-card/80 border border-border/50 rounded-2xl p-6 lg:p-8 text-right max-w-xl mx-auto shadow-sm">
                  <div className="space-y-5 text-sm lg:text-base text-muted-foreground">
                    <div className="flex items-center gap-4">
                      <Target className="w-5 h-5 text-primary flex-shrink-0" />
                      <span><strong className="text-foreground">מטרת המערכת:</strong> שיפור איכות ותהליך הבקרה על דוחות</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <FileText className="w-5 h-5 text-primary flex-shrink-0" />
                      <span><strong className="text-foreground">כיסוי נוכחי:</strong> דוח חודשי + עסקאות מתואמות / מחוץ לבורסה</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <Clock className="w-5 h-5 text-primary flex-shrink-0" />
                      <span><strong className="text-foreground">אוטומציה:</strong> ריצה ב-5 לחודש (09:00, 10:00)</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* CTA - Mobile: prominent, generous spacing */}
              <div className="mt-10 md:mt-12 animate-slide-up" style={{
              animationDelay: "0.3s"
            }}>
                {/* Mobile: Primary CTA - tap-comfortable */}
                <button onClick={() => {
                const toolsSection = document.getElementById('tools-section');
                if (toolsSection) {
                  toolsSection.scrollIntoView({
                    behavior: 'smooth'
                  });
                }
              }} className="md:hidden btn-primary inline-flex items-center gap-2 text-base py-4 px-8 w-full max-w-xs justify-center shadow-lg rounded-2xl">
                  <span>לכלים הפעילים</span>
                  <ChevronDown className="w-5 h-5" />
                </button>
                
                {/* Desktop: Outline CTA */}
                <button onClick={() => {
                const toolsSection = document.getElementById('tools-section');
                if (toolsSection) {
                  toolsSection.scrollIntoView({
                    behavior: 'smooth'
                  });
                }
              }} className="hidden md:inline-flex btn-outline items-center gap-2 text-sm">
                  <span>לכל הכלים </span>
                  <ChevronDown className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Tools Grid - Mobile: clear visual break */}
        <section id="tools-section" className="flex-1 pt-12 pb-6 md:py-16 lg:py-20 border-t border-border/30 md:border-0">
          <div className="container mx-auto px-6 md:px-8 lg:px-12">
            <h3 className="text-lg md:text-xl lg:text-2xl font-semibold text-foreground mb-6 md:mb-10 text-right max-w-6xl mx-auto">
              בחרו את סוג הדוח לבדיקה
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-8 max-w-6xl mx-auto">
              {tools.map((tool, index) => <div key={index} className="animate-slide-up" style={{
              animationDelay: `${0.3 + index * 0.1}s`
            }}>
                  <ToolCard {...tool} />
                </div>)}
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>;
};
export default Index;