import { useState } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import TextToImage from '../components/generation/layouts/TextToImage';
import ImageToImage from '../components/generation/layouts/ImageToImage';
import Inpainting from '../components/generation/layouts/Inpainting';
import RemoveBackground from '../components/generation/layouts/RemoveBackground';
import Cleanup from '../components/generation/layouts/Cleanup';
import { AiOutlineMenuFold, AiOutlineMenuUnfold } from 'react-icons/ai';
import { FaImage, FaMagic, FaPaintBrush, FaEraser, FaTrash } from 'react-icons/fa';

const Generation = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="flex h-[calc(100vh-60px)] bg-gray-100">
      {/* 사이드 메뉴탭 선택 */}
      <div
        className={`py-8 fixed top-0 left-0 bg-white shadow-lg z-20 h-full transition-transform duration-300 ease-in-out ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} w-20`}
        style={{ top: '60px' }}
      >
        <nav className="flex flex-col items-center space-y-6">
          <Link
            to="text-to-image"
            className="flex flex-col items-center text-gray-500 hover:text-gray-900 hover:bg-gray-200 transition duration-300 px-4 w-full py-2"
          >
            <FaImage className="text-xl" />
            <span className="text-xs mt-1">Txt2Img</span>
          </Link>
          <Link
            to="image-to-image"
            className="flex flex-col items-center text-gray-500 hover:text-gray-900 hover:bg-gray-200 transition duration-300 px-4 w-full py-2"
          >
            <FaMagic className="text-xl" />
            <span className="text-xs mt-1">Img2Img</span>
          </Link>
          <Link
            to="inpainting"
            className="flex flex-col items-center text-gray-500 hover:text-gray-900 hover:bg-gray-200 transition duration-300 px-4 w-full py-2"
          >
            <FaPaintBrush className="text-xl" />
            <span className="text-xs mt-1">Inpaint</span>
          </Link>
          <Link
            to="remove-background"
            className="flex flex-col items-center text-gray-500 hover:text-gray-900 hover:bg-gray-200 transition duration-300 px-4 w-full py-2"
          >
            <FaEraser className="text-xl" />
            <span className="text-xs mt-1 text-center">Remove BG</span>
          </Link>
          <Link
            to="cleanup"
            className="flex flex-col items-center text-gray-500 hover:text-gray-900 hover:bg-gray-200 transition duration-300 px-4 w-full py-2"
          >
            <FaTrash className="text-xl" />
            <span className="text-xs mt-1">Cleanup</span>
          </Link>
        </nav>
      </div>

      {/* 사이드 닫고열기 버튼 */}
      <button
        onClick={toggleSidebar}
        className="fixed bottom-4 left-4 w-12 h-12 rounded-full bg-white shadow-lg border border-[#757575] flex items-center justify-center z-30 focus:outline-none"
      >
        {isSidebarOpen ? (
          <AiOutlineMenuUnfold className="text-gray-500 text-2xl" />
        ) : (
          <AiOutlineMenuFold className="text-gray-500 text-2xl" />
        )}
      </button>

      {/* 메인 컴포넌트 렌더링 */}
      <div
        className={`flex-1 transition-all duration-300 ${isSidebarOpen ? 'ml-20' : 'ml-0'} h-full bg-gray-100`}
        style={{ marginLeft: isSidebarOpen ? '80px' : '0' }}
      >
        <Routes>
          <Route path="text-to-image" element={<TextToImage />} />
          <Route path="image-to-image" element={<ImageToImage />} />
          <Route path="inpainting" element={<Inpainting />} />
          <Route path="remove-background" element={<RemoveBackground />} />
          <Route path="cleanup" element={<Cleanup />} />
        </Routes>
      </div>
    </div>
  );
};

export default Generation;
