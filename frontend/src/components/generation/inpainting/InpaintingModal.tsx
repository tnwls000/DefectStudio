import { useRef, useState, useEffect, useCallback } from 'react';
import { Modal, Button, Slider, Tooltip } from 'antd';
import { Eraser, Brush, Triangle, Move } from 'lucide-react';

interface InpaintingModalProps {
  imageSrc: string;
  onClose: () => void;
  onApply: (maskCanvas: HTMLCanvasElement) => void;
  width: number;
  height: number;
}

const InpaintingModal: React.FC<InpaintingModalProps> = ({ imageSrc, onClose, onApply, width, height }) => {
  const [isDrawing, setIsDrawing] = useState(false);
  const [isErasing, setIsErasing] = useState(false);
  const [isPolygonMode, setIsPolygonMode] = useState(false);
  const [polygonPoints, setPolygonPoints] = useState<{ x: number; y: number }[]>([]);
  const [isMovingPolygonPoints, setIsMovingPolygonPoints] = useState(false);
  const [selectedPointIndex, setSelectedPointIndex] = useState<number | null>(null);
  const [baseBrushSize, setBaseBrushSize] = useState(20);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const maskCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const contextRef = useRef<CanvasRenderingContext2D | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const maskCanvas = maskCanvasRef.current;
    if (canvas && maskCanvas) {
      const ctx = canvas.getContext('2d');
      const maskCtx = maskCanvas.getContext('2d');
      if (ctx && maskCtx) {
        contextRef.current = maskCtx;
        const img = new Image();
        img.onload = () => {
          ctx.drawImage(img, 0, 0, width, height);
        };
        img.src = imageSrc;
      }
    }
  }, [imageSrc, width, height]);

  const startDrawing = useCallback(
    (event: React.MouseEvent<HTMLCanvasElement>) => {
      if (isPolygonMode) {
        const rect = (event.target as HTMLCanvasElement).getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        // 폴리곤 모드에서는 점을 추가하고 시각적으로 노란색으로만 표시합니다.
        setPolygonPoints((prevPoints) => [...prevPoints, { x, y }]);

        return; // 폴리곤 모드에서는 브러쉬 그리기를 하지 않음
      }

      setIsDrawing(true);
      contextRef.current?.beginPath();

      const rect = (event.target as HTMLCanvasElement).getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;

      contextRef.current?.moveTo(x, y);
    },
    [isPolygonMode]
  );

  const stopDrawing = useCallback(() => {
    setIsDrawing(false);
    contextRef.current?.closePath();
  }, []);

  const draw = useCallback(
    (event: React.MouseEvent<HTMLCanvasElement>) => {
      if (!isDrawing || !contextRef.current || isPolygonMode) return;

      const rect = (event.target as HTMLCanvasElement).getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;

      const context = contextRef.current;
      context.lineWidth = baseBrushSize;
      context.lineCap = 'round';

      if (isErasing) {
        context.globalCompositeOperation = 'destination-out'; // 지우개 모드
        context.strokeStyle = 'rgba(0, 0, 0, 1)';
      } else {
        context.globalCompositeOperation = 'source-over'; // 그리기 모드
        context.strokeStyle = 'rgba(255, 0, 0, 0.5)'; // 반투명한 빨간색으로 마스킹
      }

      context.lineTo(x, y);
      context.stroke();
    },
    [isDrawing, baseBrushSize, isErasing, isPolygonMode]
  );

  const drawPolygon = useCallback(() => {
    if (polygonPoints.length >= 3 && contextRef.current) {
      const context = contextRef.current;

      // 폴리곤을 그리되, 꼭짓점들은 노란색으로 유지
      context.clearRect(0, 0, width, height); // 이전에 그려진 폴리곤을 지움
      context.globalCompositeOperation = 'source-over';
      context.fillStyle = 'rgba(255, 0, 0, 0.5)';

      context.beginPath();
      context.moveTo(polygonPoints[0].x, polygonPoints[0].y);
      polygonPoints.forEach((point) => context.lineTo(point.x, point.y));
      context.closePath();
      context.fill();

      // 폴리곤을 그리고 나서 점을 다시 그려서 꼭짓점이 노란색으로 보이도록 함
      polygonPoints.forEach((point) => {
        context.beginPath();
        context.arc(point.x, point.y, 4, 0, 2 * Math.PI, false);
        context.fillStyle = 'yellow';
        context.fill();
        context.stroke();
      });
    }
  }, [polygonPoints, width, height]);

  const drawPoints = useCallback(() => {
    if (contextRef.current) {
      const context = contextRef.current;

      // 배경을 지우지 않고 점만 그리도록 설정
      polygonPoints.forEach((point) => {
        context.beginPath();
        context.arc(point.x, point.y, 4, 0, 2 * Math.PI, false); // 점의 반지름을 4px로 설정
        context.fillStyle = 'yellow'; // 점 색상 설정
        context.fill();
        context.stroke();
      });

      drawPolygon(); // 새로운 점이 추가되면 폴리곤도 새로 그려짐
    }
  }, [polygonPoints, drawPolygon]);

  useEffect(() => {
    drawPoints();
  }, [polygonPoints, drawPoints]);

  const movePolygonPoint = useCallback(
    (event: React.MouseEvent<HTMLCanvasElement>) => {
      if (!isMovingPolygonPoints || selectedPointIndex === null || !contextRef.current) return;

      const rect = (event.target as HTMLCanvasElement).getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;

      const updatedPoints = [...polygonPoints];
      updatedPoints[selectedPointIndex] = { x, y };
      setPolygonPoints(updatedPoints);
    },
    [isMovingPolygonPoints, selectedPointIndex, polygonPoints]
  );

  const selectPolygonPoint = useCallback(
    (event: React.MouseEvent<HTMLCanvasElement>) => {
      if (!isMovingPolygonPoints) return;

      const rect = (event.target as HTMLCanvasElement).getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;

      const closestPointIndex = polygonPoints.findIndex(
        (point) => Math.hypot(point.x - x, point.y - y) < 8 // 점의 반경과 동일하게 설정
      );

      if (closestPointIndex !== -1) {
        setSelectedPointIndex(closestPointIndex);
      } else {
        setSelectedPointIndex(null);
      }
    },
    [isMovingPolygonPoints, polygonPoints]
  );

  const handleApply = useCallback(() => {
    if (polygonPoints.length >= 3) {
      drawPolygon(); // 폴리곤이 완성되지 않았을 경우 마지막으로 한 번 더 그려줌
    }
    if (maskCanvasRef.current) {
      onApply(maskCanvasRef.current);
    }
  }, [onApply, drawPolygon, polygonPoints.length]);

  return (
    <Modal
      title={null} // 타이틀 제거
      open={true}
      onCancel={onClose}
      footer={[
        <Button key="cancel" onClick={onClose}>
          Cancel
        </Button>,
        <Button key="apply" type="primary" onClick={handleApply}>
          Save
        </Button>,
      ]}
      width={width + 160} // 캔버스 너비에 도구 버튼을 포함하도록 조정
      centered // 모달을 화면 중앙에 배치
    >
      <div className="relative" style={{ width: `${width + 160}px`, height: `${height + 100}px` }}>
        {/* 도구 버튼을 오른쪽에 배치 */}
        <div className="absolute top-4 right-4 flex flex-col items-center gap-4 z-20">
          <Tooltip title="Brush">
            <Button
              type={!isErasing && !isPolygonMode && !isMovingPolygonPoints ? 'primary' : 'default'}
              shape="circle"
              icon={<Brush size={24} />}
              onClick={() => {
                setIsErasing(false);
                setIsPolygonMode(false);
                setIsMovingPolygonPoints(false);
              }}
            />
          </Tooltip>
          <Tooltip title="Eraser">
            <Button
              type={isErasing ? 'primary' : 'default'}
              shape="circle"
              icon={<Eraser size={24} />}
              onClick={() => {
                setIsErasing(true);
                setIsPolygonMode(false);
                setIsMovingPolygonPoints(false);
              }}
            />
          </Tooltip>
          <Tooltip title="Polygon">
            <Button
              type={isPolygonMode && !isMovingPolygonPoints ? 'primary' : 'default'}
              shape="circle"
              icon={<Triangle size={24} />}
              onClick={() => {
                setIsPolygonMode(true);
                setIsErasing(false);
                setIsMovingPolygonPoints(false);
              }}
            />
          </Tooltip>
          <Tooltip title="Move Points">
            <Button
              type={isMovingPolygonPoints ? 'primary' : 'default'}
              shape="circle"
              icon={<Move size={24} />}
              onClick={() => {
                setIsMovingPolygonPoints(true);
                setIsPolygonMode(false);
                setIsErasing(false);
              }}
            />
          </Tooltip>
        </div>

        {/* 캔버스 배치 */}
        <div className="mx-auto" style={{ width: `${width}px`, height: `${height}px` }}>
          <canvas
            ref={canvasRef}
            width={width}
            height={height}
            className="border border-gray-300 rounded-lg absolute top-0 left-0 z-0"
          />
          <canvas
            ref={maskCanvasRef}
            width={width}
            height={height}
            onMouseDown={isMovingPolygonPoints ? selectPolygonPoint : startDrawing}
            onMouseUp={() => {
              if (isMovingPolygonPoints) {
                setSelectedPointIndex(null);
              }
              stopDrawing();
            }}
            onMouseMove={isMovingPolygonPoints ? movePolygonPoint : draw}
            onMouseLeave={() => {
              if (isMovingPolygonPoints) {
                setSelectedPointIndex(null);
              }
              stopDrawing();
            }}
            className="border border-gray-300 rounded-lg absolute top-0 left-0 z-10"
          />
        </div>

        {/* 슬라이더를 하단 중앙에 배치 */}
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex items-center gap-4 z-20">
          <Slider
            min={1}
            max={50}
            value={baseBrushSize}
            onChange={(value) => setBaseBrushSize(value)}
            style={{ width: 200 }}
          />
          <div>{baseBrushSize}px</div>
        </div>
      </div>
    </Modal>
  );
};

export default InpaintingModal;
