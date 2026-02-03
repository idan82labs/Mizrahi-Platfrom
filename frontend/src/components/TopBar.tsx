import { Link } from "react-router-dom";
import logo from "@/assets/logo.svg";
const TopBar = () => {
  return <header className="sticky top-0 z-40 bg-card/95 backdrop-blur-sm border-b border-border">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex items-center justify-center h-16 md:h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <img src={logo} alt="מזרחי טפחות" className="h-8 md:h-10 w-auto" />
            <div className="flex flex-col">
              
              
            </div>
          </Link>
        </div>
      </div>
    </header>;
};
export default TopBar;