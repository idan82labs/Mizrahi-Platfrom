import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Play, MessageCircle, Calendar, ZoomIn, CheckCircle2, Loader2, CheckCircle, XCircle } from "lucide-react";
import TopBar from "@/components/TopBar";
import Footer from "@/components/Footer";
import StatusBadge from "@/components/StatusBadge";
import CheckTable from "@/components/CheckTable";
import LightboxModal from "@/components/LightboxModal";
import matchedReportImage from "@/assets/matched-report-example.png";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const checkItems = [{
  check: "התאמת עסקאות",
  importance: "וידוא שכל עסקה מופיעה בשני המקורות",
  output: "עסקאות מותאמות / לא מותאמות",
  notes: "לפי מזהה עסקה ייחודי"
}, {
  check: "זיהוי כפילויות",
  importance: "מניעת דיווח כפול",
  output: "רשימת כפילויות",
  notes: "בתוך כל מקור בנפרד"
}, {
  check: "פערי סכומים",
  importance: "זיהוי הפרשי כספים",
  output: "סכום הפער",
  notes: "סטייה מותרת: 0.01₪"
}, {
  check: "עסקאות חסרות",
  importance: "זיהוי עסקאות שקיימות רק במקור אחד",
  output: "רשימת חסרים",
  notes: "לפי מקור"
}, {
  check: "בדיקת תאריכים",
  importance: "התאמת תאריכי ביצוע ודיווח",
  output: "פערי תאריכים",
  notes: "התראה על פער מעל יום עסקים"
}, {
  check: "אימות סוג עסקה",
  importance: "התאמת סיווג העסקה בין מקורות",
  output: "אי-התאמות סוג",
  notes: "קנייה/מכירה/המרה"
}, {
  check: "בדיקת מחירים",
  importance: "התאמת מחיר ביצוע",
  output: "פערי מחירים",
  notes: "אחוז סטייה מקסימלי"
}, {
  check: "אימות כמויות",
  importance: "התאמת כמויות ניירות ערך",
  output: "פערי כמויות",
  notes: "יחידות מלאות בלבד"
}, {
  check: "עסקאות מחוץ לבורסה",
  importance: "זיהוי וסיווג OTC",
  output: "רשימת עסקאות OTC",
  notes: "דורש בדיקה ידנית נוספת"
}, {
  check: "סיכום יומי",
  importance: "בקרה על סה״כ יומי",
  output: "סיכום לפי יום",
  notes: "השוואה בין מקורות"
}, {
  check: "בדיקת ברוקר",
  importance: "אימות פרטי ברוקר",
  output: "אי-התאמות ברוקר",
  notes: "לפי רשימה מאושרת"
}, {
  check: "אימות נייר ערך",
  importance: "התאמת ISIN ושם",
  output: "ניירות לא מזוהים",
  notes: "לפי מאגר ניירות"
}];

const FUND_MANAGERS = [
  "מגדל",
  "איילון",
  "קסם",
  "סיגמא",
  "פורסט",
  "הראל",
  "אנליסט",
  "מיטב",
  "איביאי",
  "אלטשולר-שחם",
];

// Mizrahi Special Transactions API
const API_BASE = "https://209.38.226.220.nip.io";

const STATUS_MESSAGES: Record<string, string> = {
  queued: "הבקשה התקבלה",
  downloading: "מוריד דוח מ-TASE Maya...",
  processing: "מעבד את הדוח...",
  sending_email: "שולח דוח במייל...",
  completed: "הדוח נשלח בהצלחה!",
};

type FormState = "idle" | "loading" | "success" | "error";

interface JobStatus {
  status: "queued" | "downloading" | "processing" | "sending_email" | "completed" | "failed";
  message: string;
  error?: string;
  result?: {
    summary: Record<string, unknown>;
    email_sent_to: string[];
    output_file: string;
  };
}

