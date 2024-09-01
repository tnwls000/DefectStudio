import { useState, useEffect } from 'react';
import { Button } from 'antd';
import { FormatPainterOutlined } from '@ant-design/icons';
import { useFabric } from '../../../contexts/FabricContext';
import InpaintingModal from '../masking/InpaintingModal';
import UploadImagePlusMask from '../parameters/UploadImagePlusMask';

const CleanupSidebar: React.FC = () => {
  const {
    imageDownloadUrl,
    canvasDownloadUrl,
    maskingResult,
    setMaskingResult
  } = useFabric();

  const [showModal, setShowModal] = useState(false);
  const [, setHeight] = useState(512);
  const [, setWidth] = useState(512);
  const [imageSrc, setImageSrc] = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState<string>('manual');

  // 탭 들어가면 MaskingResult 리셋되야함
  useEffect(() => {
    setMaskingResult(null);
  }, [setMaskingResult]);

  const handleImageUpload = (file: File) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const img = new Image();
      img.onload = () => {
        let newWidth = img.width;
        let newHeight = img.height;

        if (img.width > img.height) {
          newWidth = 512;
          newHeight = (img.height / img.width) * 512;
        } else {
          newHeight = 512;
          newWidth = (img.width / img.height) * 512;
        }

        setWidth(newWidth);
        setHeight(newHeight);
        setImageSrc(reader.result as string);
      };
      img.src = reader.result as string;
    };
    reader.readAsDataURL(file);
  };

  const handleDownloadImage = (url: string | null, filename: string) => {
    if (url) {
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleDownloadCanvasImage = () => {
    handleDownloadImage(canvasDownloadUrl, 'canvas.png');
  };

  const handleDownloadBackgroundImage = () => {
    handleDownloadImage(imageDownloadUrl, 'image.png');
  };

  return (
    <div className="w-full lg:w-72 h-full fixed-height mr-6">
      <div className="w-full lg:w-72 h-full overflow-y-auto custom-scrollbar rounded-[15px] bg-white shadow-lg border border-gray-300">
        {/* 이미지 업로드 */}
        <UploadImagePlusMask
          handleImageUpload={handleImageUpload}
          imagePreview={imageSrc}
          inpaintingResult={maskingResult}
          handleDownloadImage={handleDownloadImage}
          setActiveTab={setActiveTab}
        />

        {imageSrc && (
          <div className="px-6 pb-10">
            {/* Start Masking 버튼 (배치 모드가 아닐 때만 보임) */}
            {activeTab === 'manual' && (
              <Button
                type="primary"
                icon={<FormatPainterOutlined />}
                onClick={() => setShowModal(true)}
                className="w-full mt-2"
              >
                Start Masking
              </Button>
            )}

            {/* 인페인팅 작업 결과 이미지 표시 및 다운로드 버튼 */}
            {activeTab === 'manual' && maskingResult && (
              <div className="relative w-full pb-[61.8%] bg-gray-100 border border-dashed border-gray-300 rounded-lg mt-4 flex items-center justify-center">
                <img
                  src={maskingResult}
                  alt="Inpainting Result"
                  className="absolute top-0 left-0 w-full h-full object-cover rounded-lg"
                />

                {/* 다운로드 버튼 - 테스트용!!! */}
                <div className="mt-2 flex gap-2 flex-col">
                  <Button type="default" onClick={handleDownloadCanvasImage} className="w-full">
                    Download Canvas Image
                  </Button>

                  <Button type="default" onClick={handleDownloadBackgroundImage} className="w-full">
                    Download Background Image
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Inpainting 모달 창 */}
      {showModal && imageSrc && <InpaintingModal imageSrc={imageSrc} onClose={() => setShowModal(false)} />}
    </div>
  );
};

export default CleanupSidebar;
