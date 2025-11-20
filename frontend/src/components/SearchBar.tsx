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
    <div className="w-full max-w-md mx-auto mb-12">
      <form onSubmit={handleSubmit} className="flex items-center border-b border-gray-300 py-2 transition-colors focus-within:border-black">
        <input 
          className="appearance-none bg-transparent border-none w-full text-gray-700 mr-3 py-1 px-2 leading-tight focus:outline-none font-light text-xl" 
          type="text" 
          placeholder="Enter GitHub Username" 
          aria-label="GitHub Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled={loading}
        />
        <button 
          className={`flex-shrink-0 bg-black hover:bg-gray-800 text-white text-sm py-2 px-6 rounded-full transition-all duration-300 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          type="submit"
          disabled={loading}
        >
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>
    </div>
  );
};

export default SearchBar;
