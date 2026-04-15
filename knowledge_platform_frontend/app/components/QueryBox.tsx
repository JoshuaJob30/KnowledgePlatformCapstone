"use client";
import { useState } from "react";
import api from "../utils/axios";
import { TextField, Button, Paper, Typography, CircularProgress, Box } from "@mui/material";

export default function QueryBox() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; text: string; source?: string }[]
  >([]);
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", text: query }]);
    try {
      const res = await api.get("/query", { params: { q: query } });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: res.data.answer, source: res.data.source },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: `Error: ${err.response?.data?.detail || err.message}`, source: "error" },
      ]);
    } finally {
      setQuery("");
      setLoading(false);
    }
  };

  const handleClearChat = async () => {
    try {
      await api.post("/query/clear_memory");   // clear backend memory
      setMessages([]);                         // clear frontend chat history
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: `Error clearing chat: ${err.message}`, source: "error" },
      ]);
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
      <Box display="flex" gap={2} mt={2}>
        <Button
          variant="contained"
          color="success"
          disabled={!query.trim() || loading}
          onClick={handleQuery}
        >
          {loading ? <CircularProgress size={20} color="inherit" /> : "Ask"}
        </Button>
        <Button
          variant="outlined"
          color="error"
          onClick={handleClearChat}
        >
          Clear Chat
        </Button>
      </Box>

      {/* Scrollable chat window */}
      <Box
        sx={{
          mt: 3,
          display: "flex",
          flexDirection: "column",
          gap: 1,
          maxHeight: 400,
          overflowY: "auto",
          p: 2,
          border: "1px solid #ddd",
          borderRadius: 2,
          bgcolor: "grey.50"
        }}
      >
        {messages.map((msg, idx) => (
          <Paper
            key={idx}
            sx={{
              p: 2,
              maxWidth: "70%",
              bgcolor: msg.role === "user" ? "primary.light" : "grey.100",
              color: msg.role === "user" ? "white" : "black",
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
            }}
          >
            <Typography variant="body2" sx={{ whiteSpace: "pre-line" }}>
              {msg.text}
            </Typography>
            {msg.source && msg.role === "assistant" && (
              <Typography variant="caption" color="text.secondary">
                Source: {msg.source}
              </Typography>
            )}
          </Paper>
        ))}
      </Box>
    </Paper>
  );
}
