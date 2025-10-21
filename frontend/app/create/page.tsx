'use client';

import Link from "next/link";
import { useState } from "react";

export default function Create() {
  const [front, setFront] = useState("");
  const [back, setBack] = useState("");
  const [isRewriting, setIsRewriting] = useState(false);
  const [isAutocompleting, setIsAutocompleting] = useState(false);
  const [aiMessage, setAiMessage] = useState("");

  const handleRewrite = async () => {
    if (!front || !back) {
      setAiMessage("Please enter both front and back content before rewriting.");
      return;
    }

    setIsRewriting(true);
    setAiMessage("");

    try {
      // In a real implementation, this would call the backend AI API
      // const response = await fetch('/api/v1/ai/rewrite-card', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ front, back })
      // });
      
      // For now, show a placeholder message
      setAiMessage("AI Rewrite feature ready! Connect to backend API to use.");
    } catch (error) {
      setAiMessage("Failed to rewrite card. Please try again.");
      console.error('Failed to rewrite card:', error);
    } finally {
      setIsRewriting(false);
    }
  };

  const handleAutocomplete = async (cardType: 'front' | 'back') => {
    const partialText = cardType === 'front' ? front : back;
    
    if (!partialText) {
      setAiMessage(`Please enter some text in the ${cardType} field first.`);
      return;
    }

    setIsAutocompleting(true);
    setAiMessage("");

    try {
      // In a real implementation, this would call the backend AI API
      // const response = await fetch('/api/v1/ai/autocomplete-card', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ partial_text: partialText, card_type: cardType })
      // });
      
      // For now, show a placeholder message
      setAiMessage("AI Autocomplete feature ready! Connect to backend API to use.");
    } catch (error) {
      setAiMessage("Failed to autocomplete. Please try again.");
      console.error('Failed to autocomplete:', error);
    } finally {
      setIsAutocompleting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!front || !back) {
      setAiMessage("Please fill in both front and back fields.");
      return;
    }

    // In a real implementation, this would call the backend API to create the card
    // const response = await fetch('/api/v1/cards', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ deck_id: selectedDeckId, front, back })
    // });
    
    setAiMessage("Card created successfully!");
    setFront("");
    setBack("");
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
              <Link href="/study" className="hover:text-blue-600">Study</Link>
              <Link href="/create" className="text-blue-600 font-semibold">Create</Link>
            </div>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8">Create Flashcards</h1>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Manual Creation with AI Assist */}
          <div className="border rounded-lg p-6">
            <h2 className="text-2xl font-bold mb-4">Manual Creation</h2>
            <p className="text-gray-600 mb-6">
              Create flashcards one at a time with AI-powered assistance
            </p>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold mb-2">Deck</label>
                <select className="w-full px-4 py-2 border rounded-lg">
                  <option>Select a deck...</option>
                </select>
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-sm font-semibold">Front (Question)</label>
                  <button
                    type="button"
                    onClick={() => handleAutocomplete('front')}
                    disabled={isAutocompleting || !front}
                    className="text-sm px-3 py-1 bg-purple-100 text-purple-700 rounded hover:bg-purple-200 disabled:bg-gray-100 disabled:text-gray-400 transition"
                    title="AI Auto-complete"
                  >
                    ✨ Auto-complete
                  </button>
                </div>
                <textarea
                  className="w-full px-4 py-2 border rounded-lg"
                  rows={3}
                  placeholder="Enter the question or prompt..."
                  value={front}
                  onChange={(e) => setFront(e.target.value)}
                ></textarea>
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-sm font-semibold">Back (Answer)</label>
                  <button
                    type="button"
                    onClick={() => handleAutocomplete('back')}
                    disabled={isAutocompleting || !back}
                    className="text-sm px-3 py-1 bg-purple-100 text-purple-700 rounded hover:bg-purple-200 disabled:bg-gray-100 disabled:text-gray-400 transition"
                    title="AI Auto-complete"
                  >
                    ✨ Auto-complete
                  </button>
                </div>
                <textarea
                  className="w-full px-4 py-2 border rounded-lg"
                  rows={3}
                  placeholder="Enter the answer..."
                  value={back}
                  onChange={(e) => setBack(e.target.value)}
                ></textarea>
              </div>

              {/* AI Assist Buttons */}
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={handleRewrite}
                  disabled={isRewriting || !front || !back}
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 transition"
                  title="Use AI to improve this card"
                >
                  {isRewriting ? '✨ Rewriting...' : '✨ AI Rewrite'}
                </button>
              </div>

              {/* AI Message */}
              {aiMessage && (
                <div className={`p-3 rounded-lg text-sm ${
                  aiMessage.includes('Failed') || aiMessage.includes('Please') 
                    ? 'bg-yellow-50 border border-yellow-200 text-yellow-800'
                    : 'bg-green-50 border border-green-200 text-green-800'
                }`}>
                  {aiMessage}
                </div>
              )}
              
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
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  💡 <strong>AI Features Available:</strong> Use the "AI Rewrite" and "Auto-complete" buttons in the manual creation form to enhance your cards with AI assistance.
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