const ToolMatched = () => {
  const [isLightboxOpen, setIsLightboxOpen] = useState(false);
  const [isRunDialogOpen, setIsRunDialogOpen] = useState(false);
  
  // Form state
  const [managerName, setManagerName] = useState("");
  const [email, setEmail] = useState("");
  const [formState, setFormState] = useState<FormState>("idle");
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  
  // Validation errors
  const [managerError, setManagerError] = useState("");
  const [emailError, setEmailError] = useState("");

  const validateEmail = (emailStr: string): boolean => {
    const emails = emailStr.split(";").map((e) => e.trim()).filter((e) => e);
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emails.length > 0 && emails.every((e) => emailRegex.test(e));
  };

  const validateForm = (): boolean => {
    let valid = true;
    
    if (!managerName) {
      setManagerError("שדה חובה");
      valid = false;
    } else {
      setManagerError("");
    }
    
    if (!email) {
      setEmailError("שדה חובה");
      valid = false;
    } else if (!validateEmail(email)) {
      setEmailError("כתובת אימייל לא תקינה");
      valid = false;
    } else {
      setEmailError("");
    }
    
    return valid;
  };

  const submitReport = async (): Promise<string> => {
    const formData = new FormData();
    formData.append("manager_name", managerName);
    formData.append("email", email);

    const response = await fetch(`${API_BASE}/api/process-report`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "שגיאה בשליחת הבקשה");
    }

    const data = await response.json();
    return data.job_id;
  };

  const getJobStatus = async (jobId: string): Promise<JobStatus> => {
    const response = await fetch(`${API_BASE}/api/job/${jobId}`);
    if (!response.ok) {
      throw new Error("שגיאה בבדיקת סטטוס");
    }
    return response.json();
  };

  const waitForCompletion = async (jobId: string): Promise<JobStatus> => {
    let attempts = 0;
    const maxAttempts = 120;

    while (attempts < maxAttempts) {
      const status = await getJobStatus(jobId);
      // Use Hebrew status message mapping
      const hebrewMessage = STATUS_MESSAGES[status.status] || status.message;
      setStatusMessage(hebrewMessage);

      if (status.status === "completed") {
        return status;
      }

      if (status.status === "failed") {
        throw new Error(status.error || status.message || "עיבוד הדוח נכשל");
      }

      await new Promise((resolve) => setTimeout(resolve, 2000));
      attempts++;
    }

    throw new Error("העיבוד לקח יותר מדי זמן. נסה שוב מאוחר יותר.");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setFormState("loading");
    setStatusMessage("מתחיל עיבוד...");
    setErrorMessage("");

    try {
      const jobId = await submitReport();
      await waitForCompletion(jobId);
      setFormState("success");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "שגיאה לא צפויה");
      setFormState("error");
    }
  };

  const resetForm = () => {
    setManagerName("");
    setEmail("");
    setFormState("idle");
    setStatusMessage("");
    setErrorMessage("");
    setManagerError("");
    setEmailError("");
  };

  const closeDialog = () => {
    setIsRunDialogOpen(false);
    // Reset form when closing
    setTimeout(resetForm, 200);
  };

  return <div className="min-h-screen flex flex-col bg-background">
      <TopBar />
      
      <main className="flex-1 py-8 md:py-12">
        <div className="container mx-auto px-4 md:px-6 max-w-5xl">
          {/* Back Link */}
          <Link to="/" className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-6">
            <ArrowRight className="w-4 h-4" />
            חזרה לפורטל
          </Link>

          {/* Header */}
          <div className="mb-8">
            <div className="flex flex-wrap items-center gap-4 mb-4">
              <h1 className="text-2xl md:text-3xl font-bold text-foreground">
                בקרה אוטומטית על דוח עסקאות מתואמות ועסקאות מחוץ לבורסה
              </h1>
              <StatusBadge status="active" />
            </div>
            <p className="text-lg text-muted-foreground mb-4">
              זיהוי התאמות, כפילויות ופערים בין מקורות.
            </p>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="w-4 h-4" />
              <span>ריצה אוטומטית: בכל 5 לחודש ב-10:00</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-4 mb-10">
            <button
              onClick={() => setIsRunDialogOpen(true)}
              className="btn-primary flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              הפעל בדיקה עכשיו
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
                  <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                  <span>הבדיקה תופעל בעתיד בצורה אוטומטית ותשלח דוח לצוות הבקרה</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                  <span>בכל 5 לחודש בשעה 10:00 -- עדיין לא פעיל</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                  <span>סינון וסיווג אוטומטי של עסקאות מחוץ לבורסה (OTC)</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                  <span>דוח מפורט עם פירוט הפערים והמלצות</span>
                </li>
              </ul>
            </div>
          </section>

          {/* Check Table */}
          <section className="mb-10 hidden md:block">
            <h2 className="text-xl font-semibold text-foreground mb-4">מה נבדק</h2>
            <CheckTable items={checkItems} />
          </section>

          {/* Schedule */}
          <section className="mb-10">
            <h2 className="text-xl font-semibold text-foreground mb-4">זמני ריצה אוטומטיים</h2>
            <div className="card-portal">
              <div className="flex items-center gap-3">
                <Calendar className="w-6 h-6 text-primary" />
                <div>
                  <p className="font-medium text-foreground">בכל 5 לחודש בשעה 10:00</p>
                  <p className="text-sm text-muted-foreground">הבדיקה מופעלת אוטומטית ושולחת דוח לצוות</p>
                </div>
              </div>
            </div>
          </section>

          {/* Sample Report */}
          <section className="mb-10">
            <h2 className="text-xl font-semibold text-foreground mb-4">דוח לדוגמה</h2>
            <div className="card-portal">
              <img 
                src={matchedReportImage} 
                alt="דוח עסקאות מתואמות לדוגמה" 
                className="w-full rounded-lg border border-border"
              />
              <button onClick={() => setIsLightboxOpen(true)} className="btn-outline flex items-center gap-2 mt-4">
                <ZoomIn className="w-4 h-4" />
                הגדל
              </button>
            </div>
          </section>

          {/* Manual Run */}
          
        </div>
      </main>

      <Footer />
      
      <LightboxModal isOpen={isLightboxOpen} onClose={() => setIsLightboxOpen(false)} title="דוח עסקאות מתואמות לדוגמה" imageSrc={matchedReportImage} />
      
      {/* Run Check Dialog */}
      <Dialog open={isRunDialogOpen} onOpenChange={closeDialog}>
        <DialogContent className="sm:max-w-lg" dir="rtl">
          <DialogHeader className="text-right">
            <DialogTitle className="text-right">בחירת קרן לדוח</DialogTitle>
            <DialogDescription className="text-right">
              בחר מנהל קרן מהרשימה - הדוח יורד אוטומטית מאתר מאיה
            </DialogDescription>
          </DialogHeader>
          
          {formState === "idle" || formState === "loading" ? (
            <form onSubmit={handleSubmit} className="space-y-6 py-4">
              {/* Manager Select */}
              <div className="space-y-2 text-right">
                <Label htmlFor="manager" className="block text-right">שם מנהל הקרן</Label>
                <Select
                  value={managerName}
                  onValueChange={setManagerName}
                  disabled={formState === "loading"}
                  dir="rtl"
                >
                  <SelectTrigger id="manager" className={`text-right ${managerError ? "border-destructive" : ""}`}>
                    <SelectValue placeholder="בחר מנהל קרן..." />
                  </SelectTrigger>
                  <SelectContent dir="rtl">
                    {FUND_MANAGERS.map((manager) => (
                      <SelectItem key={manager} value={manager} className="text-right">
                        {manager}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {managerError && (
                  <p className="text-sm text-destructive text-right">{managerError}</p>
                )}
              </div>

              {/* Email Input */}
              <div className="space-y-2 text-right">
                <Label htmlFor="email" className="block text-right">כתובת אימייל לשליחת הדוח</Label>
                <Input
                  id="email"
                  type="text"
                  placeholder="first@gmail.com; second@gmail.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={formState === "loading"}
                  className={`text-left ${emailError ? "border-destructive" : ""}`}
                  dir="ltr"
                />
                <p className="text-xs text-muted-foreground text-right">
                  ניתן להזין מספר כתובות מופרדות בנקודה-פסיק
                </p>
                {emailError && (
                  <p className="text-sm text-destructive text-right">{emailError}</p>
                )}
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full"
                disabled={formState === "loading"}
              >
                {formState === "loading" ? (
                  <>
                    <Loader2 className="w-4 h-4 me-2 animate-spin" />
                    מעבד...
                  </>
                ) : (
                  "הפק דוח"
                )}
              </Button>

              {/* Status Message */}
              {formState === "loading" && statusMessage && (
                <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>{statusMessage}</span>
                </div>
              )}
            </form>
          ) : formState === "success" ? (
            <div className="py-8 text-center space-y-4">
              <div className="flex justify-center">
                <CheckCircle className="w-16 h-16 text-success" />
              </div>
              <h3 className="text-xl font-semibold text-foreground">הדוח נשלח בהצלחה!</h3>
              <p className="text-muted-foreground">
                דוח עסקאות מיוחדות עבור {managerName} נשלח ל-{email}
              </p>
              <Button onClick={resetForm} variant="outline" className="mt-4">
                הפק דוח נוסף
              </Button>
            </div>
          ) : (
            <div className="py-8 text-center space-y-4">
              <div className="flex justify-center">
                <XCircle className="w-16 h-16 text-destructive" />
              </div>
              <h3 className="text-xl font-semibold text-foreground">שגיאה בעיבוד הדוח</h3>
              <p className="text-muted-foreground">{errorMessage}</p>
              <Button onClick={resetForm} variant="outline" className="mt-4">
                נסה שוב
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>;
};
export default ToolMatched;