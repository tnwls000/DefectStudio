import { Routes, Route } from 'react-router-dom';
import TextToImage from '../components/generation/TextToImage';
import ImageToImage from '../components/generation/ImageToImage';
import Inpainting from '../components/generation/Inpainting'
import RemoveBackground from '../components/generation/RemoveBackground';
import Cleanup from '../components/generation/Cleanup';

const Generation = () => {
  return (
    <Routes>
      <Route path="text-to-image" element={<TextToImage />} />
      <Route path="image-to-image" element={<ImageToImage />} />
      <Route path="inpainting" element={<Inpainting />} />
      <Route path="remove-background" element={<RemoveBackground />} />
      <Route path="cleanup" element={<Cleanup />} />
    </Routes>
  );
};

export default Generation;
