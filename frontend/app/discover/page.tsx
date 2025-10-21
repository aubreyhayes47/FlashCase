'use client';

import Link from "next/link";
import { useState } from "react";

interface Deck {
  id: number;
  name: string;
  description: string | null;
  is_public: boolean;
  school: string | null;
  course: string | null;
  professor: string | null;
  year: number | null;
  created_at: string;
  updated_at: string;
}

export default function Discover() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filters, setFilters] = useState({
    school: "",
    course: "",
    professor: "",
    year: ""
  });
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(false);

  const handleFilterChange = (field: string, value: string) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      // In a real implementation, this would call the backend API
      // const params = new URLSearchParams();
      // if (filters.school) params.append('school', filters.school);
      // if (filters.course) params.append('course', filters.course);
      // if (filters.professor) params.append('professor', filters.professor);
      // if (filters.year) params.append('year', filters.year);
      // const response = await fetch(`/api/v1/decks?${params}`);
      // const data = await response.json();
      // setDecks(data);
    } catch (error) {
      console.error('Failed to fetch decks:', error);
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setFilters({
      school: "",
      course: "",
      professor: "",
      year: ""
    });
  };

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
        <h1 className="text-4xl font-bold mb-4">Discover Decks</h1>
        
        {/* Legal Disclaimer */}
        <div className="mb-8">
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 text-sm">
            <p className="text-yellow-800">
              <strong>⚖️ Not Legal Advice:</strong> Community-created content is for educational purposes only and does not constitute legal advice. 
              Verify all information with authoritative sources.
            </p>
          </div>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <input
            type="text"
            placeholder="Search for decks by subject, course, or topic..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-3 border rounded-lg"
          />
        </div>

        {/* Metadata Filters */}
        <div className="mb-8 bg-gray-50 p-6 rounded-lg border">
          <h2 className="text-xl font-bold mb-4">Filter by Metadata</h2>
          <div className="grid md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-semibold mb-2">School</label>
              <input
                type="text"
                placeholder="e.g., Harvard Law"
                value={filters.school}
                onChange={(e) => handleFilterChange('school', e.target.value)}
                className="w-full px-4 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Course</label>
              <input
                type="text"
                placeholder="e.g., Constitutional Law"
                value={filters.course}
                onChange={(e) => handleFilterChange('course', e.target.value)}
                className="w-full px-4 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Professor</label>
              <input
                type="text"
                placeholder="e.g., Prof. Smith"
                value={filters.professor}
                onChange={(e) => handleFilterChange('professor', e.target.value)}
                className="w-full px-4 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Year</label>
              <input
                type="number"
                placeholder="e.g., 2024"
                value={filters.year}
                onChange={(e) => handleFilterChange('year', e.target.value)}
                className="w-full px-4 py-2 border rounded-lg"
                min="1900"
                max="2100"
              />
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 transition"
            >
              {loading ? 'Searching...' : 'Apply Filters'}
            </button>
            <button
              onClick={clearFilters}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Categories */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Popular Categories</h2>
          <div className="grid md:grid-cols-4 gap-4">
            {["Constitutional Law", "Contracts", "Torts", "Civil Procedure", "Criminal Law", "Property", "Evidence", "Professional Responsibility"].map((category) => (
              <button
                key={category}
                onClick={() => handleFilterChange('course', category)}
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
          {decks.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {decks.map((deck) => (
                <div key={deck.id} className="border rounded-lg p-6 hover:shadow-lg transition">
                  <h3 className="text-xl font-bold mb-2">{deck.name}</h3>
                  {deck.description && (
                    <p className="text-gray-600 mb-4">{deck.description}</p>
                  )}
                  <div className="text-sm text-gray-500 space-y-1">
                    {deck.school && <div>🏫 {deck.school}</div>}
                    {deck.course && <div>📚 {deck.course}</div>}
                    {deck.professor && <div>👨‍🏫 {deck.professor}</div>}
                    {deck.year && <div>📅 {deck.year}</div>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="border rounded-lg p-8 text-center text-gray-500">
              <p>Community decks will appear here once created</p>
              <p className="mt-2 text-sm">Be the first to create a public deck!</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
