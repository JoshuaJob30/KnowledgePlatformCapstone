"use client";
import { Paper, Typography } from "@mui/material";

const sourceLabels: Record<string, string> = {
  rag_doc: "Uploaded Documents",
  calc: "Calculator",
  healthcare: "Healthcare Agent",
  finance: "Finance Agent",
  shopping: "Shopping Agent",
  code: "Programming Agent",
  search: "Web Search",
  guardrail: "Safety Guardrail",
  error: "Error"
};

export default function AnswerDisplay({ answer, source }: { answer: string; source?: string }) {
  if (!answer) return null;
  const isError = answer.startsWith("Error:") || source === "error";

  return (
    <Paper
      elevation={2}
      sx={{
        mt: 3,
        p: 3,
        bgcolor: isError ? "error.light" : "grey.50",
        color: isError ? "error.dark" : "text.primary",
      }}
    >
      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
        Answer
      </Typography>
      <Typography variant="body2" sx={{ whiteSpace: "pre-line" }}>
        {answer}
      </Typography>
      {source && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: "block" }}>
          Source: {sourceLabels[source] || source}
        </Typography>
      )}
    </Paper>
  );
}
