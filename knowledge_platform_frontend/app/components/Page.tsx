"use client";
import UploadForm from "../components/UploadForm";
import QueryBox from "../components/QueryBox";

export default function Page() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold text-gray-800">Knowledge Platform</h1>
      <UploadForm />
      <QueryBox />
    </div>
  );
}
