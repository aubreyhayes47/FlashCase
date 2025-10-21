import Link from "next/link";

export default function Discover() {
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
              <Link href="/discover" className="text-blue-600 font-semibold">Discover</Link>
              <Link href="/study" className="hover:text-blue-600">Study</Link>
              <Link href="/create" className="hover:text-blue-600">Create</Link>
            </div>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8">Discover Decks</h1>

        {/* Search Bar */}
        <div className="mb-8">
          <input
            type="text"
            placeholder="Search for decks by subject, course, or topic..."
            className="w-full px-4 py-3 border rounded-lg"
          />
        </div>

        {/* Categories */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Popular Categories</h2>
          <div className="grid md:grid-cols-4 gap-4">
            {["Constitutional Law", "Contracts", "Torts", "Civil Procedure", "Criminal Law", "Property", "Evidence", "Professional Responsibility"].map((category) => (
              <button
                key={category}
                className="border rounded-lg p-4 hover:border-blue-600 hover:bg-blue-50 transition"
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* Featured Decks */}
        <div>
          <h2 className="text-2xl font-bold mb-4">Featured Decks</h2>
          <div className="border rounded-lg p-8 text-center text-gray-500">
            <p>Community decks will appear here once created</p>
            <p className="mt-2 text-sm">Be the first to create a public deck!</p>
          </div>
        </div>
      </main>
    </div>
  );
}
