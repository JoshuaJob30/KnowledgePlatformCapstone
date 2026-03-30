"use client";
import { useEffect, useState } from "react";
import UploadForm from "./components/UploadForm";
import QueryBox from "./components/QueryBox";
import { Container, Typography } from "@mui/material";

export default function Page() {
  const [role, setRole] = useState<string | null>(null);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("jwt");
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        setRole(payload.role);
      } catch {
        setRole(null);
      }
    }
    setChecked(true);
  }, []);

  if (!checked) return null;

  return (
    <Container maxWidth="md" sx={{ mt: 6 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Knowledge Platform
      </Typography>
      <UploadForm />
      <QueryBox />
    </Container>
  );
}
