import { useRef, useEffect, useState } from 'react';

interface InpaintingModalProps {
  imageSrc: string;
  onApply: (canvas: HTMLCanvasElement) => void;
  onClose: () => void;
  width: number;
  height: number;
}

const InpaintingModal = ({ imageSrc, onApply, onClose, width, height }: InpaintingModalProps) => {
  const imageCanvasRef = useRef<HTMLCanvasElement>(null);
  const drawingCanvasRef = useRef<HTMLCanvasElement>(null);
  const cursorRef = useRef<HTMLDivElement>(null);

  const [isPainting, setIsPainting] = useState(false);
  const [brushSize, setBrushSize] = useState(10);
  const [tool, setTool] = useState<'brush' | 'eraser' | 'polygon' | 'move'>('brush');
  const [pixelMatrix, setPixelMatrix] = useState<number[][] | null>(null);
  const [polygonPoints, setPolygonPoints] = useState<{ x: number; y: number }[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedPointIndex, setSelectedPointIndex] = useState<number | null>(null);

  useEffect(() => {
    if (imageCanvasRef.current && drawingCanvasRef.current) {
      const intWidth = Math.floor(width);
      const intHeight = Math.floor(height);

      if (intWidth > 0 && intHeight > 0) {
        const initialMatrix = Array.from({ length: intHeight }, () => Array(intWidth).fill(0));
        setPixelMatrix(initialMatrix);

        const ctx = imageCanvasRef.current.getContext('2d');
        const img = new Image();

        img.onload = () => {
          ctx?.clearRect(0, 0, imageCanvasRef.current!.width, imageCanvasRef.current!.height);
          ctx?.drawImage(img, 0, 0, imageCanvasRef.current!.width, imageCanvasRef.current!.height);
        };

        img.src = imageSrc;
      } else {
        console.error('Invalid canvas dimensions: width and height must be positive integers.');
      }
    }
  }, [imageSrc, width, height]);

  const startPainting = (event: React.MouseEvent) => {
    if (tool === 'polygon' && !isDragging) {
      const rect = drawingCanvasRef.current!.getBoundingClientRect();
      const scaleX = drawingCanvasRef.current!.width / rect.width;
      const scaleY = drawingCanvasRef.current!.height / rect.height;
      const x = Math.floor((event.clientX - rect.left) * scaleX);
      const y = Math.floor((event.clientY - rect.top) * scaleY);
      setPolygonPoints([...polygonPoints, { x, y }]);
    } else if (tool === 'move' && selectedPointIndex !== null) {
      setIsDragging(true);
    } else {
      setIsPainting(true);
      paint(event);
    }
  };

  const endPainting = () => {
    setIsDragging(false);
    setSelectedPointIndex(null);
    setIsPainting(false);
  };

  const movePolygonPoint = (event: React.MouseEvent) => {
    if (isDragging && selectedPointIndex !== null) {
      const rect = drawingCanvasRef.current!.getBoundingClientRect();
      const scaleX = drawingCanvasRef.current!.width / rect.width;
      const scaleY = drawingCanvasRef.current!.height / rect.height;
      const x = Math.floor((event.clientX - rect.left) * scaleX);
      const y = Math.floor((event.clientY - rect.top) * scaleY);
      const newPoints = [...polygonPoints];
      newPoints[selectedPointIndex] = { x, y };
      setPolygonPoints(newPoints);
      updatePolygonMatrix();
    }
  };

  const paint = (event: React.MouseEvent) => {
    if (!isPainting || !drawingCanvasRef.current || !pixelMatrix) return;

    const canvas = drawingCanvasRef.current;
    const ctx = canvas.getContext('2d');

    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const x = Math.floor((event.clientX - rect.left) * scaleX);
    const y = Math.floor((event.clientY - rect.top) * scaleY);

    const radius = Math.floor(brushSize / 2);

    for (let i = -radius; i <= radius; i++) {
      for (let j = -radius; j <= radius; j++) {
        const newX = x + i;
        const newY = y + j;

        if (newX >= 0 && newX < pixelMatrix[0].length && newY >= 0 && newY < pixelMatrix.length) {
          const distance = Math.sqrt(i * i + j * j);
          if (distance <= radius) {
            if (tool === 'brush') {
              pixelMatrix[newY][newX] = 1;
            } else if (tool === 'eraser') {
              pixelMatrix[newY][newX] = 0;
            }
          }
        }
      }
    }

    updateCanvasFromMatrix();
  };

  const updatePolygonMatrix = () => {
    if (!drawingCanvasRef.current || !pixelMatrix) return;
    const ctx = drawingCanvasRef.current.getContext('2d');
    if (!ctx || polygonPoints.length < 3) return;

    for (let y = 0; y < pixelMatrix.length; y++) {
      for (let x = 0; x < pixelMatrix[y].length; x++) {
        pixelMatrix[y][x] = 0;
      }
    }

    ctx.clearRect(0, 0, drawingCanvasRef.current.width, drawingCanvasRef.current.height);

    ctx.save();
    ctx.beginPath();
    polygonPoints.forEach((point, index) => {
      if (index === 0) {
        ctx.moveTo(point.x, point.y);
      } else {
        ctx.lineTo(point.x, point.y);
      }
    });
    ctx.closePath();
    ctx.clip();

    const imgData = ctx.getImageData(0, 0, drawingCanvasRef.current.width, drawingCanvasRef.current.height);
    for (let y = 0; y < imgData.height; y++) {
      for (let x = 0; x < imgData.width; x++) {
        const idx = (y * imgData.width + x) * 4;
        if (ctx.isPointInPath(x, y)) {
          pixelMatrix[y][x] = 1;
        }
      }
    }

    ctx.restore();
    updateCanvasFromMatrix();
  };

  const updateCanvasFromMatrix = () => {
    if (!drawingCanvasRef.current || !pixelMatrix) return;
    const ctx = drawingCanvasRef.current.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, drawingCanvasRef.current.width, drawingCanvasRef.current.height);

    for (let y = 0; y < pixelMatrix.length; y++) {
      for (let x = 0; x < pixelMatrix[y].length; x++) {
        if (pixelMatrix[y][x] === 1) {
          ctx.fillStyle = 'rgba(255, 255, 0, 0.3)';
          ctx.fillRect(x, y, 1, 1);
        }
      }
    }
  };

  const handleMouseMove = (event: React.MouseEvent) => {
    if (cursorRef.current) {
      const rect = drawingCanvasRef.current?.getBoundingClientRect();
      if (rect) {
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        cursorRef.current.style.left = `${x - brushSize / 2}px`;
        cursorRef.current.style.top = `${y - brushSize / 2}px`;
      }

      if (isPainting) {
        paint(event);
      } else if (isDragging) {
        movePolygonPoint(event);
      }
    }
  };

  const handleMouseLeave = () => {
    setIsDragging(false);
    setIsPainting(false);
    if (cursorRef.current) {
      cursorRef.current.style.display = 'none';
    }
  };

  const handleMouseEnter = () => {
    if (cursorRef.current) {
      cursorRef.current.style.display = 'block';
    }
  };

  const handleApply = () => {
    if (drawingCanvasRef.current) {
      onApply(drawingCanvasRef.current);
    }
  };

  const selectPointForMovement = (index: number) => {
    if (tool === 'move') {
      setSelectedPointIndex(index);
      setIsDragging(true);
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50" onClick={onClose}>
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-4xl relative" onClick={(e) => e.stopPropagation()}>
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-600 hover:text-gray-900">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
            className="w-6 h-6"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <h2 className="text-2xl font-semibold mb-4">Inpainting</h2>
        <div
          className="relative"
          style={{ width: width, height: height }}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          onMouseEnter={handleMouseEnter}
        >
          <canvas
            ref={imageCanvasRef}
            width={Math.floor(width)}
            height={Math.floor(height)}
            className="absolute top-0 left-0 border border-gray-300 rounded"
          />
          <canvas
            ref={drawingCanvasRef}
            width={Math.floor(width)}
            height={Math.floor(height)}
            className="absolute top-0 left-0 border border-gray-300 rounded"
            onMouseDown={startPainting}
            onMouseUp={endPainting}
          />
          <div
            ref={cursorRef}
            style={{
              position: 'absolute',
              width: `${brushSize}px`,
              height: `${brushSize}px`,
              borderRadius: '50%',
              pointerEvents: 'none',
              backgroundColor: tool === 'brush' ? 'rgba(255, 255, 0, 0.3)' : 'transparent',
              border: tool === 'eraser' ? '1px solid black' : 'none',
              display: 'none'
            }}
          />
          {polygonPoints.map((point, index) => (
            <div
              key={index}
              style={{
                position: 'absolute',
                top: point.y - 5,
                left: point.x - 5,
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: 'orange',
                cursor: tool === 'move' ? 'move' : 'pointer'
              }}
              onMouseDown={() => selectPointForMovement(index)}
            />
          ))}
        </div>
        <div className="flex justify-between items-end mt-4">
          <div className="flex justify-between items-center mt-4 space-x-4">
            <div className="flex items-center space-x-2">
              <label htmlFor="brushSize" className="text-sm font-medium">
                Size:
              </label>
              <input
                type="range"
                min="1"
                max="50"
                value={brushSize}
                onChange={(e) => setBrushSize(Number(e.target.value))}
                className="slider w-36"
              />
              <input
                id="brushSize"
                type="number"
                min="1"
                max="50"
                value={brushSize}
                onChange={(e) => setBrushSize(Number(e.target.value))}
                className="w-16 p-1 border border-gray-300 rounded-md text-center"
              />
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => setTool('brush')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${tool === 'brush' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
              >
                Brush
              </button>
              <button
                onClick={() => setTool('eraser')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${tool === 'eraser' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
              >
                Eraser
              </button>
              <button
                onClick={() => setTool('polygon')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${tool === 'polygon' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
              >
                Polygon
              </button>
              <button
                onClick={() => setTool('move')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${tool === 'move' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
              >
                Hand
              </button>
            </div>
          </div>

          <div className="flex space-x-4">
            <button
              onClick={handleApply}
              className="px-4 h-[40px] bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
            >
              Apply
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InpaintingModal;

