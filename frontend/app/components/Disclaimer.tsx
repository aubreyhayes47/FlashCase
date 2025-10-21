/**
 * Disclaimer component for displaying legal and AI content warnings
 */

import React from 'react';

interface DisclaimerProps {
  type: 'legal' | 'ai' | 'both';
  className?: string;
}

export default function Disclaimer({ type, className = '' }: DisclaimerProps) {
  const showLegal = type === 'legal' || type === 'both';
  const showAI = type === 'ai' || type === 'both';

  return (
    <div className={`bg-yellow-50 border-l-4 border-yellow-400 p-4 ${className}`}>
      <div className="flex">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-yellow-800">Important Disclaimers</h3>
          <div className="mt-2 text-sm text-yellow-700 space-y-2">
            {showLegal && (
              <p>
                <strong>⚖️ Not Legal Advice:</strong> FlashCase is an educational tool designed to help law students study. 
                The content provided through this platform does not constitute legal advice and should not be relied upon 
                for legal decisions. Always consult with a qualified attorney for specific legal matters.
              </p>
            )}
            {showAI && (
              <p>
                <strong>🤖 AI-Generated Content:</strong> This platform uses artificial intelligence to assist with 
                content generation. AI-generated content may contain errors, inaccuracies, or outdated information. 
                Always verify important information with authoritative sources and use AI features as a study aid, 
                not as a definitive legal resource.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
