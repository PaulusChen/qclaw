// 模型训练页面
import React, { useState, useEffect, useRef } from 'react';
import {
  Form,
  Input,
  InputNumber,
  Select,
  Checkbox,
  Button,
  Card,
  Row,
  Col,
  Space,
  Divider,
  Typography,
  Progress,
  Statistic,
  Alert,
  Spin,
  Collapse,
  message as antMessage,
} from 'antd';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  ReloadOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import type { TrainingConfig, ModelType, OptimizerType, LRSchedulerType } from '../../../types/dl';
import { trainingApi } from '../../../services/dl/trainingApi';
import TrainingChart from './components/TrainingChart';
import TrainingLogs from './components/TrainingLogs';

const { Title, Text } = Typography;
const { Panel } = Collapse;

// 模型预设配置
const MODEL_PRESETS: Record<ModelType, { name: string; description: string; params: any }> = {
  lstm: {
    name: 'LSTM',
    description: '长短期记忆网络，适合序列建模',
    params: {
      hidden_size: 128,
      num_layers: 2,
      dropout: 0.2,
      bidirectional: true,
    },
  },
  transformer: {
    name: 'Transformer',
    description: '基于自注意力机制，并行计算能力强',
    params: {
      d_model: 256,
      num_heads: 8,
      num_layers: 4,
      dropout: 0.1,
    },
  },
};

// 默认训练配置
const DEFAULT_CONFIG: TrainingConfig = {
  model_type: 'transformer',
  d_model: 256,
  num_heads: 8,
  num_layers: 4,
  dropout: 0.1,
  batch_size: 64,
  learning_rate: 0.001,
  epochs: 100,
  optimizer: 'adamw',
  lr_scheduler: 'cosine',
  mixed_precision: true,
  gradient_clip: 1.0,
  early_stopping_patience: 10,
  use_pretrained: false,
  data_source: 'A 股全市场',
  start_date: '2020-01-01',
  end_date: '2024-12-31',
  train_ratio: 0.7,
  val_ratio: 0.15,
  test_ratio: 0.15,
};

interface TrainingPageProps {
  // 可以通过 props 传入初始配置
  initialConfig?: Partial<TrainingConfig>;
}

