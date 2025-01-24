"use client";

import { FormEvent, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import SuggestionsList from "./SuggestionsList";

interface SearchBarProps {
  suggestions: string[];
  onSearch: (ticker: string) => void;
}

export default function SearchBar({ suggestions, onSearch }: SearchBarProps) {
  const router = useRouter();
  const [inputValue, setInputValue] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);

  const filteredSuggestions = suggestions.filter((ticker) =>
    ticker.toLowerCase().includes(inputValue.toLowerCase())
  );

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const selectedTicker = inputValue.toUpperCase().trim();
    if (suggestions.includes(selectedTicker)) {
      onSearch(selectedTicker);
      setInputValue("");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-8 relative">
      <div className="relative flex items-center">
        <input
          type="text"
          placeholder="Search for a stock symbol..."
          className="w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none text-white placeholder-gray-400 transition-all"
          value={inputValue}
          onChange={(e) => {
            setInputValue(e.target.value.toUpperCase());
            setShowSuggestions(true);
          }}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 100)}
        />
        <button
          type="submit"
          className="ml-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors flex items-center"
        >
          <SearchIcon />
          Search
        </button>
      </div>

      {showSuggestions && inputValue && filteredSuggestions.length > 0 && (
        <SuggestionsList
          suggestions={filteredSuggestions}
          onSelect={(suggestion) => {
            onSearch(suggestion);
            setInputValue("");
          }}
        />
      )}
    </form>
  );
}

const SearchIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className="h-5 w-5 mr-2"
    viewBox="0 0 20 20"
    fill="currentColor"
  >
    <path
      fillRule="evenodd"
      d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
      clipRule="evenodd"
    />
  </svg>
);
