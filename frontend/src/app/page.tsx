import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-neutral-900 text-white p-8">
      <header className="flex justify-between items-center mb-12">
        <h1 className="text-3xl font-bold text-purple-500">Auto Clipper Platform</h1>
        <nav>
          <ul className="flex space-x-6">
            <li><Link href="/" className="hover:text-purple-400">Dashboard</Link></li>
            <li><Link href="/upload" className="hover:text-purple-400">Upload Video</Link></li>
            <li><Link href="/clips" className="hover:text-purple-400">My Clips</Link></li>
          </ul>
        </nav>
      </header>

      <main>
        <section className="bg-neutral-800 p-8 rounded-xl shadow-lg border border-neutral-700">
          <h2 className="text-2xl font-semibold mb-6">Welcome to Auto Clipper</h2>
          <p className="text-neutral-300 mb-8 max-w-2xl">
            Automatically convert your long-form videos into viral short-form reels.
            Everything runs locally on your machine for maximum privacy and performance.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-neutral-900 p-6 rounded-lg border border-neutral-700">
              <h3 className="text-xl font-bold text-purple-400 mb-2">1. Upload</h3>
              <p className="text-neutral-400 text-sm">Upload a local file or paste a YouTube URL.</p>
            </div>
            <div className="bg-neutral-900 p-6 rounded-lg border border-neutral-700">
              <h3 className="text-xl font-bold text-purple-400 mb-2">2. Analyze</h3>
              <p className="text-neutral-400 text-sm">Local AI transcribes and finds the most viral moments.</p>
            </div>
            <div className="bg-neutral-900 p-6 rounded-lg border border-neutral-700">
              <h3 className="text-xl font-bold text-purple-400 mb-2">3. Export</h3>
              <p className="text-neutral-400 text-sm">Get ready-to-post vertical videos with captions.</p>
            </div>
          </div>

          <div className="mt-10">
            <Link href="/upload" className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-lg transition-colors">
              Start Creating Clips
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