const TrainingPage: React.FC<TrainingPageProps> = ({ initialConfig }) => {
  const [form] = Form.useForm();
  const [trainingStatus, setTrainingStatus] = useState<'idle' | 'running' | 'paused' | 'completed' | 'error'>('idle');
  const [currentEpoch, setCurrentEpoch] = useState(0);
  const [totalEpochs, setTotalEpochs] = useState(100);
  const [metrics, setMetrics] = useState({
    train_loss: 0,
    val_loss: 0,
    learning_rate: 0.001,
  });
  const [logs, setLogs] = useState<Array<{ timestamp: string; message: string }>>([]);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [trainLossHistory, setTrainLossHistory] = useState<number[]>([]);
  const [valLossHistory, setValLossHistory] = useState<number[]>([]);
  const [learningRateHistory, setLearningRateHistory] = useState<number[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // 初始化表单
  useEffect(() => {
    form.setFieldsValue({
      ...DEFAULT_CONFIG,
      ...initialConfig,
    });
  }, [initialConfig, form]);

  // 清理 WebSocket 和轮询
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  // 轮询训练状态
  useEffect(() => {
    if (trainingStatus === 'running' && taskId) {
      pollIntervalRef.current = setInterval(async () => {
        try {
          const status = await trainingApi.getTrainingStatus(taskId);
          setCurrentEpoch(status.progress.current_epoch);
          setTotalEpochs(status.progress.total_epochs);
          
          const newTrainLoss = status.metrics.train_loss || 0;
          const newValLoss = status.metrics.val_loss || 0;
          const newLearningRate = status.metrics.learning_rate || 0.001;
          
          setMetrics({
            train_loss: newTrainLoss,
            val_loss: newValLoss,
            learning_rate: newLearningRate,
          });
          
          // 更新历史数据用于图表
          setTrainLossHistory(prev => [...prev, newTrainLoss]);
          setValLossHistory(prev => [...prev, newValLoss]);
          setLearningRateHistory(prev => [...prev, newLearningRate]);
          
          // 检查训练状态变化
          if (status.status === 'stopped' || status.status === 'completed' || status.status === 'error') {
            setTrainingStatus(status.status);
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current);
            }
            antMessage.info(`训练已${status.status === 'stopped' ? '停止' : status.status === 'completed' ? '完成' : '失败'}`);
          }
        } catch (error) {
          console.error('Failed to poll training status:', error);
        }
      }, 2000); // 每 2 秒轮询一次
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [trainingStatus, taskId]);

  // 开始训练
  const handleStartTraining = async (values: any) => {
    try {
      const config: TrainingConfig = {
        ...values,
        model_type: values.model_type as ModelType,
        optimizer: values.optimizer as OptimizerType,
        lr_scheduler: values.lr_scheduler as LRSchedulerType,
      };

      const response = await trainingApi.startTraining(config);
      setTaskId(response.task_id);
      setTrainingStatus('running');
      setCurrentEpoch(0);
      setTotalEpochs(values.epochs);
      
      antMessage.success('训练任务已启动');
      
      // 添加初始日志
      setLogs([
        {
          timestamp: new Date().toLocaleTimeString(),
          message: `训练任务 ${response.task_id} 已启动`,
        },
      ]);

      // 创建 WebSocket 连接
      wsRef.current = trainingApi.createTrainingWebSocket(response.task_id);
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'log') {
          setLogs((prev) => [...prev, { timestamp: new Date().toLocaleTimeString(), message: data.message }]);
        }
      };
    } catch (error: any) {
      console.error('Failed to start training:', error);
      antMessage.error(error.response?.data?.message || '启动训练失败');
      setTrainingStatus('error');
    }
  };

  // 停止训练
  const handleStopTraining = async () => {
    if (!taskId) return;
    
    try {
      await trainingApi.stopTraining(taskId);
      antMessage.success('停止请求已发送，等待服务器确认...');
      
      setLogs((prev) => [
        ...prev,
        {
          timestamp: new Date().toLocaleTimeString(),
          message: '用户请求停止训练',
        },
      ]);
      
      // 继续轮询直到服务器确认停止
    } catch (error: any) {
      console.error('Failed to stop training:', error);
      antMessage.error('停止训练失败');
    }
  };

  // 重置表单
  const handleReset = () => {
    form.resetFields();
    setTrainingStatus('idle');
    setTaskId(null);
    setLogs([]);
    setCurrentEpoch(0);
  };

  // 根据模型类型显示不同的参数
  const modelType = Form.useWatch('model_type', form);

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <Title level={2} className="text-xl sm:text-2xl lg:text-3xl mb-4 sm:mb-6">模型训练</Title>
      
      <Row gutter={[16, 16]}>
        {/* 左侧配置面板 */}
        <Col xs={24} sm={24} md={24} lg={8} xl={7}>
          <Card 
            title="训练配置" 
            className="mb-4"
            size="small"
            bodyStyle={{ padding: '12px sm:16px' }}
          >
            <Form
              form={form}
              layout="vertical"
              onFinish={handleStartTraining}
              disabled={trainingStatus === 'running'}
            >
              {/* 模型选择 */}
              <Form.Item
                label="模型架构"
                name="model_type"
                initialValue="transformer"
              >
                <Select>
                  <Select.Option value="lstm">
                    <div>
                      <strong>LSTM</strong>
                      <div style={{ fontSize: '12px', color: '#999' }}>
                        长短期记忆网络，适合序列建模
                      </div>
                    </div>
                  </Select.Option>
                  <Select.Option value="transformer">
                    <div>
                      <strong>Transformer</strong>
                      <div style={{ fontSize: '12px', color: '#999' }}>
                        基于自注意力机制，并行计算能力强
                      </div>
                    </div>
                  </Select.Option>
                </Select>
              </Form.Item>

              {/* 模型参数 - 根据类型动态显示 */}
              {modelType === 'transformer' ? (
                <>
                  <Form.Item label="d_model" name="d_model" initialValue={256}>
                    <InputNumber min={64} max={1024} step={64} style={{ width: '100%' }} />
                  </Form.Item>
                  <Form.Item label="num_heads" name="num_heads" initialValue={8}>
                    <InputNumber min={2} max={16} step={2} style={{ width: '100%' }} />
                  </Form.Item>
                </>
              ) : (
                <>
                  <Form.Item label="hidden_size" name="hidden_size" initialValue={128}>
                    <InputNumber min={32} max={512} step={32} style={{ width: '100%' }} />
                  </Form.Item>
                  <Form.Item label="bidirectional" name="bidirectional" valuePropName="checked" initialValue={true}>
                    <Checkbox>双向 LSTM</Checkbox>
                  </Form.Item>
                </>
              )}
              
              <Form.Item label="num_layers" name="num_layers" initialValue={4}>
                <InputNumber min={1} max={12} style={{ width: '100%' }} />
              </Form.Item>
              
              <Form.Item label="dropout" name="dropout" initialValue={0.1}>
                <InputNumber min={0} max={0.5} step={0.05} style={{ width: '100%' }} />
              </Form.Item>

              <Divider orientation="left" style={{ fontSize: '12px' }}>训练参数</Divider>

              <Form.Item label="batch_size" name="batch_size" initialValue={64}>
                <InputNumber min={8} max={256} step={8} style={{ width: '100%' }} />
              </Form.Item>
              
              <Form.Item label="learning_rate" name="learning_rate" initialValue={0.001}>
                <InputNumber min={0.00001} max={0.01} step={0.0001} style={{ width: '100%' }} />
              </Form.Item>
              
              <Form.Item label="epochs" name="epochs" initialValue={100}>
                <InputNumber min={10} max={500} step={10} style={{ width: '100%' }} />
              </Form.Item>
              
              <Form.Item label="optimizer" name="optimizer" initialValue="adamw">
                <Select>
                  <Select.Option value="adam">Adam</Select.Option>
                  <Select.Option value="adamw">AdamW</Select.Option>
                  <Select.Option value="sgd">SGD</Select.Option>
                </Select>
              </Form.Item>
              
              <Form.Item label="lr_scheduler" name="lr_scheduler" initialValue="cosine">
                <Select>
                  <Select.Option value="cosine">余弦退火</Select.Option>
                  <Select.Option value="plateau">ReduceLROnPlateau</Select.Option>
                  <Select.Option value="step">StepLR</Select.Option>
                  <Select.Option value="one_cycle">OneCycle</Select.Option>
                </Select>
              </Form.Item>

              <Divider orientation="left" style={{ fontSize: '12px' }}>数据配置</Divider>

              <Form.Item label="数据源" name="data_source" initialValue="A 股全市场">
                <Select>
                  <Select.Option value="A 股全市场">A 股全市场</Select.Option>
                  <Select.Option value="沪深 300">沪深 300</Select.Option>
                  <Select.Option value="中证 500">中证 500</Select.Option>
                  <Select.Option value="自定义">自定义</Select.Option>
                </Select>
              </Form.Item>
              
              <Row gutter={8}>
                <Col span={12}>
                  <Form.Item label="开始日期" name="start_date" initialValue="2020-01-01">
                    <Input placeholder="YYYY-MM-DD" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="结束日期" name="end_date" initialValue="2024-12-31">
                    <Input placeholder="YYYY-MM-DD" />
                  </Form.Item>
                </Col>
              </Row>

              <Collapse ghost size="small">
                <Panel header="高级选项" key="advanced">
                  <Form.Item label="混合精度训练" name="mixed_precision" valuePropName="checked" initialValue={true}>
                    <Checkbox>启用 (加速训练)</Checkbox>
                  </Form.Item>
                  
                  <Form.Item label="梯度裁剪" name="gradient_clip" initialValue={1.0}>
                    <InputNumber min={0.1} max={10} step={0.1} style={{ width: '100%' }} />
                  </Form.Item>
                  
                  <Form.Item label="早停 patience" name="early_stopping_patience" initialValue={10}>
                    <InputNumber min={5} max={50} step={5} style={{ width: '100%' }} />
                  </Form.Item>
                  
                  <Form.Item label="使用预训练模型" name="use_pretrained" valuePropName="checked" initialValue={false}>
                    <Checkbox>从检查点继续训练</Checkbox>
                  </Form.Item>
                </Panel>
              </Collapse>

              <Divider className="my-3 sm:my-4" />

              <Space 
                direction={{ xs: 'vertical', sm: 'horizontal' }}
                style={{ width: '100%' }} 
                className="w-full"
              >
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  icon={<PlayCircleOutlined />}
                  disabled={trainingStatus === 'running'}
                  size={{ xs: 'middle', sm: 'large' }}
                  className="w-full sm:w-auto"
                  block={{ xs: true, sm: false }}
                >
                  开始训练
                </Button>
                <Button 
                  icon={<ReloadOutlined />} 
                  onClick={handleReset}
                  disabled={trainingStatus === 'running'}
                  size={{ xs: 'middle', sm: 'default' }}
                  className="w-full sm:w-auto"
                  block={{ xs: true, sm: false }}
                >
                  重置
                </Button>
              </Space>
            </Form>
          </Card>
        </Col>

        {/* 右侧监控面板 */}
        <Col xs={24} sm={24} md={24} lg={16} xl={17}>
          <Space direction="vertical" style={{ width: '100%' }} size="middle" className="w-full">
            {/* 训练状态卡片 */}
            <Card size="small" bodyStyle={{ padding: '12px sm:16px' }}>
              <Row gutter={[12, 12]}>
                <Col xs={12} sm={8}>
                  <Statistic
                    title="状态"
                    value={trainingStatus === 'idle' ? '未开始' : 
                            trainingStatus === 'running' ? '训练中' :
                            trainingStatus === 'paused' ? '已暂停' :
                            trainingStatus === 'completed' ? '已完成' : '错误'}
                    valueStyle={{ 
                      color: trainingStatus === 'running' ? '#52c41a' : 
                             trainingStatus === 'completed' ? '#1890ff' :
                             trainingStatus === 'error' ? '#f5222d' : '#999'
                    }}
                    prefix={
                      trainingStatus === 'running' ? '🟢' :
                      trainingStatus === 'completed' ? '✅' :
                      trainingStatus === 'error' ? '❌' : '⚪'
                    }
                  />
                </Col>
                <Col xs={12} sm={8}>
                  <Statistic
                    title="Epoch"
                    value={currentEpoch}
                    suffix={`/ ${totalEpochs}`}
                    valueStyle={{ fontSize: 'clamp(16px, 4vw, 20px)' }}
                  />
                </Col>
                <Col xs={24} sm={8}>
                  <Statistic
                    title="当前损失"
                    value={metrics.train_loss}
                    precision={4}
                    valueStyle={{ color: '#722ed1', fontSize: 'clamp(16px, 4vw, 20px)' }}
                  />
                </Col>
              </Row>
              
              {trainingStatus === 'running' && (
                <Progress
                  percent={Math.round((currentEpoch / totalEpochs) * 100)}
                  className="mt-4 sm:mt-6"
                  strokeColor={{
                    '0%': '#722ed1',
                    '100%': '#b37feb',
                  }}
                />
              )}
              
              {trainingStatus === 'running' && (
                <div className="mt-4 sm:mt-6 text-right">
                  <Button 
                    danger 
                    icon={<StopOutlined />} 
                    onClick={handleStopTraining}
                    size={{ xs: 'middle', sm: 'default' }}
                    className="w-full sm:w-auto"
                    block={{ xs: true, sm: false }}
                  >
                    停止训练
                  </Button>
                </div>
              )}
            </Card>

            {/* 训练曲线图表 */}
            <Card title="训练监控" size="small">
              <TrainingChart
                trainLoss={metrics.train_loss}
                valLoss={metrics.val_loss}
                learningRate={metrics.learning_rate}
                status={trainingStatus}
                trainLossHistory={trainLossHistory}
                valLossHistory={valLossHistory}
                learningRateHistory={learningRateHistory}
              />
            </Card>

            {/* 训练日志 */}
            <Card title="训练日志" size="small">
              <TrainingLogs logs={logs} />
            </Card>
          </Space>
        </Col>
      </Row>
    </div>
  );
};

export default TrainingPage;
