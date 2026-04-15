// app/components/Footer.tsx
"use client";
import { Box, Typography } from "@mui/material";

export default function Footer() {
  return (
    <Box
      component="footer"
      sx={{
        bgcolor: "grey.100",
        borderTop: "1px solid",
        borderColor: "grey.300",
        py: 3,
        mt: 8,
        textAlign: "center",
      }}
    >
      <Typography variant="body2" color="text.secondary">
        © 2026 Knowledge Platform
      </Typography>
    </Box>
  );
}
