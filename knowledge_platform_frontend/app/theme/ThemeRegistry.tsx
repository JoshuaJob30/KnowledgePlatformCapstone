// app/theme/ThemeRegistry.tsx
"use client";

import * as React from "react";
import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import { CacheProvider } from "@emotion/react";
import createCache from "@emotion/cache";

const muiCache = createCache({ key: "mui", prepend: true });

const theme = createTheme({
  palette: {
    primary: {
      main: "#1E40AF",       // Deep blue
      light: "#3B82F6",
      dark: "#1E3A8A",
    },
    secondary: {
      main: "#10B981",       // Green
      light: "#34D399",
      dark: "#047857",
    },
    background: {
      default: "#ffffff",
      paper: "#f9fafb",
    },
    text: {
      primary: "#171717",
      secondary: "#4b5563",
    },
  },
  typography: {
    fontFamily: "Inter, system-ui, sans-serif",
    h1: { fontFamily: "Poppins, sans-serif" },
    h2: { fontFamily: "Poppins, sans-serif" },
    h3: { fontFamily: "Poppins, sans-serif" },
    h4: { fontFamily: "Poppins, sans-serif" },
  },
});

export default function ThemeRegistry({ children }: { children: React.ReactNode }) {
  return (
    <CacheProvider value={muiCache}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </CacheProvider>
  );
}
