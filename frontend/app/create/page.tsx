import Link from "next/link";

export default function Create() {
  return (
    <div className="min-h-screen">
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
              <Link href="/create" className="text-blue-600 font-semibold">Create</Link>
            </div>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8">Create Flashcards</h1>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Manual Creation */}
          <div className="border rounded-lg p-6">
            <h2 className="text-2xl font-bold mb-4">Manual Creation</h2>
            <p className="text-gray-600 mb-6">
              Create flashcards one at a time with full control over content
            </p>
            
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-semibold mb-2">Deck</label>
                <select className="w-full px-4 py-2 border rounded-lg">
                  <option>Select a deck...</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-semibold mb-2">Front (Question)</label>
                <textarea
                  className="w-full px-4 py-2 border rounded-lg"
                  rows={3}
                  placeholder="Enter the question or prompt..."
                ></textarea>
              </div>
              
              <div>
                <label className="block text-sm font-semibold mb-2">Back (Answer)</label>
                <textarea
                  className="w-full px-4 py-2 border rounded-lg"
                  rows={3}
                  placeholder="Enter the answer..."
                ></textarea>
              </div>
              
              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
              >
                Add Card
              </button>
            </form>
          </div>

          {/* AI-Assisted Creation */}
          <div className="border rounded-lg p-6 bg-gradient-to-br from-purple-50 to-blue-50">
            <h2 className="text-2xl font-bold mb-4">AI-Assisted Creation</h2>
            <p className="text-gray-600 mb-6">
              Generate flashcards automatically from case briefs or legal texts
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold mb-2">Paste Text</label>
                <textarea
                  className="w-full px-4 py-2 border rounded-lg"
                  rows={8}
                  placeholder="Paste your case brief, outline, or legal text here..."
                ></textarea>
              </div>
              
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800">
                  🚧 AI generation coming soon in Phase 3
                </p>
              </div>
              
              <button
                type="button"
                className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 transition disabled:bg-gray-300"
                disabled
              >
                Generate Cards (Coming Soon)
              </button>
            </div>
          </div>
        </div>

        {/* Recent Cards */}
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">Recently Created Cards</h2>
          <div className="border rounded-lg p-8 text-center text-gray-500">
            <p>Your recently created cards will appear here</p>
          </div>
        </div>
      </main>
    </div>
  );
}
