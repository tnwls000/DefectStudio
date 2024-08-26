import { useState } from 'react';

const Sidebar: React.FC = () => {
  const [width, setWidth] = useState(512);
  const [height, setHeight] = useState(512);
  const [guidanceScale, setGuidanceScale] = useState(7.5);
  const [samplingSteps, setSamplingSteps] = useState(50);
  const [seed, setSeed] = useState('');
  const [isRandomSeed, setIsRandomSeed] = useState(false);
  const [model, setModel] = useState('Stable Diffusion v1-5');
  const [samplingMethod, setSamplingMethod] = useState('DPM++ 2M');

  const handleRandomSeedChange = () => {
    setIsRandomSeed(!isRandomSeed);
    setSeed(!isRandomSeed ? '-1' : '');
  };

  return (
    <div className="w-full lg:w-80 mr-8">  
      <div className="w-full lg:w-80 h-full max-h-[calc(100vh-120px)] overflow-y-auto custom-scrollbar rounded-[20px] bg-white shadow-md">
        <p className="p-4 text-lg font-bold text-[#222]">Text To Image</p>

        <hr className="border-t-[2px] border-[#E6E6E6] w-full" />

        <div className="p-4">
          <p className="text-sm font-bold text-[#222] mb-2">Model</p>
          <div className="bg-[#f8f8f8] rounded-md p-3 flex items-center justify-between cursor-pointer">
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="bg-transparent text-sm text-[#464646] focus:outline-none w-full"
            >
              <option value="Stable Diffusion v1-5">Stable Diffusion v1-5</option>
              <option value="Stable Diffusion v2-1">Stable Diffusion v2-1</option>
              <option value="Custom Model">Custom Model</option>
            </select>
          </div>
        </div>

        <hr className="border-t-[2px] border-[#E6E6E6] w-full" />

        <div className="p-4">
          <p className="text-sm font-bold text-[#222] mb-2">Image Dimensions</p>
          <div className="mb-4">
            <p className="text-sm text-[#464646] mb-1">Width</p>
            <div className="relative flex items-center">
              <input
                type="range"
                min="128"
                max="2048"
                value={width}
                onChange={(e) => setWidth(parseInt(e.target.value))}
                className="w-full"
              />
              <input
                type="number"
                min="128"
                max="2048"
                value={width}
                onChange={(e) => setWidth(parseInt(e.target.value))}
                className="w-16 ml-2 p-1 text-sm text-right bg-[#f8f8f8] border border-gray-300 rounded-md"
              />
            </div>
          </div>
          <div>
            <p className="text-sm text-[#464646] mb-1">Height</p>
            <div className="relative flex items-center">
              <input
                type="range"
                min="128"
                max="2048"
                value={height}
                onChange={(e) => setHeight(parseInt(e.target.value))}
                className="w-full"
              />
              <input
                type="number"
                min="128"
                max="2048"
                value={height}
                onChange={(e) => setHeight(parseInt(e.target.value))}
                className="w-16 ml-2 p-1 text-sm text-right bg-[#f8f8f8] border border-gray-300 rounded-md"
              />
            </div>
          </div>
        </div>

        <hr className="border-t-[2px] border-[#E6E6E6] w-full" />

        <div className="p-4">
          <p className="text-sm font-bold text-[#222] mb-2">Generation Settings</p>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-[#464646] mb-1">Guidance Scale</p>
              <div className="relative flex items-center">
                <input
                  type="range"
                  min="1.0"
                  max="30.0"
                  step="0.1"
                  value={guidanceScale}
                  onChange={(e) => setGuidanceScale(parseFloat(e.target.value))}
                  className="w-full"
                />
                <input
                  type="number"
                  min="1.0"
                  max="30.0"
                  step="0.1"
                  value={guidanceScale}
                  onChange={(e) => setGuidanceScale(parseFloat(e.target.value))}
                  className="w-16 ml-2 p-1 text-sm text-right bg-[#f8f8f8] border border-gray-300 rounded-md"
                />
              </div>
            </div>
            <div>
              <p className="text-sm text-[#464646] mb-1">Sampling Steps</p>
              <div className="relative flex items-center">
                <input
                  type="range"
                  min="10"
                  max="150"
                  value={samplingSteps}
                  onChange={(e) => setSamplingSteps(parseInt(e.target.value))}
                  className="w-full"
                />
                <input
                  type="number"
                  min="10"
                  max="150"
                  value={samplingSteps}
                  onChange={(e) => setSamplingSteps(parseInt(e.target.value))}
                  className="w-16 ml-2 p-1 text-sm text-right bg-[#f8f8f8] border border-gray-300 rounded-md"
                />
              </div>
            </div>
            <div>
              <p className="text-sm text-[#464646] mb-1">Seed</p>
              <div className="flex flex-col gap-1">
                <input
                  type="text"
                  value={seed}
                  onChange={(e) => setSeed(e.target.value)}
                  disabled={isRandomSeed}
                  className="w-full p-2 bg-[#f8f8f8] border border-gray-300 rounded-md"
                />
                <div className="flex items-center">
                  <input type="checkbox" checked={isRandomSeed} onChange={handleRandomSeedChange} />
                  <label className="ml-1 text-sm text-[#464646]">random</label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <hr className="border-t-[2px] border-[#E6E6E6] w-full" />

        <div className="p-4">
          <p className="text-sm font-bold text-[#222] mb-2">Sampling Method</p>
          <div className="bg-[#f8f8f8] rounded-md p-3 flex items-center justify-between cursor-pointer">
            <select
              value={samplingMethod}
              onChange={(e) => setSamplingMethod(e.target.value)}
              className="bg-transparent text-sm text-[#464646] focus:outline-none w-full"
            >
              <option value="DPM++ 2M">DPM++ 2M</option>
              <option value="Euler a">Euler a</option>
              <option value="LMS">LMS</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
