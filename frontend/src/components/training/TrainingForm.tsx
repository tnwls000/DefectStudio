import { Collapse } from 'antd';

const TrainingForm = () => {
  const collapseItems = [
    {
      key: '1',
      label: '1. Create Embedding',
      children: <div></div>
    },
    {
      key: '2',
      label: '2. Create Hypernetwork',
      children: <div></div>
    },
    {
      key: '3',
      label: '3. Train',
      children: <div></div>
    }
  ];

  return (
    <div className="training-form-container h-full overflow-y-auto">
      <Collapse defaultActiveKey={['1']} items={collapseItems} />
    </div>
  );
};

export default TrainingForm;
