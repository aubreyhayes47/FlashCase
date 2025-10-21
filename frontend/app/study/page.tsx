import Link from "next/link";

export default function Study() {
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
              <Link href="/study" className="text-blue-600 font-semibold">Study</Link>
              <Link href="/create" className="hover:text-blue-600">Create</Link>
            </div>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8">Study Session</h1>

        <div className="max-w-2xl mx-auto">
          {/* Card Display Area */}
          <div className="border rounded-lg p-12 mb-6 min-h-[400px] flex items-center justify-center">
            <div className="text-center text-gray-500">
              <p className="text-xl mb-4">No cards to review right now</p>
              <p>Create a deck or import cards to start studying</p>
            </div>
          </div>

          {/* Study Controls */}
          <div className="flex justify-between items-center">
            <div className="text-gray-600">
              <span className="font-semibold">0</span> cards remaining
            </div>
            <div className="space-x-2">
              <button 
                className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:bg-gray-300"
                disabled
              >
                Again
              </button>
              <button 
                className="px-6 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 disabled:bg-gray-300"
                disabled
              >
                Hard
              </button>
              <button 
                className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300"
                disabled
              >
                Good
              </button>
              <button 
                className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300"
                disabled
              >
                Easy
              </button>
            </div>
          </div>

          {/* Study Stats */}
          <div className="mt-8 grid grid-cols-3 gap-4 text-center">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold">0</div>
              <div className="text-sm text-gray-600">New</div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold">0</div>
              <div className="text-sm text-gray-600">Learning</div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold">0</div>
              <div className="text-sm text-gray-600">Review</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
