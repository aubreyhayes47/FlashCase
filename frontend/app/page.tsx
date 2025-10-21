import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <nav className="flex justify-between items-center">
            <Link href="/" className="text-2xl font-bold text-blue-600">
              FlashCase 📚⚖️
            </Link>
            <div className="space-x-4">
              <Link href="/dashboard" className="hover:text-blue-600">Dashboard</Link>
              <Link href="/discover" className="hover:text-blue-600">Discover</Link>
              <Link href="/study" className="hover:text-blue-600">Study</Link>
              <Link href="/create" className="hover:text-blue-600">Create</Link>
            </div>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-grow container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold mb-6">
            Master Law School with Smart Flashcards
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            FlashCase combines spaced repetition, community decks, and AI-powered content creation 
            to help law students learn efficiently and retain knowledge long-term.
          </p>
          <div className="flex gap-4 justify-center">
            <Link 
              href="/dashboard"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
            >
              Get Started
            </Link>
            <Link 
              href="/discover"
              className="bg-gray-200 text-gray-800 px-8 py-3 rounded-lg font-semibold hover:bg-gray-300 transition"
            >
              Browse Decks
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-16">
          <div className="p-6 border rounded-lg">
            <div className="text-3xl mb-4">🧠</div>
            <h3 className="text-xl font-semibold mb-2">Smart Learning</h3>
            <p className="text-gray-600">
              Spaced repetition algorithm optimizes your study time by focusing on cards you're about to forget.
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <div className="text-3xl mb-4">👥</div>
            <h3 className="text-xl font-semibold mb-2">Community Decks</h3>
            <p className="text-gray-600">
              Access professionally curated decks for every law school course, created and verified by peers.
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <div className="text-3xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold mb-2">AI-Powered</h3>
            <p className="text-gray-600">
              Generate flashcards automatically from case briefs, outlines, and legal texts using AI.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>FlashCase - Modern flashcard app for law students</p>
        </div>
      </footer>
    </div>
  );
}
