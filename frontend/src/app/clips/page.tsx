"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function ClipsPage() {
  const [clips, setClips] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchClips();
  }, []);

  const fetchClips = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/clips");
      if (res.ok) {
        const data = await res.json();
        setClips(data);
      }
    } catch (error) {
      console.error("Failed to fetch clips", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-900 text-white p-8">
      <header className="flex justify-between items-center mb-12">
        <Link href="/">
          <h1 className="text-3xl font-bold text-purple-500 hover:text-purple-400 cursor-pointer">Auto Clipper</h1>
        </Link>
      </header>

      <main>
        <h2 className="text-2xl font-semibold mb-6">Generated Clips</h2>

        {loading ? (
          <p>Loading clips...</p>
        ) : clips.length === 0 ? (
          <p className="text-neutral-400">No clips generated yet. Go to <Link href="/upload" className="text-purple-400 underline">Upload</Link> to start.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {clips.map((clip) => (
              <div key={clip.id} className="bg-neutral-800 rounded-lg overflow-hidden border border-neutral-700">
                <div className="aspect-[9/16] bg-neutral-900 relative">
                  {/* Placeholder for video thumbnail */}
                  <div className="absolute inset-0 flex items-center justify-center text-neutral-600">
                    Video Preview
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="font-bold text-lg mb-1 truncate">{clip.title || "Untitled Clip"}</h3>
                  <div className="flex justify-between text-sm text-neutral-400 mb-4">
                    <span>{clip.duration?.toFixed(1) || "???"}s</span>
                    <span className="text-green-400">Viral Score: {clip.virality_score || 0}</span>
                  </div>
                  <button className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 rounded font-medium transition-colors">
                    Export
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
