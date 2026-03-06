// 模型管理页面 - WEBUI-DL-003
import React, { useEffect, useState } from 'react';
import {
  Typography,
  Card,
  Table,
  Tag,
  Button,
  Space,
  Modal,
  Descriptions,
  Progress,
  Alert,
  message,
  Popconfirm,
  Upload,
  Badge,
  Tabs,
  Select,
  Input,
  Checkbox,
} from 'antd';
import {
  InboxOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  DownloadOutlined,
  UploadOutlined,
  CompareOutlined,
  DeleteOutlined,
  FileTextOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  ArchiveOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { Bar, BarChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useDLStore } from '../../../store/dlStore';
import type { ModelInfo, ModelDetailResponse, ModelComparison } from '../../../types/dl';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

const ManagementPage: React.FC = () => {
  const {
    models,
    modelsLoading,
    loadModels,
    selectModel,
    selectedModel,
    selectedModelLoading,
    clearSelectedModel,
    activateModel,
    archiveModel,
    deleteModel,
    comparingModels,
    addToComparison,
    removeFromComparison,
    clearComparison,
    compareSelected,
    comparisonResult,
    comparisonLoading,
  } = useDLStore();

  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [comparisonModalVisible, setComparisonModalVisible] = useState(false);
  const [importModalVisible, setImportModalVisible] = useState(false);
  const [selectedModelForDetail, setSelectedModelForDetail] = useState<ModelInfo | null>(null);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // 加载模型列表
  useEffect(() => {
    loadModels();
  }, []);

  // 处理模型详情查看
  const handleViewDetail = async (model: ModelInfo) => {
    setSelectedModelForDetail(model);
    await selectModel(model.version);
    setDetailModalVisible(true);
  };

  // 处理模型激活
  const handleActivate = async (version: string) => {
    try {
      await activateModel(version);
      message.success('模型已激活');
    } catch (error) {
      message.error('激活模型失败');
    }
  };

  // 处理模型归档
  const handleArchive = async (version: string) => {
    try {
      await archiveModel(version);
      message.success('模型已归档');
    } catch (error) {
      message.error('归档模型失败');
    }
  };

  // 处理模型删除
  const handleDelete = async (version: string) => {
    try {
      await deleteModel(version);
      message.success('模型已删除');
    } catch (error) {
      message.error('删除模型失败');
    }
  };

  // 处理对比选择
  const handleToggleComparison = (version: string, checked: boolean) => {
    if (checked) {
      addToComparison(version);
    } else {
      removeFromComparison(version);
    }
  };

  // 开始对比
  const handleCompare = async () => {
    if (comparingModels.length < 2) {
      message.warning('请至少选择 2 个模型进行对比');
      return;
    }
    await compareSelected();
    setComparisonModalVisible(true);
  };

  // 模型状态标签
  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string; icon: React.ReactNode }> = {
      active: { color: 'green', text: '激活', icon: <CheckCircleOutlined /> },
      archived: { color: 'default', text: '归档', icon: <ArchiveOutlined /> },
      deleted: { color: 'red', text: '已删除', icon: <DeleteOutlined /> },
    };
    const config = statusMap[status] || statusMap.archived;
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    );
  };

  // 模型类型标签
  const getTypeTag = (type: string) => {
    const typeMap: Record<string, { color: string; text: string }> = {
      transformer: { color: 'purple', text: 'Transformer' },
      lstm: { color: 'blue', text: 'LSTM' },
    };
    const config = typeMap[type] || { color: 'default', text: type };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 表格列定义
  const columns: ColumnsType<ModelInfo> = [
    {
      title: '对比',
      key: 'compare',
      width: 60,
      render: (_, record) => (
        <Checkbox
          checked={comparingModels.includes(record.version)}
          onChange={(e) => handleToggleComparison(record.version, e.target.checked)}
          disabled={record.status !== 'active'}
        />
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '模型版本',
      dataIndex: 'version',
      key: 'version',
      width: 150,
      render: (version: string, record: ModelInfo) => (
        <Space direction="vertical" size={0}>
          <Text strong>{version}</Text>
          {record.name && <Text type="secondary" style={{ fontSize: 12 }}>{record.name}</Text>}
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => getTypeTag(type),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (date: string) => new Date(date).toLocaleDateString('zh-CN'),
    },
    {
      title: '验证准确率',
      dataIndex: ['metrics', 'val_accuracy'],
      key: 'val_accuracy',
      width: 100,
      render: (accuracy: number) => (
        <Space>
          <Progress
            percent={(accuracy || 0) * 100}
            size="small"
            strokeColor={{
              '0%': '#108ee9',
              '100%': '#87d068',
            }}
            format={(percent) => `${(percent / 100).toFixed(1)}`}
          />
        </Space>
      ),
    },
    {
      title: '文件大小',
      dataIndex: 'file_size_mb',
      key: 'file_size_mb',
      width: 80,
      render: (size: number) => `${size.toFixed(1)} MB`,
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space size="small" wrap>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          {record.status === 'active' ? (
            <Button
              type="link"
              size="small"
              icon={<ArchiveOutlined />}
              onClick={() => handleArchive(record.version)}
            >
              归档
            </Button>
          ) : (
            <Button
              type="link"
              size="small"
              icon={<PlayCircleOutlined />}
              onClick={() => handleActivate(record.version)}
            >
              激活
            </Button>
          )}
          <Button
            type="link"
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => message.info('导出功能开发中')}
          >
            导出
          </Button>
          <Popconfirm
            title="确定删除此模型？"
            description="此操作不可恢复"
            onConfirm={() => handleDelete(record.version)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 过滤模型列表
  const filteredModels = models.filter((model) => {
    const matchSearch = model.version.toLowerCase().includes(searchText.toLowerCase()) ||
      model.name?.toLowerCase().includes(searchText.toLowerCase());
    const matchStatus = statusFilter === 'all' || model.status === statusFilter;
    return matchSearch && matchStatus;
  });

  // 对比图表数据
  const comparisonChartData = comparisonResult
    ? Object.entries(comparisonResult.metrics_comparison).map(([metric, values]) => ({
        name: metric,
        ...Object.fromEntries(
          Object.entries(values).map(([version, value]) => [version, typeof value === 'number' ? value * 100 : value])
        ),
      }))
    : [];

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="mb-4 sm:mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-0">
        <Title level={2} style={{ margin: 0 }} className="text-xl sm:text-2xl lg:text-3xl">模型管理</Title>
        <Space 
          direction={{ xs: 'vertical', sm: 'horizontal' }}
          className="w-full sm:w-auto"
        >
          <Button
            icon={<UploadOutlined />}
            onClick={() => setImportModalVisible(true)}
            size={{ xs: 'middle', sm: 'default' }}
            className="w-full sm:w-auto"
            block={{ xs: true, sm: false }}
          >
            上传模型
          </Button>
          <Button
            icon={<CompareOutlined />}
            type="primary"
            onClick={handleCompare}
            disabled={comparingModels.length < 2}
            size={{ xs: 'middle', sm: 'default' }}
            className="w-full sm:w-auto"
            block={{ xs: true, sm: false }}
          >
            对比选中 ({comparingModels.length})
          </Button>
          {comparingModels.length > 0 && (
            <Button 
              onClick={clearComparison}
              size={{ xs: 'middle', sm: 'default' }}
              className="w-full sm:w-auto"
              block={{ xs: true, sm: false }}
            >
              清空对比
            </Button>
          )}
        </Space>
      </div>

      {/* 筛选和搜索 */}
      <Card className="mb-4 sm:mb-6" bodyStyle={{ padding: '12px sm:16px' }}>
        <Space wrap className="w-full">
          <Input
            placeholder="搜索模型版本或名称..."
            prefix={<InboxOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: '100%', minWidth: 200, flex: '1 1 auto' }}
            allowClear
          />
          <Select
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: '100%', minWidth: 140, flex: '0 0 auto' }}
          >
            <Option value="all">全部状态</Option>
            <Option value="active">激活</Option>
            <Option value="archived">归档</Option>
          </Select>
        </Space>
      </Card>

      {/* 模型列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredModels}
          rowKey="version"
          loading={modelsLoading}
          pagination={{ pageSize: 10, showSizeChanger: true }}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 模型详情弹窗 */}
      <Modal
        title={
          <Space>
            <ThunderboltOutlined />
            <span>模型详情：{selectedModelForDetail?.version}</span>
          </Space>
        }
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false);
          clearSelectedModel();
          setSelectedModelForDetail(null);
        }}
        width={900}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
          <Button key="export" icon={<DownloadOutlined />}>
            导出模型
          </Button>,
        ]}
      >
        {selectedModelLoading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Progress type="spin" />
          </div>
        ) : selectedModel ? (
          <Tabs>
            <Tabs.TabPane tab="基本信息" key="basic">
              <Descriptions column={2} bordered>
                <Descriptions.Item label="模型类型">
                  {getTypeTag(selectedModel.type)}
                </Descriptions.Item>
                <Descriptions.Item label="状态">
                  {getStatusTag(selectedModel.status)}
                </Descriptions.Item>
                <Descriptions.Item label="创建时间">
                  {new Date(selectedModel.created_at).toLocaleString('zh-CN')}
                </Descriptions.Item>
                <Descriptions.Item label="更新时间">
                  {new Date(selectedModel.updated_at).toLocaleString('zh-CN')}
                </Descriptions.Item>
                <Descriptions.Item label="文件大小">
                  {selectedModel.file_size_mb.toFixed(2)} MB
                </Descriptions.Item>
                <Descriptions.Item label="文件路径">
                  <Text code>{selectedModel.file_path}</Text>
                </Descriptions.Item>
                {selectedModel.description && (
                  <Descriptions.Item label="描述" span={2}>
                    {selectedModel.description}
                  </Descriptions.Item>
                )}
                {selectedModel.tags && selectedModel.tags.length > 0 && (
                  <Descriptions.Item label="标签" span={2}>
                    <Space wrap>
                      {selectedModel.tags.map((tag) => (
                        <Tag key={tag}>{tag}</Tag>
                      ))}
                    </Space>
                  </Descriptions.Item>
                )}
              </Descriptions>
            </Tabs.TabPane>

            <Tabs.TabPane tab="架构参数" key="params">
              <Descriptions column={2} bordered>
                {selectedModel.params.d_model && (
                  <Descriptions.Item label="d_model">{selectedModel.params.d_model}</Descriptions.Item>
                )}
                {selectedModel.params.num_heads && (
                  <Descriptions.Item label="num_heads">{selectedModel.params.num_heads}</Descriptions.Item>
                )}
                {selectedModel.params.num_layers && (
                  <Descriptions.Item label="num_layers">{selectedModel.params.num_layers}</Descriptions.Item>
                )}
                {selectedModel.params.hidden_size && (
                  <Descriptions.Item label="hidden_size">{selectedModel.params.hidden_size}</Descriptions.Item>
                )}
                {selectedModel.params.dropout && (
                  <Descriptions.Item label="dropout">{selectedModel.params.dropout}</Descriptions.Item>
                )}
                {selectedModel.params.activation && (
                  <Descriptions.Item label="activation">{selectedModel.params.activation}</Descriptions.Item>
                )}
              </Descriptions>
            </Tabs.TabPane>

            <Tabs.TabPane tab="训练配置" key="training">
              <Descriptions column={2} bordered>
                <Descriptions.Item label="数据源">{selectedModel.training_config.data_source}</Descriptions.Item>
                <Descriptions.Item label="时间范围">
                  {selectedModel.training_config.start_date} 至 {selectedModel.training_config.end_date}
                </Descriptions.Item>
                <Descriptions.Item label="Batch Size">{selectedModel.training_config.batch_size}</Descriptions.Item>
                <Descriptions.Item label="Learning Rate">{selectedModel.training_config.learning_rate}</Descriptions.Item>
                <Descriptions.Item label="Epochs">{selectedModel.training_config.epochs}</Descriptions.Item>
                <Descriptions.Item label="Optimizer">{selectedModel.training_config.optimizer}</Descriptions.Item>
                <Descriptions.Item label="训练样本">{selectedModel.training_config.train_samples.toLocaleString()}</Descriptions.Item>
                <Descriptions.Item label="验证样本">{selectedModel.training_config.val_samples.toLocaleString()}</Descriptions.Item>
              </Descriptions>
            </Tabs.TabPane>

            <Tabs.TabPane tab="性能指标" key="metrics">
              <Descriptions column={2} bordered>
                <Descriptions.Item label="验证准确率">
                  <Progress
                    percent={(selectedModel.metrics.val_accuracy || 0) * 100}
                    size="small"
                    format={(percent) => `${(percent / 100).toFixed(2)}`}
                  />
                </Descriptions.Item>
                <Descriptions.Item label="验证损失">
                  {selectedModel.metrics.val_loss?.toFixed(4)}
                </Descriptions.Item>
                {selectedModel.metrics.test_accuracy && (
                  <>
                    <Descriptions.Item label="测试准确率">
                      <Progress
                        percent={(selectedModel.metrics.test_accuracy || 0) * 100}
                        size="small"
                        format={(percent) => `${(percent / 100).toFixed(2)}`}
                      />
                    </Descriptions.Item>
                    <Descriptions.Item label="测试损失">
                      {selectedModel.metrics.test_loss?.toFixed(4)}
                    </Descriptions.Item>
                  </>
                )}
                {selectedModel.metrics.sharpe_ratio && (
                  <Descriptions.Item label="夏普比率">
                    <Text strong>{selectedModel.metrics.sharpe_ratio.toFixed(2)}</Text>
                  </Descriptions.Item>
                )}
                {selectedModel.metrics.max_drawdown && (
                  <Descriptions.Item label="最大回撤">
                    <Text type="danger">{(selectedModel.metrics.max_drawdown * 100).toFixed(2)}%</Text>
                  </Descriptions.Item>
                )}
              </Descriptions>
            </Tabs.TabPane>
          </Tabs>
        ) : (
          <Alert message="模型详情加载失败" type="error" showIcon />
        )}
      </Modal>

      {/* 模型对比弹窗 */}
      <Modal
        title={
          <Space>
            <CompareOutlined />
            <span>模型性能对比</span>
          </Space>
        }
        open={comparisonModalVisible}
        onCancel={() => setComparisonModalVisible(false)}
        width={1000}
        footer={[
          <Button key="close" onClick={() => setComparisonModalVisible(false)}>
            关闭
          </Button>,
        ]}
      >
        {comparisonLoading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Progress type="spin" />
          </div>
        ) : comparisonResult ? (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* 准确率对比图表 */}
            <Card title="准确率对比">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={comparisonChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  {comparingModels.map((version) => (
                    <Bar key={version} dataKey={version} fill={`hsl(${Math.random() * 360}, 70%, 50%)}`} />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </Card>

            {/* 详细指标对比表格 */}
            <Card title="详细指标对比">
              <Table
                dataSource={Object.entries(comparisonResult.metrics_comparison).map(([metric, values]) => ({
                  metric,
                  ...values,
                }))}
                pagination={false}
                size="small"
                columns={[
                  {
                    title: '指标',
                    dataIndex: 'metric',
                    key: 'metric',
                    render: (metric: string) => {
                      const metricNames: Record<string, string> = {
                        val_accuracy: '验证准确率',
                        val_loss: '验证损失',
                        test_accuracy: '测试准确率',
                        sharpe_ratio: '夏普比率',
                        max_drawdown: '最大回撤',
                      };
                      return metricNames[metric] || metric;
                    },
                  },
                  ...comparingModels.map((version) => ({
                    title: version,
                    dataIndex: version,
                    key: version,
                    render: (value: number) => {
                      if (value > 1) return value.toFixed(4); // 损失值
                      return `${(value * 100).toFixed(2)}%`; // 准确率
                    },
                  })),
                ]}
              />
            </Card>

            {/* 排名 */}
            {comparisonResult.ranking && (
              <Card title="综合排名">
                <Table
                  dataSource={comparisonResult.ranking}
                  pagination={false}
                  size="small"
                  columns={[
                    { title: '排名', dataIndex: 'rank', key: 'rank', width: 80 },
                    { title: '模型版本', dataIndex: 'version', key: 'version' },
                    {
                      title: '综合得分',
                      dataIndex: 'score',
                      key: 'score',
                      render: (score: number) => (
                        <Progress percent={score * 100} size="small" format={(p) => (p / 100).toFixed(2)} />
                      ),
                    },
                  ]}
                />
              </Card>
            )}
          </Space>
        ) : (
          <Alert message="对比数据加载失败" type="error" showIcon />
        )}
      </Modal>

      {/* 导入模型弹窗 */}
      <Modal
        title={
          <Space>
            <UploadOutlined />
            <span>上传模型</span>
          </Space>
        }
        open={importModalVisible}
        onCancel={() => setImportModalVisible(false)}
        footer={null}
      >
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Upload.Dragger
            name="file"
            multiple={false}
            accept=".pt,.pth,.onnx,.safetensors"
            style={{ padding: '20px' }}
          >
            <p className="ant-upload-drag-icon">
              <InboxOutlined style={{ color: '#1890ff' }} />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p className="ant-upload-hint">
              支持的文件格式：.pt, .pth, .onnx, .safetensors
            </p>
          </Upload.Dragger>
          <Alert
            message="模型导入功能开发中"
            description="后端 API 完成后将支持模型文件上传和自动识别"
            type="info"
            showIcon
            style={{ marginTop: 16 }}
          />
        </div>
      </Modal>
    </div>
  );
};

export default ManagementPage;
