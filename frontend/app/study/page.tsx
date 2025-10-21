'use client';

import Link from "next/link";
import { useState, useEffect } from "react";

interface Card {
  id: number;
  deck_id: number;
  front: string;
  back: string;
  ease_factor: number;
  interval: number;
  repetitions: number;
  due_date: string;
}

export default function Study() {
  const [cards, setCards] = useState<Card[]>([]);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(false);

  const currentCard = cards[currentCardIndex];
  const remainingCards = cards.length - currentCardIndex;

  // Keyboard shortcuts handler
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (!currentCard) return;

      // Space to show answer
      if (e.code === 'Space' && !showAnswer) {
        e.preventDefault();
        setShowAnswer(true);
      }
      
      // Number keys for rating (only when answer is shown)
      if (showAnswer) {
        if (e.key === '1') handleRating(0); // Again
        else if (e.key === '2') handleRating(2); // Hard
        else if (e.key === '3') handleRating(3); // Good
        else if (e.key === '4') handleRating(5); // Easy
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentCard, showAnswer]);

  const handleRating = async (quality: number) => {
    if (!currentCard || loading) return;
    
    setLoading(true);
    
    try {
      // In a real implementation, this would call the backend API
      // const response = await fetch(`/api/v1/study/review/${currentCard.id}`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ quality })
      // });
      
      // Move to next card
      if (currentCardIndex < cards.length - 1) {
        setCurrentCardIndex(currentCardIndex + 1);
        setShowAnswer(false);
      } else {
        // Session complete
        setCards([]);
        setCurrentCardIndex(0);
      }
    } catch (error) {
      console.error('Failed to submit rating:', error);
    } finally {
      setLoading(false);
    }
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
              <Link href="/discover" className="hover:text-blue-600">Discover</Link>
              <Link href="/study" className="text-blue-600 font-semibold">Study</Link>
              <Link href="/create" className="hover:text-blue-600">Create</Link>
            </div>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-4">Study Session</h1>
        
        {/* Legal Disclaimer */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 text-sm">
            <p className="text-yellow-800">
              <strong>⚖️ Not Legal Advice:</strong> FlashCase is an educational tool. Content does not constitute legal advice. 
              Always consult with a qualified attorney for specific legal matters.
            </p>
          </div>
        </div>

        <div className="max-w-2xl mx-auto">
          {/* Card Display Area */}
          <div className="border rounded-lg p-12 mb-6 min-h-[400px] flex items-center justify-center bg-white shadow-lg">
            {currentCard ? (
              <div className="text-center w-full">
                <div className="text-sm text-gray-500 mb-4">
                  {showAnswer ? 'Answer:' : 'Question:'}
                </div>
                <div className="text-2xl mb-8">
                  {showAnswer ? currentCard.back : currentCard.front}
                </div>
                {!showAnswer && (
                  <button
                    onClick={() => setShowAnswer(true)}
                    className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                  >
                    Show Answer (Space)
                  </button>
                )}
              </div>
            ) : (
              <div className="text-center text-gray-500">
                <p className="text-xl mb-4">No cards to review right now</p>
                <p>Create a deck or import cards to start studying</p>
              </div>
            )}
          </div>

          {/* Study Controls */}
          <div className="flex justify-between items-center mb-4">
            <div className="text-gray-600">
              <span className="font-semibold">{remainingCards}</span> cards remaining
            </div>
            {showAnswer && currentCard && (
              <div className="space-x-2">
                <button 
                  onClick={() => handleRating(0)}
                  disabled={loading}
                  className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:bg-gray-300 transition"
                  title="Again (1)"
                >
                  Again
                </button>
                <button 
                  onClick={() => handleRating(2)}
                  disabled={loading}
                  className="px-6 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 disabled:bg-gray-300 transition"
                  title="Hard (2)"
                >
                  Hard
                </button>
                <button 
                  onClick={() => handleRating(3)}
                  disabled={loading}
                  className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300 transition"
                  title="Good (3)"
                >
                  Good
                </button>
                <button 
                  onClick={() => handleRating(5)}
                  disabled={loading}
                  className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 transition"
                  title="Easy (4)"
                >
                  Easy
                </button>
              </div>
            )}
          </div>

          {/* Keyboard Shortcuts Help */}
          <div className="text-center text-sm text-gray-500 mb-6">
            Keyboard shortcuts: Space (show answer), 1 (again), 2 (hard), 3 (good), 4 (easy)
          </div>

          {/* Study Stats */}
          <div className="mt-8 grid grid-cols-3 gap-4 text-center">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold">0</div>
              <div className="text-sm text-gray-600">New</div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold">{cards.length}</div>
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
