import { useState } from 'react';
import { FaSun, FaMoon, FaChevronDown } from 'react-icons/fa';
import { Link } from 'react-router-dom'; // Link를 import 합니다.
import logo from '../../assets/logo.png';
import token from '../../assets/token.png';

const Navbar = () => {
  const [isGenerationDropdownOpen, setGenerationDropdownOpen] = useState(false);
  const [isLevelDropdownOpen, setLevelDropdownOpen] = useState(false);
  const [mode, setMode] = useState<'light' | 'dark'>('light');
  const [level, setLevel] = useState<'Basic' | 'Advanced'>('Basic');

  const toggleGenerationDropdown = () => {
    setGenerationDropdownOpen(!isGenerationDropdownOpen);
  };

  const toggleLevelDropdown = () => {
    setLevelDropdownOpen(!isLevelDropdownOpen);
  };

  const toggleMode = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
    // 추가적으로 다크모드 스타일을 적용하는 코드를 추가할 수 있습니다.
  };

  const selectLevel = (selectedLevel: 'Basic' | 'Advanced') => {
    setLevel(selectedLevel);
    setLevelDropdownOpen(false);
  };

  return (
    <div className="z-50 w-full h-[60px] flex items-center px-10 bg-white shadow-md">
      <Link to={'/'}>
        <div className="flex items-center">
          <img src={logo} className="w-[30px] h-[30px] mr-2 object-cover" alt="logo" />
          <p className="text-xl font-bold text-[#1428a0] font-samsung">Defect Studio</p>
        </div>
      </Link>
      <div className="hidden md:flex ml-10 space-x-8">
        <div className="relative">
          <button
            onClick={toggleGenerationDropdown}
            className="flex items-center text-base text-black cursor-pointer focus:outline-none"
          >
            Generation
          </button>
          {isGenerationDropdownOpen && (
            <div className="absolute mt-2 w-48 bg-white border border-gray-200 rounded-md shadow-lg z-50">
              {[
                { name: 'Text To Image', path: '/generation/text-to-image' },
                { name: 'Image To Image', path: '/generation/image-to-image' },
                { name: 'Inpainting', path: '/generation/inpainting' },
                { name: 'Remove Background', path: '/generation/remove-bg' },
                { name: 'Cleanup', path: '/generation/cleanup' }
              ].map((item) => (
                <Link
                  key={item.name}
                  to={item.path}
                  className="block px-4 py-2 text-sm text-black cursor-pointer hover:bg-gray-100"
                  onClick={() => setGenerationDropdownOpen(false)}
                >
                  {item.name}
                </Link>
              ))}
            </div>
          )}
        </div>
        <Link to="/training" className="text-base text-black cursor-pointer">
          Training
        </Link>
        <Link to="/model" className="text-base text-black cursor-pointer">
          Model
        </Link>
        <Link to="/settings" className="text-base text-black cursor-pointer">
          Settings
        </Link>
        <Link to="/docs" className="text-base text-black cursor-pointer">
          Docs
        </Link>
      </div>
      <div className="flex ml-auto items-center space-x-4">
        <div className="flex items-center">
          <img src={token} className="w-[25px] h-[25px] object-contain" alt="token" />
          <p className="ml-2 text-base font-bold">300</p>
        </div>
        <p className="text-base text-black hidden md:block">정현수</p>
        <div className="relative">
          <button
            onClick={toggleLevelDropdown}
            className="flex items-center justify-between text-base text-black cursor-pointer focus:outline-none"
            style={{ width: '100px' }} // 드롭다운 버튼의 너비를 고정합니다.
          >
            <span>{level}</span>
            <FaChevronDown className="ml-2" />
          </button>
          {isLevelDropdownOpen && (
            <div className="absolute right-0 mt-2 w-32 bg-white border border-gray-200 rounded-md shadow-lg">
              <div
                className="block px-4 py-2 text-sm text-black cursor-pointer hover:bg-gray-100"
                onClick={() => selectLevel('Basic')}
              >
                Basic
              </div>
              <div
                className="block px-4 py-2 text-sm text-black cursor-pointer hover:bg-gray-100"
                onClick={() => selectLevel('Advanced')}
              >
                Advanced
              </div>
            </div>
          )}
        </div>
        <button onClick={toggleMode} className="text-black focus:outline-none">
          {mode === 'light' ? <FaSun className="w-6 h-6" /> : <FaMoon className="w-6 h-6" />}
        </button>
      </div>
    </div>
  );
};

export default Navbar;
