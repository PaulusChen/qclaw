// 模型推理页面
import React, { useState, useEffect } from 'react';
import {
  Form,
  Input,
  Select,
  DatePicker,
  Button,
  Card,
  Row,
  Col,
  Space,
  Divider,
  Typography,
  Alert,
  Spin,
  Table,
  Tag,
  Statistic,
  Progress,
  message as antMessage,
  Collapse,
  InputNumber,
  Checkbox,
} from 'antd';
import {
  SearchOutlined,
  PlayCircleOutlined,
  ThunderboltOutlined,
  HistoryOutlined,
  DownloadOutlined,
  RiseOutlined,
  FallOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import type {
  PredictionRequest,
  PredictionResult,
  ModelInfo,
  PredictionHorizon,
  FeatureImportance,
  AccuracyTrend,
} from '../../../types/dl';
import { inferenceApi } from '../../../services/dl/inferenceApi';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

// 预测周期选项
const HORIZON_OPTIONS: { value: PredictionHorizon; label: string }[] = [
  { value: 1, label: 'T+1 (明日)' },
  { value: 3, label: 'T+3 (3 日后)' },
  { value: 5, label: 'T+5 (周线)' },
  { value: 7, label: 'T+7' },
  { value: 14, label: 'T+14 (双周)' },
  { value: 30, label: 'T+30 (月线)' },
];

// 默认预测请求
const DEFAULT_REQUEST: PredictionRequest = {
  stock_code: '',
  date: new Date().toISOString().split('T')[0],
  model_version: '',
  horizons: [1, 3, 5],
};

const InferencePage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [predictionResult, setPredictionResult] = useState<PredictionResult | null>(null);
  const [batchTaskId, setBatchTaskId] = useState<string | null>(null);
  const [batchStatus, setBatchStatus] = useState<'idle' | 'running' | 'completed' | 'error'>('idle');
  const [batchProgress, setBatchProgress] = useState({ total: 0, completed: 0 });
  const [accuracyTrend, setAccuracyTrend] = useState<AccuracyTrend[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // 加载模型列表
  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const response = await inferenceApi.getModels();
      const modelsArray = Array.isArray(response.models) ? response.models : [];
      setModels(modelsArray);
      // 默认选择激活的模型
      const activeModel = modelsArray.find(m => m.is_active);
      if (activeModel) {
        form.setFieldValue('model_version', activeModel.version);
      }
    } catch (error: any) {
      console.error('Failed to load models:', error);
      antMessage.error('加载模型列表失败');
    }
  };

  // 单次预测
  const handleSinglePredict = async (values: any) => {
    if (!values.stock_code) {
      antMessage.warning('请输入股票代码');
      return;
    }

    setLoading(true);
    try {
      const request: PredictionRequest = {
        stock_code: values.stock_code,
        date: values.date,
        model_version: values.model_version,
        horizons: values.horizons || [1],
      };

      const result = await inferenceApi.predictSingle(request);
      setPredictionResult(result);
      antMessage.success('预测完成');

      // 加载准确率趋势
      if (result.model_version) {
        loadAccuracyTrend(result.model_version);
      }
    } catch (error: any) {
      console.error('Prediction failed:', error);
      antMessage.error(error.response?.data?.message || '预测失败');
    } finally {
      setLoading(false);
    }
  };

  // 批量预测
  const handleBatchPredict = async (values: any) => {
    if (!values.batch_stock_codes) {
      antMessage.warning('请输入股票代码列表');
      return;
    }

    setLoading(true);
    try {
      const stockCodes = values.batch_stock_codes
        .split(/[\n,，\s]+/)
        .filter((code: string) => code.trim())
        .map((code: string) => code.trim().toUpperCase());

      const response = await inferenceApi.predictBatch({
        stock_codes: stockCodes,
        date: values.date,
        model_version: values.model_version,
        horizons: values.horizons || [1],
      });

      setBatchTaskId(response.task_id);
      setBatchStatus('running');
      antMessage.success('批量预测任务已启动');

      // 轮询任务状态
      pollBatchStatus(response.task_id);
    } catch (error: any) {
      console.error('Batch prediction failed:', error);
      antMessage.error(error.response?.data?.message || '批量预测失败');
      setLoading(false);
    }
  };

  // 轮询批量预测状态
  const pollBatchStatus = async (taskId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const status = await inferenceApi.getBatchPredictionStatus(taskId);
        setBatchProgress({ total: status.total, completed: status.completed });

        if (status.status === 'completed') {
          setBatchStatus('completed');
          clearInterval(pollInterval);
          antMessage.success(`批量预测完成，共 ${status.completed} 只股票`);
        } else if (status.status === 'error') {
          setBatchStatus('error');
          clearInterval(pollInterval);
          antMessage.error('批量预测失败');
        }
      } catch (error) {
        console.error('Failed to poll batch status:', error);
      }
    }, 3000);

    // 5 分钟后停止轮询
    setTimeout(() => clearInterval(pollInterval), 300000);
  };

  // 加载准确率趋势
  const loadAccuracyTrend = async (modelVersion: string) => {
    try {
      const trend = await inferenceApi.getAccuracyTrend(modelVersion, 30);
      setAccuracyTrend(trend);
    } catch (error) {
      console.error('Failed to load accuracy trend:', error);
    }
  };

  // 导出预测结果
  const handleExport = async () => {
    if (!batchTaskId) {
      antMessage.warning('暂无可导出的预测结果');
      return;
    }

    try {
      const response = await inferenceApi.exportPredictions([batchTaskId]);
      window.open(response.download_url, '_blank');
      antMessage.success('导出成功');
    } catch (error: any) {
      antMessage.error('导出失败');
    }
  };

  // 渲染预测方向
  const renderDirection = (direction: string, prob: number) => {
    const isUp = direction === 'up';
    return (
      <div className="flex items-center gap-2">
        {isUp ? (
          <RiseOutlined className="text-red-500 text-xl" />
        ) : (
          <FallOutlined className="text-green-500 text-xl" />
        )}
        <span className={isUp ? 'text-red-500 font-medium' : 'text-green-500 font-medium'}>
          {isUp ? '涨' : '跌'}
        </span>
        <span className="text-gray-500 text-sm">({(prob * 100).toFixed(0)}%)</span>
      </div>
    );
  };

  // 渲染买卖信号
  const renderSignal = (signal: string, confidence: number) => {
    const config: Record<string, { color: string; icon: any; text: string }> = {
      buy: { color: 'red', icon: RiseOutlined, text: '买入' },
      sell: { color: 'green', icon: FallOutlined, text: '卖出' },
      hold: { color: 'gray', icon: InfoCircleOutlined, text: '持有' },
    };

    const cfg = config[signal] || config.hold;
    const Icon = cfg.icon;

    return (
      <div className="flex items-center gap-2">
        <Tag color={cfg.color} icon={<Icon />}>
          {cfg.text}
        </Tag>
        <span className="text-gray-500 text-sm">置信度 {(confidence * 100).toFixed(0)}%</span>
      </div>
    );
  };

  // 渲染特征重要性
  const renderFeatureImportance = (features: FeatureImportance[]) => {
    const maxImportance = Math.max(...features.map(f => f.importance));

    return (
      <div className="space-y-2">
        {features.slice(0, 10).map((feature, index) => (
          <div key={index} className="flex items-center gap-2">
            <Text className="w-32 text-sm" ellipsis>{feature.name}</Text>
            <div className="flex-1 h-4 bg-gray-100 rounded overflow-hidden">
              <div
                className={`h-full ${feature.contribution === 'positive' ? 'bg-red-400' : 'bg-green-400'}`}
                style={{ width: `${(feature.importance / maxImportance) * 100}%` }}
              />
            </div>
            <Text className="w-12 text-xs text-right">{feature.importance.toFixed(2)}</Text>
          </div>
        ))}
      </div>
    );
  };

  // 准确率趋势图表数据
  const chartData = accuracyTrend.map(item => ({
    date: item.date.slice(5), // 只显示 MM-DD
    accuracy: item.accuracy * 100,
    cumulative: item.cumulative_accuracy * 100,
  }));

  // 多周期预测表格列
  const horizonColumns = [
    {
      title: '周期',
      dataIndex: 'horizon',
      key: 'horizon',
      render: (h: PredictionHorizon) => `T+${h}`,
      width: 80,
    },
    {
      title: '方向',
      dataIndex: 'direction',
      key: 'direction',
      render: (direction: string, record: any) =>
        renderDirection(direction, record.direction_prob),
      width: 120,
    },
    {
      title: '收益率',
      dataIndex: 'return_pred',
      key: 'return_pred',
      render: (val: number) => (
        <span className={val > 0 ? 'text-red-500' : val < 0 ? 'text-green-500' : ''}>
          {val > 0 ? '+' : ''}{(val * 100).toFixed(2)}%
        </span>
      ),
      width: 100,
    },
    {
      title: '信号',
      dataIndex: 'signal',
      key: 'signal',
      render: (signal: string, record: any) => renderSignal(signal, record.confidence),
      width: 150,
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (val: number) => (
        <Progress
          percent={Math.round(val * 100)}
          size="small"
          strokeColor={val > 0.6 ? '#52c41a' : val > 0.4 ? '#faad14' : '#f5222d'}
          format={() => `${(val * 100).toFixed(0)}%`}
        />
      ),
      width: 120,
    },
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <Title level={2} className="text-xl sm:text-2xl lg:text-3xl mb-2 sm:mb-4">模型推理</Title>
      <Paragraph type="secondary" className="text-sm sm:text-base mb-4 sm:mb-6">
        使用训练好的深度学习模型对股票进行预测，支持单次预测和批量预测
      </Paragraph>

      <Space direction="vertical" style={{ width: '100%' }} size="large" className="w-full">
        {/* 预测配置卡片 */}
        <Card title="预测配置" size="small" bodyStyle={{ padding: '12px sm:16px' }}>
          <Form
            form={form}
            layout={{ xs: 'vertical', sm: 'inline' }}
            onFinish={handleSinglePredict}
            disabled={loading && batchStatus === 'running'}
          >
            <Form.Item
              label="模型版本"
              name="model_version"
              rules={[{ required: true, message: '请选择模型' }]}
              className="w-full sm:w-auto"
            >
              <Select style={{ width: '100%', minWidth: 180 }} placeholder="选择模型">
                {models.map(model => (
                  <Select.Option key={model.version} value={model.version}>
                    {model.version} {model.is_active && <Tag color="green">激活</Tag>}
                    <span className="text-gray-400 text-xs ml-2">
                      准确率：{(model.metrics.val_accuracy * 100).toFixed(1)}%
                    </span>
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              label="股票代码"
              name="stock_code"
              rules={[{ required: true, message: '请输入股票代码' }]}
              className="w-full sm:w-auto"
            >
              <Input
                placeholder="000001.SZ"
                style={{ width: '100%', minWidth: 150 }}
                prefix={<SearchOutlined />}
              />
            </Form.Item>

            <Form.Item
              label="预测日期"
              name="date"
              rules={[{ required: true, message: '请选择日期' }]}
              className="w-full sm:w-auto"
            >
              <DatePicker style={{ width: '100%', minWidth: 140 }} />
            </Form.Item>

            <Form.Item
              label="预测周期"
              name="horizons"
              initialValue={[1, 3, 5]}
              className="w-full sm:w-auto"
            >
              <Select
                mode="multiple"
                style={{ width: '100%', minWidth: 180 }}
                placeholder="选择周期"
                maxTagCount="responsive"
              >
                {HORIZON_OPTIONS.map(opt => (
                  <Select.Option key={opt.value} value={opt.value}>
                    {opt.label}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item className="w-full sm:w-auto mt-2 sm:mt-0">
              <Space 
                direction={{ xs: 'vertical', sm: 'horizontal' }}
                className="w-full sm:w-auto"
              >
                <Button
                  type="primary"
                  htmlType="submit"
                  icon={<PlayCircleOutlined />}
                  loading={loading}
                  size={{ xs: 'middle', sm: 'default' }}
                  className="w-full sm:w-auto"
                  block={{ xs: true, sm: false }}
                >
                  开始预测
                </Button>
                <Button
                  type="default"
                  icon={<ThunderboltOutlined />}
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  size={{ xs: 'middle', sm: 'default' }}
                  className="w-full sm:w-auto"
                  block={{ xs: true, sm: false }}
                >
                  批量预测
                </Button>
              </Space>
            </Form.Item>
          </Form>

          {/* 批量预测面板 */}
          {showAdvanced && (
            <Collapse activeKeys={['batch']} style={{ marginTop: 16 }}>
              <Panel header="批量预测配置" key="batch">
                <Form
                  layout="vertical"
                  onFinish={handleBatchPredict}
                  disabled={loading && batchStatus === 'running'}
                >
                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        label="股票代码列表 (每行一个或逗号分隔)"
                        name="batch_stock_codes"
                        rules={[{ required: true, message: '请输入股票代码' }]}
                      >
                        <Input.TextArea
                          rows={4}
                          placeholder="000001.SZ&#10;000002.SZ&#10;600519.SH"
                        />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item label="预测日期" name="date" initialValue={DEFAULT_REQUEST.date}>
                        <DatePicker style={{ width: '100%' }} />
                      </Form.Item>

                      <Form.Item
                        label="预测周期"
                        name="horizons"
                        initialValue={[1, 3, 5]}
                      >
                        <Select
                          mode="multiple"
                          style={{ width: '100%' }}
                          placeholder="选择周期"
                        >
                          {HORIZON_OPTIONS.map(opt => (
                            <Select.Option key={opt.value} value={opt.value}>
                              {opt.label}
                            </Select.Option>
                          ))}
                        </Select>
                      </Form.Item>

                      <Form.Item>
                        <Button
                          type="primary"
                          htmlType="submit"
                          icon={<ThunderboltOutlined />}
                          loading={loading}
                        >
                          启动批量预测
                        </Button>
                      </Form.Item>
                    </Col>
                  </Row>
                </Form>

                {batchStatus !== 'idle' && (
                  <Alert
                    message={
                      batchStatus === 'running' ? '批量预测进行中' :
                      batchStatus === 'completed' ? '批量预测完成' : '批量预测失败'
                    }
                    description={
                      <div className="mt-2">
                        <Progress
                          percent={Math.round((batchProgress.completed / batchProgress.total) * 100)}
                          status={batchStatus === 'error' ? 'exception' : 'active'}
                        />
                        <Text className="mt-2 block">
                          已完成：{batchProgress.completed} / {batchProgress.total} 只股票
                        </Text>
                      </div>
                    }
                    type={batchStatus === 'error' ? 'error' : batchStatus === 'completed' ? 'success' : 'info'}
                    showIcon
                    action={
                      batchStatus === 'completed' && (
                        <Button size="small" icon={<DownloadOutlined />} onClick={handleExport}>
                          导出结果
                        </Button>
                      )
                    }
                  />
                )}
              </Panel>
            </Collapse>
          )}
        </Card>

        {/* 预测结果 */}
        {predictionResult && (
          <>
            {/* 预测结果摘要 */}
            <Card title="预测结果摘要" size="small">
              <Row gutter={16}>
                <Col span={6}>
                  <Statistic
                    title="股票"
                    value={`${predictionResult.stock_code}`}
                    suffix={`(${predictionResult.stock_name})`}
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="预测日期"
                    value={predictionResult.predict_date}
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="模型版本"
                    value={predictionResult.model_version}
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="推理耗时"
                    value={predictionResult.inference_time_ms}
                    suffix="ms"
                  />
                </Col>
              </Row>
            </Card>

            {/* 核心预测指标 */}
            <Row gutter={[16, 16]}>
              <Col xs={24} md={8}>
                <Card size="small" title="涨跌方向">
                  <div className="text-center py-4">
                    {renderDirection(
                      predictionResult.prediction.direction,
                      predictionResult.prediction.direction_prob
                    )}
                    <div className="mt-4">
                      <Progress
                        type="dashboard"
                        percent={Math.round(predictionResult.prediction.direction_prob * 100)}
                        strokeColor={
                          predictionResult.prediction.direction === 'up' ? '#f5222d' : '#52c41a'
                        }
                        format={(percent) => `${percent}%`}
                      />
                    </div>
                  </div>
                </Card>
              </Col>

              <Col xs={24} md={8}>
                <Card size="small" title="收益率预测">
                  <div className="text-center py-4">
                    <div
                      className={`text-4xl font-bold ${
                        predictionResult.prediction.return_pred > 0
                          ? 'text-red-500'
                          : predictionResult.prediction.return_pred < 0
                          ? 'text-green-500'
                          : ''
                      }`}
                    >
                      {predictionResult.prediction.return_pred > 0 ? '+' : ''}
                      {(predictionResult.prediction.return_pred * 100).toFixed(2)}%
                    </div>
                    <Text type="secondary" className="mt-2 block">
                      置信区间：[
                      {(predictionResult.prediction.return_ci[0] * 100).toFixed(2)}%,
                      {(predictionResult.prediction.return_ci[1] * 100).toFixed(2)}%
                      ]
                    </Text>
                  </div>
                </Card>
              </Col>

              <Col xs={24} md={8}>
                <Card size="small" title="买卖信号">
                  <div className="text-center py-4">
                    {renderSignal(
                      predictionResult.prediction.signal,
                      predictionResult.prediction.confidence
                    )}
                    <div className="mt-4">
                      {predictionResult.prediction.signal === 'buy' && (
                        <CheckCircleOutlined className="text-red-500 text-5xl" />
                      )}
                      {predictionResult.prediction.signal === 'sell' && (
                        <CloseCircleOutlined className="text-green-500 text-5xl" />
                      )}
                      {predictionResult.prediction.signal === 'hold' && (
                        <InfoCircleOutlined className="text-gray-400 text-5xl" />
                      )}
                    </div>
                  </div>
                </Card>
              </Col>
            </Row>

            {/* 多周期预测结果 */}
            {predictionResult.multi_horizon && predictionResult.multi_horizon.length > 0 && (
              <Card title="多周期预测结果" size="small">
                <Table
                  columns={horizonColumns}
                  dataSource={predictionResult.multi_horizon}
                  rowKey="horizon"
                  pagination={false}
                  size="small"
                  scroll={{ x: 600 }}
                />
              </Card>
            )}

            {/* 特征重要性和准确率趋势 */}
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={12}>
                <Card title="预测依据 (特征重要性)" size="small">
                  {renderFeatureImportance(predictionResult.feature_importance)}
                  {predictionResult.key_insights && predictionResult.key_insights.length > 0 && (
                    <Alert
                      message="关键依据"
                      description={
                        <ul className="mt-2 space-y-1">
                          {predictionResult.key_insights.map((insight, i) => (
                            <li key={i}>{insight}</li>
                          ))}
                        </ul>
                      }
                      type="info"
                      showIcon
                      style={{ marginTop: 16 }}
                    />
                  )}
                </Card>
              </Col>

              <Col xs={24} lg={12}>
                <Card title="历史预测准确率 (该模型)" size="small">
                  {accuracyTrend.length > 0 ? (
                    <ResponsiveContainer width="100%" height={250}>
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis domain={[40, 70]} />
                        <Tooltip />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="accuracy"
                          stroke="#722ed1"
                          name="日准确率"
                          strokeWidth={2}
                        />
                        <Line
                          type="monotone"
                          dataKey="cumulative"
                          stroke="#1890ff"
                          name="累计准确率"
                          strokeWidth={2}
                          strokeDasharray="5 5"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="text-center py-8 text-gray-400">
                      <HistoryOutlined className="text-4xl mb-2" />
                      <div>暂无准确率数据</div>
                    </div>
                  )}
                  {accuracyTrend.length > 0 && (
                    <div className="mt-4 text-center">
                      <Text>
                        当前准确率：<strong className="text-purple-600">
                          {(accuracyTrend[accuracyTrend.length - 1]?.accuracy * 100).toFixed(1)}%
                        </strong>
                        {' '}
                        (过去 30 天)
                      </Text>
                    </div>
                  )}
                </Card>
              </Col>
            </Row>
          </>
        )}

        {/* 无结果时的提示 */}
        {!predictionResult && !loading && (
          <Card>
            <div className="text-center py-12">
              <SearchOutlined className="text-6xl text-gray-300 mb-4" />
              <Title level={4} type="secondary">
                请输入股票代码并开始预测
              </Title>
              <Text type="secondary">
                支持 A 股和美股市场，预测结果包括涨跌方向、收益率、买卖信号等
              </Text>
            </div>
          </Card>
        )}
      </Space>
    </div>
  );
};

export default InferencePage;
