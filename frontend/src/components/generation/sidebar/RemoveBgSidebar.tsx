import { useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../../store/store';
import UploadImage from '../parameters/UploadImage';


const RemoveBgSidebar = () => {
  const level = useSelector((state: RootState) => state.level) as 'Basic' | 'Advanced';

  const [uploadedImage, setUploadedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | ArrayBuffer | null>(null);

  const handleImageUpload = (file: File) => {
    setUploadedImage(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="w-full lg:w-72 h-full fixed-height mr-6">
      <div className="w-full lg:w-72 h-full overflow-y-auto custom-scrollbar rounded-[15px] bg-white shadow-lg border border-gray-300">

        {/* 이미지 업로드 */}
        <UploadImage handleImageUpload={handleImageUpload} imagePreview={imagePreview} />

      </div>
    </div>
  );
};

export default RemoveBgSidebar;
