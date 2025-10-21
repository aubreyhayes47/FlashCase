import Link from "next/link";

export default function Dashboard() {
  return (
    <div className="min-h-screen">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <nav className="flex justify-between items-center">
            <Link href="/" className="text-2xl font-bold text-blue-600">
              FlashCase 📚⚖️
            </Link>
            <div className="space-x-4">
              <Link href="/dashboard" className="text-blue-600 font-semibold">Dashboard</Link>
              <Link href="/discover" className="hover:text-blue-600">Discover</Link>
              <Link href="/study" className="hover:text-blue-600">Study</Link>
              <Link href="/create" className="hover:text-blue-600">Create</Link>
            </div>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8">Dashboard</h1>

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-blue-50 p-6 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">0</div>
            <div className="text-gray-600">Cards Due Today</div>
          </div>
          <div className="bg-green-50 p-6 rounded-lg">
            <div className="text-2xl font-bold text-green-600">0</div>
            <div className="text-gray-600">Cards Mastered</div>
          </div>
          <div className="bg-purple-50 p-6 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">0</div>
            <div className="text-gray-600">Study Streak</div>
          </div>
          <div className="bg-orange-50 p-6 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">0</div>
            <div className="text-gray-600">Total Decks</div>
          </div>
        </div>

        {/* Recent Decks */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">My Decks</h2>
          <div className="border rounded-lg p-8 text-center text-gray-500">
            <p>No decks yet. Create your first deck or discover community decks!</p>
            <div className="mt-4 space-x-4">
              <Link href="/create" className="text-blue-600 hover:underline">
                Create Deck
              </Link>
              <Link href="/discover" className="text-blue-600 hover:underline">
                Discover Decks
              </Link>
            </div>
          </div>
        </div>

        {/* Study Activity */}
        <div>
          <h2 className="text-2xl font-bold mb-4">Recent Activity</h2>
          <div className="border rounded-lg p-8 text-center text-gray-500">
            <p>Start studying to see your activity here</p>
          </div>
        </div>
      </main>
    </div>
  );
}
