import React, { useState, FormEvent } from 'react';

interface SearchBarProps {
    onSearch: (username: string) => void;
    loading: boolean;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch, loading }) => {
  const [username, setUsername] = useState<string>('');

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (username.trim()) {
      onSearch(username);
    }
  };

    return (

      <div className="w-full max-w-lg mx-auto mb-16">

        <form onSubmit={handleSubmit} className="relative group">

          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">

              <svg className="h-5 w-5 text-gray-400 group-focus-within:text-gray-800 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">

                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />

              </svg>

          </div>

          <input

            className="block w-full bg-gray-50 text-gray-900 rounded-2xl py-4 pl-12 pr-32 focus:outline-none focus:bg-white focus:ring-2 focus:ring-gray-100 focus:shadow-lg transition-all duration-300 text-lg placeholder-gray-400"

            type="text"

            placeholder="Enter GitHub Username..."

            aria-label="GitHub Username"

            value={username}

            onChange={(e) => setUsername(e.target.value)}

            disabled={loading}

          />

          <button

            className={`absolute right-2 top-2 bottom-2 bg-black hover:bg-gray-800 text-white font-medium rounded-xl px-6 transition-all duration-300 ${loading ? 'opacity-75 cursor-wait' : ''}`}

            type="submit"

            disabled={loading}

          >

            {loading ? (

                <span className="flex items-center gap-2">

                    <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">

                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>

                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>

                    </svg>

                    Processing

                </span>

            ) : 'Analyze'}

          </button>

        </form>

      </div>

    );

  };

export default SearchBar;
