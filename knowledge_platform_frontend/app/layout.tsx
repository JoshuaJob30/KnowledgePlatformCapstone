// app/layout.tsx
import NavigationBar from "./components/NavigationBar";
import Footer from "./components/Footer";
import "./globals.css";
import ThemeRegistry from "./theme/ThemeRegistry";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {/* Ensure ThemeRegistry sets up MUI ThemeProvider + CssBaseline */}
        <ThemeRegistry>
          {/* NavigationBar is a client component, safe inside ThemeRegistry */}
          <NavigationBar />
          <main className="container mx-auto p-6">{children}</main>
          <Footer />
        </ThemeRegistry>
      </body>
    </html>
  );
}
