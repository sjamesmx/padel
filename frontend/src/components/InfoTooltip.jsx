import { useState } from 'react';
import { Info } from 'lucide-react';

export default function InfoTooltip({ content, position = "top" }) {
  const [isVisible, setIsVisible] = useState(false);

  const positionClasses = {
    top: "bottom-full left-1/2 transform -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 transform -translate-x-1/2 mt-2",
    left: "right-full top-1/2 transform -translate-y-1/2 mr-2",
    right: "left-full top-1/2 transform -translate-y-1/2 ml-2",
  };

  return (
    <div className="relative inline-block">
      <button
        className="text-gray-400 hover:text-white transition-colors focus:outline-none"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onClick={() => setIsVisible(!isVisible)}
      >
        <Info className="w-4 h-4" />
      </button>
      {isVisible && (
        <div
          className={`absolute ${positionClasses[position]} z-50 w-48 p-2 bg-noir-eclipse text-white text-xs rounded-lg shadow-lg border border-royal-nebula/30`}
        >
          {content}
        </div>
      )}
    </div>
  );
}