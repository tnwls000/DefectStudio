import { useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../../store/store';
import Model from '../parameters/Model';
import ImageDimensions from '../parameters/ImageDimensions';
import GeneralSettings from '../parameters/GeneralSettings';
import SamplingSettings from '../parameters/SamplingSettings';
import BatchSettings from '../parameters/BatchSettings';

const Sidebar = () => {
  const level = useSelector((state: RootState) => state.level) as 'Basic' | 'Advanced';
  const [width, setWidth] = useState(512);
  const [height, setHeight] = useState(512);
  const [guidanceScale, setGuidanceScale] = useState(7.5);
  const [samplingSteps, setSamplingSteps] = useState(50);
  const [seed, setSeed] = useState('-1');
  const [isRandomSeed, setIsRandomSeed] = useState(false);
  const [model, setModel] = useState('Stable Diffusion v1-5');
  const [samplingMethod, setSamplingMethod] = useState('DPM++ 2M');
  const [batchCount, setBatchCount] = useState('1');
  const [batchSize, setBatchSize] = useState('1');

  const handleRandomSeedChange = () => {
    setIsRandomSeed(!isRandomSeed);
    setSeed(!isRandomSeed ? '-1' : '');
  };

  return (
    <div className="w-full lg:w-72 h-full fixed-height mr-6">
      <div className="w-full lg:w-72 h-full overflow-y-auto custom-scrollbar rounded-[15px] bg-white shadow-lg border border-gray-300">
        {/* 모델 */}
        <Model model={model} setModel={setModel} />

        {level === 'Advanced' && (
          <>
            <hr className="border-t-[2px] border-[#E6E6E6] w-full" />

            {/* 이미지 크기 */}
            <ImageDimensions width={width} height={height} setWidth={setWidth} setHeight={setHeight} />

            <hr className="border-t-[2px] border-[#E6E6E6] w-full" />

            {/* 샘플링 세팅 */}
            <SamplingSettings
              samplingMethod={samplingMethod}
              samplingSteps={samplingSteps}
              setSamplingSteps={setSamplingSteps}
              setSamplingMethod={setSamplingMethod}
            />

            <hr className="border-t-[2px] border-[#E6E6E6] w-full" />

            {/* 일반 세팅 */}
            <GeneralSettings
              guidanceScale={guidanceScale}
              setGuidanceScale={setGuidanceScale}
              seed={seed}
              setSeed={setSeed}
              isRandomSeed={isRandomSeed}
              handleRandomSeedChange={handleRandomSeedChange}
            />

            <hr className="border-t-[2px] border-[#E6E6E6] w-full" />

            {/* 배치 세팅 */}
            <BatchSettings
              batchCount={batchCount}
              batchSize={batchSize}
              setBatchCount={setBatchCount}
              setBatchSize={setBatchSize}
            />
          </>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
