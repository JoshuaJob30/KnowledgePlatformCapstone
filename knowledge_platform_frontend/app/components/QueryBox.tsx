"use client";
import { useState } from "react";
import api from "../utils/axios";
import AnswerDisplay from "./AnswerDisplay";
import { TextField, Button, Paper, Typography, CircularProgress } from "@mui/material";

export default function QueryBox() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<{ answer: string; source: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await api.get("/query", { params: { q: query } });
      setResult({ answer: res.data.answer, source: res.data.source });
    } catch (err: any) {
      setResult({ answer: `Error: ${err.response?.data?.detail || err.message}`, source: "error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
      <Typography variant="h6" gutterBottom>Ask a Question</Typography>
      <TextField
        fullWidth
        label="Your question"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        margin="normal"
      />
      <Button
        variant="contained"
        color="success"
        disabled={!query.trim() || loading}
        onClick={handleQuery}
        sx={{ mt: 2 }}
      >
        {loading ? <CircularProgress size={20} color="inherit" /> : "Ask"}
      </Button>
      <AnswerDisplay answer={result?.answer || ""} source={result?.source || ""} />
    </Paper>
  );
}
