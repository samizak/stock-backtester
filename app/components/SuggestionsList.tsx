"use client";

interface SuggestionsListProps {
  suggestions: string[];
  onSelect: (suggestion: string) => void;
}

export default function SuggestionsList({
  suggestions,
  onSelect,
}: SuggestionsListProps) {
  return (
    <div className="absolute top-full left-0 right-0 mt-2 bg-gray-800 rounded-lg shadow-lg z-10">
      {suggestions.map((suggestion) => (
        <button
          key={suggestion}
          type="button"
          className="w-full px-4 py-2 text-left text-white hover:bg-gray-700 transition-colors"
          onMouseDown={() => onSelect(suggestion)}
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
}
