import { useState } from 'react';
import { RiSparkling2Fill } from "react-icons/ri";

const PromptComponent = () => {
  const [negativePrompt, setNegativePrompt] = useState(false);

  return (
    <div className="w-full p-6 bg-white rounded-[20px] shadow-md mx-auto">
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm font-bold text-left text-[#222]">Prompt</p>
        <div className="flex items-center">
          <input
            type="checkbox"
            id="negativePromptToggle"
            checked={negativePrompt}
            onChange={() => setNegativePrompt(!negativePrompt)}
            className="mr-2"
          />
          <label htmlFor="negativePromptToggle" className="text-xs text-left text-[#464646]">
            Add Negative Prompt
          </label>
        </div>
      </div>
      <textarea
        className="w-full h-[100px] p-4 mb-4 rounded-[10px] bg-[#f8f8f8] border border-[#e6e6e6] text-[#464646] resize-none focus:outline-none"
      />
      {negativePrompt && (
        <>
          <p className="text-sm text-left text-[#222] mb-2">Negative Prompt</p>
          <textarea
            className="w-full h-[100px] p-4 mb-4 rounded-[10px] bg-[#f8f8f8] border border-[#e6e6e6] text-[#464646] resize-none focus:outline-none"
          />
        </>
      )}
      <div className="flex justify-end">
        <button className="flex items-center justify-center px-4 py-2 bg-blue-700 text-white rounded-full">
          <RiSparkling2Fill className="w-[18px] h-[18px] mr-2 transform" />
          <span className="font-bold">Generate</span>
        </button>
      </div>
    </div>
  );
};

export default PromptComponent;
