// app/components/NavigationBar.tsx
"use client";
import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import Image from "next/image";

export default function NavigationBar() {
  return (
    <AppBar position="static" sx={{ bgcolor: "#ffffff" }} elevation={1}>
      <Toolbar sx={{ maxWidth: "1200px", mx: "auto", width: "100%" }}>
        <Box display="flex" alignItems="center" flexGrow={1}>
          <Image src="/logo.png" alt="Logo" width={40} height={40} />
          <Typography
            variant="h6"
            sx={{ ml: 2, fontWeight: "bold", color: "#000000" }}
          >
            Knowledge Platform
          </Typography>
        </Box>
        <Box>
          <Button color="inherit" href="/">Home</Button>
          <Button color="inherit" href="/about">About</Button>
          <Button color="inherit" href="/contact">Contact</Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
