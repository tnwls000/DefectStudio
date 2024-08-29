import Sidebar from '../sidebar/Txt2ImgSidebar';
import Prompt from '../parameters/Prompt';

const TextToImage = () => {
  return (
    <div className="flex h-[calc(100vh-60px)] bg-gray-100">
      {/* 사이드바 */}
      <div className="w-[340px] p-8 h-full">
        <Sidebar />
      </div>

      {/* 메인 컨텐츠 */}
      <div className="flex-1 flex flex-col justify-end p-8 w-full">
        <div className="mt-auto w-full">
          <Prompt />
        </div>
      </div>
    </div>
  );
};

export default TextToImage;
