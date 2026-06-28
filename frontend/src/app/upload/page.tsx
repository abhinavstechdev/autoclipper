"use client";

import { useState } from "react";
import Link from "next/link";

export default function UploadPage() {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState("");

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Submitting...");

    try {
      const res = await fetch("http://localhost:8000/api/videos/url", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });

      if (res.ok) {
        setStatus("Video submitted successfully! Processing started in the background.");
        setUrl("");
      } else {
        setStatus("Error submitting video.");
      }
    } catch (error) {
      setStatus("Connection error. Ensure backend is running.");
    }
  };

  return (
    <div className="min-h-screen bg-neutral-900 text-white p-8">
      <header className="flex justify-between items-center mb-12">
        <Link href="/">
          <h1 className="text-3xl font-bold text-purple-500 hover:text-purple-400 cursor-pointer">Auto Clipper</h1>
        </Link>
      </header>

      <main className="max-w-2xl mx-auto">
        <div className="bg-neutral-800 p-8 rounded-xl shadow-lg border border-neutral-700">
          <h2 className="text-2xl font-semibold mb-6">Upload Video</h2>

          <form onSubmit={handleUrlSubmit} className="mb-8">
            <label className="block text-sm font-medium text-neutral-300 mb-2">
              YouTube URL
            </label>
            <div className="flex gap-4">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="flex-1 bg-neutral-900 border border-neutral-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500"
                required
              />
              <button
                type="submit"
                className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-6 rounded-lg transition-colors"
              >
                Import
              </button>
            </div>
          </form>

          <div className="border-t border-neutral-700 pt-8 text-center">
            <p className="text-neutral-400 mb-4">Or upload a local file</p>
            <div className="border-2 border-dashed border-neutral-600 rounded-xl p-12 hover:border-purple-500 transition-colors cursor-pointer">
              <p className="text-neutral-300">Drag & drop a video file here, or click to browse.</p>
              <p className="text-neutral-500 text-sm mt-2">Supports MP4, MOV, MKV up to 5GB.</p>
            </div>
          </div>

          {status && (
            <div className="mt-6 p-4 rounded bg-neutral-900 border border-purple-500/30 text-purple-200">
              {status}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
