"use client";
import { useState } from "react";
import api from "../utils/axios";
import { Button, Typography, Paper, Box } from "@mui/material";

export default function UploadForm() {
  const [files, setFiles] = useState<File[]>([]);
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  const handleUpload = async () => {
    if (files.length === 0) return;
    setLoading(true);
    setStatus("");
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    try {
      const res = await api.post("/ingestion/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      // Backend returns { results: [{ filename, chunks_ingested }] }
      const results = res.data.results
        .map(
          (r: any) =>
            `${r.filename} (${r.chunks_ingested} chunks ingested${
              r.chunks_ingested === process.env.NEXT_PUBLIC_MAX_CHUNKS
                ? ", truncated to system limit"
                : ""
            })`
        )
        .join(", ");

      setStatus(`Uploaded: ${results}`);
      setFiles([]);
    } catch (err: any) {
      setStatus(`Error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 4 }}>
      <Typography variant="h6" gutterBottom>
        Upload Documents
      </Typography>
      <input
        type="file"
        multiple
        onChange={(e) => setFiles(Array.from(e.target.files || []))}
        style={{ marginBottom: "1rem" }}
      />
      {files.length > 0 && (
        <Box display="flex" flexDirection="column" mb={2}>
          {files.map((file, idx) => (
            <Box
              key={idx}
              display="flex"
              justifyContent="space-between"
              alignItems="center"
              mb={1}
            >
              <Typography variant="body2">{file.name}</Typography>
              <Button
                color="error"
                size="small"
                onClick={() =>
                  setFiles(files.filter((_, i) => i !== idx))
                }
              >
                Remove
              </Button>
            </Box>
          ))}
        </Box>
      )}
      <Button
        variant="contained"
        color="primary"
        disabled={files.length === 0 || loading}
        onClick={handleUpload}
      >
        {loading ? "Uploading..." : "Upload"}
      </Button>
      {status && (
        <Typography variant="body2" sx={{ mt: 2 }}>
          {status}
        </Typography>
      )}
    </Paper>
  );
}
