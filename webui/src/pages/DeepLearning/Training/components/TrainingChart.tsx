// 训练曲线图表组件
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Typography, Tabs } from 'antd';

const { Text } = Typography;

interface TrainingChartProps {
  trainLoss: number;
  valLoss: number;
  learningRate: number;
  status: 'idle' | 'running' | 'paused' | 'completed' | 'error';
  // 历史数据 (实际使用时会从父组件传入)
  trainLossHistory?: number[];
  valLossHistory?: number[];
  learningRateHistory?: number[];
}

const TrainingChart: React.FC<TrainingChartProps> = ({
  trainLoss,
  valLoss,
  learningRate,
  status,
  trainLossHistory = [],
  valLossHistory = [],
  learningRateHistory = [],
}) => {
  // 使用真实数据生成图表
  const generateChartData = () => {
    // 优先使用真实历史数据
    if (trainLossHistory.length > 0) {
      return trainLossHistory.map((loss, i) => ({
        epoch: i + 1,
        train_loss: loss,
        val_loss: valLossHistory[i] || loss,
        learning_rate: learningRateHistory[i] || 0.001,
      }));
    }
    
    // 如果没有历史数据但有当前值，显示当前值
    if (trainLoss > 0) {
      return [{
        epoch: 1,
        train_loss: trainLoss,
        val_loss: valLoss,
        learning_rate: learningRate,
      }];
    }
    
    return [];
  };

  const chartData = generateChartData();

  const lossChart = (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis 
          dataKey="epoch" 
          label={{ value: 'Epoch', position: 'insideBottom', offset: -5 }}
          stroke="#999"
        />
        <YAxis 
          label={{ value: 'Loss', angle: -90, position: 'insideLeft' }}
          stroke="#999"
          domain={['auto', 'auto']}
        />
        <Tooltip 
          formatter={(value: number) => [value.toFixed(4), 'Loss']}
          labelFormatter={(label) => `Epoch ${label}`}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="train_loss"
          name="训练损失"
          stroke="#722ed1"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6 }}
        />
        <Line
          type="monotone"
          dataKey="val_loss"
          name="验证损失"
          stroke="#faad14"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );

  const lrChart = (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis 
          dataKey="epoch" 
          label={{ value: 'Epoch', position: 'insideBottom', offset: -5 }}
          stroke="#999"
        />
        <YAxis 
          label={{ value: 'LR', angle: -90, position: 'insideLeft' }}
          stroke="#999"
          domain={['auto', 'auto']}
          tickFormatter={(value) => value.toExponential(2)}
        />
        <Tooltip 
          formatter={(value: number) => [value.toExponential(4), 'Learning Rate']}
          labelFormatter={(label) => `Epoch ${label}`}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="learning_rate"
          name="学习率"
          stroke="#1890ff"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );

  const items = [
    {
      key: 'loss',
      label: '损失曲线',
      children: lossChart,
    },
    {
      key: 'lr',
      label: '学习率变化',
      children: lrChart,
    },
  ];

  return (
    <div>
      {status === 'idle' ? (
        <div style={{ 
          textAlign: 'center', 
          padding: '60px 0',
          color: '#999'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
          <Text>暂无训练数据，请先启动训练</Text>
        </div>
      ) : (
        <Tabs 
          defaultActiveKey="loss" 
          items={items}
          size="small"
        />
      )}
      
      {/* 实时指标展示 */}
      {status === 'running' && (
        <div style={{ 
          marginTop: 16, 
          padding: 12, 
          background: '#f5f5f5', 
          borderRadius: 4,
          display: 'flex',
          justifyContent: 'space-around',
        }}>
          <div>
            <Text type="secondary">当前训练损失</Text>
            <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#722ed1' }}>
              {trainLoss.toFixed(4)}
            </div>
          </div>
          <div>
            <Text type="secondary">当前验证损失</Text>
            <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#faad14' }}>
              {valLoss.toFixed(4)}
            </div>
          </div>
          <div>
            <Text type="secondary">当前学习率</Text>
            <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#1890ff' }}>
              {learningRate.toExponential(2)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TrainingChart;
