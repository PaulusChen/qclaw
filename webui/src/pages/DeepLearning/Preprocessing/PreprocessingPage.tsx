// 数据预处理配置页面
import React, { useEffect, useState } from 'react';
import {
  Typography,
  Card,
  Form,
  Input,
  Select,
  Radio,
  Checkbox,
  Button,
  Table,
  Collapse,
  Alert,
  Space,
  Progress,
  Tag,
  Modal,
  message as antdMessage,
  Divider,
  Row,
  Col,
  Statistic,
  Descriptions,
} from 'antd';
import {
  DatabaseOutlined,
  FileTextOutlined,
  TableOutlined,
  CheckOutlined,
  CloseOutlined,
  DownloadOutlined,
  UploadOutlined,
  PlayCircleOutlined,
  SaveOutlined,
  FolderOpenOutlined,
  SettingOutlined,
  InfoCircleOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { useDLStore } from '@/store/dlStore';
import type {
  DataSourceType,
  NormalizationMethod,
  PreprocessingConfig,
  FeatureGroup,
} from '@/types/dl/preprocessing';
import { AVAILABLE_FEATURES } from '@/types/dl/preprocessing';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

// 标准化方法说明
const NORMALIZATION_METHODS: Array<{
  value: NormalizationMethod;
  label: string;
  description: string;
  formula: string;
  applicable: string;
}> = [
  {
    value: 'zscore',
    label: 'Z-Score (标准差标准化)',
    description: '将特征转换为均值为 0，标准差为 1 的分布',
    formula: 'z = (x - μ) / σ',
    applicable: '特征近似正态分布',
  },
  {
    value: 'minmax',
    label: 'Min-Max (归一化)',
    description: '将特征缩放到指定范围',
    formula: "x' = (x - min) / (max - min)",
    applicable: '需要固定范围的场景',
  },
  {
    value: 'robust',
    label: 'Robust (稳健标准化)',
    description: '使用中位数和四分位距，对异常值不敏感',
    formula: "x' = (x - median) / IQR",
    applicable: '存在异常值的数据',
  },
  {
    value: 'rankgauss',
    label: 'RankGauss (秩变换)',
    description: '秩变换后高斯化，适用于任意分布',
    formula: '秩变换 + 反正态分布函数',
    applicable: '深度学习推荐，任意分布',
  },
];

// 缺失值处理方式
const MISSING_VALUE_HANDLERS: Array<{
  value: 'drop' | 'fill_mean' | 'fill_median' | 'fill_zero';
  label: string;
}> = [
  { value: 'drop', label: '删除缺失行' },
  { value: 'fill_mean', label: '填充均值' },
  { value: 'fill_median', label: '填充中位数' },
  { value: 'fill_zero', label: '填充零' },
];

// 异常值处理方式
const OUTLIER_HANDLERS: Array<{
  value: 'none' | 'clip' | 'remove';
  label: string;
}> = [
  { value: 'none', label: '不处理' },
  { value: 'clip', label: '截断到阈值范围' },
  { value: 'remove', label: '删除异常值' },
];

const PreprocessingPage: React.FC = () => {
  const [form] = Form.useForm();
  
  // Zustand state
  const {
    availableFeatures,
    featuresLoaded,
    currentConfig,
    dataStats,
    dataPreview,
    taskStatus,
    currentTask,
    savedConfigs,
    loadFeatures,
    updateConfig,
    setConfig,
    resetConfig,
    loadDataStats,
    loadDataPreview,
    saveConfig,
    loadSavedConfig,
    listSavedConfigs,
    applyPreprocessing,
    checkTaskStatus,
    cancelTask,
  } = useDLStore();

  // 本地状态
  const [dataSourceType, setDataSourceType] = useState<DataSourceType>('parquet');
  const [selectedFeatures, setSelectedFeatures] = useState<Set<string>>(new Set());
  const [normalizationMethod, setNormalizationMethod] = useState<NormalizationMethod>('zscore');
  const [expandedGroups, setExpandedGroups] = useState<string[]>(['价格类特征']);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showLoadModal, setShowLoadModal] = useState(false);
  const [configName, setConfigName] = useState('');
  const [configDescription, setConfigDescription] = useState('');
  const [processing, setProcessing] = useState(false);

  // 初始化
  useEffect(() => {
    loadFeatures();
    listSavedConfigs();
    
    // 初始化表单
    form.setFieldsValue({
      dataSourceType: 'parquet',
      filePath: '/home/qclaw/data/processed/stock_features.parquet',
      startDate: '2020-01-01',
      endDate: '2024-12-31',
      normalizationMethod: 'zscore',
      handleMissing: 'fill_mean',
      handleOutliers: 'clip',
      outlierThreshold: 3,
    });
  }, []);

  // 监听任务状态
  useEffect(() => {
    if (taskStatus === 'running') {
      const interval = setInterval(checkTaskStatus, 2000);
      return () => clearInterval(interval);
    }
  }, [taskStatus]);

  // 全选/全不选
  const handleSelectAll = () => {
    const allFeatures = AVAILABLE_FEATURES.flatMap(g => g.features.map(f => f.id));
    setSelectedFeatures(new Set(allFeatures));
  };

  const handleSelectNone = () => {
    setSelectedFeatures(new Set());
  };

  const handleSelectInverse = () => {
    const allFeatures = new Set(AVAILABLE_FEATURES.flatMap(g => g.features.map(f => f.id)));
    const newSelected = new Set<string>();
    allFeatures.forEach(f => {
      if (!selectedFeatures.has(f)) {
        newSelected.add(f);
      }
    });
    setSelectedFeatures(newSelected);
  };

  // 切换特征选择
  const handleFeatureToggle = (featureId: string) => {
    const newSelected = new Set(selectedFeatures);
    if (newSelected.has(featureId)) {
      newSelected.delete(featureId);
    } else {
      newSelected.add(featureId);
    }
    setSelectedFeatures(newSelected);
  };

  // 切换分组选择
  const handleGroupToggle = (group: FeatureGroup, checked: boolean) => {
    const newSelected = new Set(selectedFeatures);
    group.features.forEach(f => {
      if (checked) {
        newSelected.add(f.id);
      } else {
        newSelected.delete(f.id);
      }
    });
    setSelectedFeatures(newSelected);
  };

  // 获取分组选择状态
  const getGroupCheckStatus = (group: FeatureGroup): boolean | null => {
    const selectedInGroup = group.features.filter(f => selectedFeatures.has(f.id));
    if (selectedInGroup.length === 0) return false;
    if (selectedInGroup.length === group.features.length) return true;
    return null; // 部分选择
  };

  // 保存配置
  const handleSaveConfig = async () => {
    if (!configName.trim()) {
      antdMessage.error('请输入配置名称');
      return;
    }
    
    try {
      await saveConfig(configName, configDescription || undefined);
      antdMessage.success('配置已保存');
      setShowSaveModal(false);
      setConfigName('');
      setConfigDescription('');
      listSavedConfigs();
    } catch (error) {
      antdMessage.error('保存失败');
    }
  };

  // 加载配置
  const handleLoadConfig = async (configId: string) => {
    try {
      await loadSavedConfig(configId);
      antdMessage.success('配置已加载');
      setShowLoadModal(false);
      
      // 更新本地状态
      const config = useDLStore.getState().currentConfig;
      if (config) {
        setDataSourceType(config.data_source.type);
        setNormalizationMethod(config.normalization.method);
        setSelectedFeatures(new Set(config.selected_features));
        form.setFieldsValue({
          dataSourceType: config.data_source.type,
          filePath: config.data_source.file_path,
          startDate: config.data_source.start_date,
          endDate: config.data_source.end_date,
          normalizationMethod: config.normalization.method,
          handleMissing: config.handle_missing,
          handleOutliers: config.handle_outliers,
          outlierThreshold: config.outlier_threshold,
        });
      }
    } catch (error) {
      antdMessage.error('加载失败');
    }
  };

  // 应用预处理
  const handleApplyPreprocessing = async () => {
    const values = await form.validateFields();
    
    const config: PreprocessingConfig = {
      name: configName || '临时配置',
      data_source: {
        type: dataSourceType,
        file_path: values.filePath,
        start_date: values.startDate,
        end_date: values.endDate,
      },
      selected_features: Array.from(selectedFeatures),
      normalization: {
        method: normalizationMethod,
      },
      handle_missing: values.handleMissing,
      handle_outliers: values.handleOutliers,
      outlier_threshold: values.outlierThreshold,
    };
    
    setConfig(config);
    setProcessing(true);
    
    try {
      const taskId = await applyPreprocessing();
      antdMessage.success(`预处理任务已启动：${taskId}`);
    } catch (error) {
      antdMessage.error('启动预处理失败');
      setProcessing(false);
    }
  };

  // 取消任务
  const handleCancelTask = async () => {
    await cancelTask();
    setProcessing(false);
    antdMessage.info('任务已取消');
  };

  // 加载数据统计
  const handleLoadStats = async () => {
    const values = form.getFieldsValue();
    await loadDataStats(
      values.filePath || 'default',
      values.startDate || '2020-01-01',
      values.endDate || '2024-12-31'
    );
    antdMessage.success('数据统计已加载');
  };

  // 加载数据预览
  const handleLoadPreview = async () => {
    const values = form.getFieldsValue();
    await loadDataPreview(values.filePath || 'default', 10);
    antdMessage.success('数据预览已加载');
  };

  // 渲染数据源配置
  const renderDataSourceConfig = () => (
    <Card
      title={<><DatabaseOutlined className="mr-2" />数据源配置</>}
      className="mb-4"
      extra={
        <Button icon={<ReloadOutlined />} onClick={handleLoadStats}>
          刷新统计
        </Button>
      }
    >
      <Form form={form} layout="vertical">
        <Form.Item label="数据源类型" name="dataSourceType">
          <Radio.Group
            value={dataSourceType}
            onChange={e => setDataSourceType(e.target.value)}
          >
            <Radio value="database"><DatabaseOutlined /> 数据库连接</Radio>
            <Radio value="parquet"><FileTextOutlined /> Parquet 文件</Radio>
            <Radio value="csv"><TableOutlined /> CSV 文件</Radio>
          </Radio.Group>
        </Form.Item>

        {dataSourceType === 'parquet' || dataSourceType === 'csv' ? (
          <Form.Item
            label="文件路径"
            name="filePath"
            rules={[{ required: true, message: '请输入文件路径' }]}
          >
            <Input
              placeholder="/home/qclaw/data/processed/stock_features.parquet"
              suffix={
                <Button size="small" icon={<FolderOpenOutlined />}>
                  浏览
                </Button>
              }
            />
          </Form.Item>
        ) : (
          <>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item label="数据库主机" name="dbHost">
                  <Input placeholder="localhost" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="端口" name="dbPort">
                  <Input placeholder="5432" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item label="数据库名" name="dbName">
                  <Input placeholder="qclaw" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="表名" name="dbTable">
                  <Input placeholder="stock_features" />
                </Form.Item>
              </Col>
            </Row>
          </>
        )}

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              label="开始日期"
              name="startDate"
              rules={[{ required: true, message: '请选择开始日期' }]}
            >
              <Input type="date" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              label="结束日期"
              name="endDate"
              rules={[{ required: true, message: '请选择结束日期' }]}
            >
              <Input type="date" />
            </Form.Item>
          </Col>
        </Row>

        {/* 数据统计展示 */}
        {dataStats && (
          <Card size="small" className="mt-4 bg-gray-50">
            <Title level={5}>数据统计</Title>
            <Row gutter={16}>
              <Col span={6}>
                <Statistic
                  title="总行数"
                  value={dataStats.total_rows}
                  suffix="条"
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="特征数"
                  value={dataStats.feature_count}
                  suffix="个"
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="缺失率"
                  value={dataStats.missing_rate * 100}
                  suffix="%"
                  precision={2}
                />
              </Col>
              <Col span={6}>
                <Text type="secondary">
                  时间范围：{dataStats.date_range.start} 至 {dataStats.date_range.end}
                </Text>
              </Col>
            </Row>
          </Card>
        )}
      </Form>
    </Card>
  );

  // 渲染特征选择器
  const renderFeatureSelector = () => (
    <Card
      title={<><SettingOutlined className="mr-2" />特征选择 ({selectedFeatures.size}/38)</>}
      className="mb-4"
      extra={
        <Space>
          <Input
            placeholder="搜索特征..."
            style={{ width: 200 }}
            prefix={<InfoCircleOutlined />}
          />
          <Button size="small" onClick={handleSelectAll}>全选</Button>
          <Button size="small" onClick={handleSelectNone}>全不选</Button>
          <Button size="small" onClick={handleSelectInverse}>反选</Button>
        </Space>
      }
    >
      <Collapse
        activeKey={expandedGroups}
        onChange={keys => setExpandedGroups(keys as string[])}
        accordion={false}
      >
        {AVAILABLE_FEATURES.map((group, groupIndex) => {
          const checkStatus = getGroupCheckStatus(group);
          return (
            <Collapse.Panel
              key={group.name}
              header={
                <div className="flex items-center justify-between w-full">
                  <span>{group.name}</span>
                  <Checkbox
                    checked={checkStatus === true}
                    indeterminate={checkStatus === null}
                    onChange={e => handleGroupToggle(group, e.target.checked)}
                    onClick={e => e.stopPropagation()}
                  >
                    {group.features.filter(f => selectedFeatures.has(f.id)).length}/{group.features.length}
                  </Checkbox>
                </div>
              }
            >
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                {group.features.map(feature => (
                  <Checkbox
                    key={feature.id}
                    checked={selectedFeatures.has(feature.id)}
                    onChange={() => handleFeatureToggle(feature.id)}
                    title={feature.description}
                  >
                    <span className="text-sm">{feature.name}</span>
                  </Checkbox>
                ))}
              </div>
            </Collapse.Panel>
          );
        })}
      </Collapse>
    </Card>
  );

  // 渲染标准化配置
  const renderNormalizationConfig = () => (
    <Card
      title={<><SettingOutlined className="mr-2" />标准化配置</>}
      className="mb-4"
    >
      <Form form={form} layout="vertical">
        <Form.Item label="标准化方法" name="normalizationMethod">
          <Radio.Group
            value={normalizationMethod}
            onChange={e => setNormalizationMethod(e.target.value)}
          >
            <div className="space-y-3">
              {NORMALIZATION_METHODS.map(method => (
                <div
                  key={method.value}
                  className={`p-3 border rounded-lg cursor-pointer transition-all ${
                    normalizationMethod === method.value
                      ? 'border-purple-500 bg-purple-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setNormalizationMethod(method.value)}
                >
                  <Radio value={method.value} className="font-medium">
                    {method.label}
                  </Radio>
                  <Paragraph type="secondary" className="mb-1 mt-2">
                    {method.description}
                  </Paragraph>
                  <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                    {method.formula}
                  </code>
                  <div className="mt-1 text-xs text-gray-500">
                    适用：{method.applicable}
                  </div>
                </div>
              ))}
            </div>
          </Radio.Group>
        </Form.Item>

        <Divider />

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              label="缺失值处理"
              name="handleMissing"
              initialValue="fill_mean"
            >
              <Select>
                {MISSING_VALUE_HANDLERS.map(handler => (
                  <Select.Option key={handler.value} value={handler.value}>
                    {handler.label}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              label="异常值处理"
              name="handleOutliers"
              initialValue="clip"
            >
              <Select>
                {OUTLIER_HANDLERS.map(handler => (
                  <Select.Option key={handler.value} value={handler.value}>
                    {handler.label}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          label="异常值阈值 (标准差倍数)"
          name="outlierThreshold"
          initialValue={3}
        >
          <Input type="number" min={1} max={5} step={0.5} />
        </Form.Item>
      </Form>
    </Card>
  );

  // 渲染数据预览
  const renderDataPreview = () => (
    <Card
      title={<><TableOutlined className="mr-2" />数据预览</>}
      className="mb-4"
      extra={
        <Button icon={<ReloadOutlined />} onClick={handleLoadPreview}>
          刷新预览
        </Button>
      }
    >
      {dataPreview ? (
        <>
          {/* 统计信息表格 */}
          <Title level={5}>特征统计</Title>
          <Table
            size="small"
            columns={[
              { title: '特征', dataIndex: 'feature_name', key: 'feature_name', fixed: 'left', width: 120 },
              { title: '均值', dataIndex: 'mean', key: 'mean', render: (v: number) => v?.toFixed(4) },
              { title: '标准差', dataIndex: 'std', key: 'std', render: (v: number) => v?.toFixed(4) },
              { title: '最小值', dataIndex: 'min', key: 'min', render: (v: number) => v?.toFixed(4) },
              { title: '最大值', dataIndex: 'max', key: 'max', render: (v: number) => v?.toFixed(4) },
              { title: '缺失率', dataIndex: 'missing_rate', key: 'missing_rate', render: (v: number) => `${(v * 100).toFixed(2)}%` },
            ]}
            dataSource={dataPreview.statistics}
            pagination={false}
            scroll={{ x: 800 }}
            className="mb-4"
          />

          <Divider />

          {/* 样本数据 */}
          <Title level={5}>样本数据 (前 5 行)</Title>
          <Table
            size="small"
            columns={dataPreview.columns.map(col => ({
              title: col,
              dataIndex: col,
              key: col,
            }))}
            dataSource={dataPreview.data.slice(0, 5)}
            pagination={false}
            scroll={{ x: 1000 }}
          />
        </>
      ) : (
        <div className="text-center py-12">
          <TableOutlined style={{ fontSize: 64, color: '#d9d9d9', marginBottom: 16 }} />
          <Title level={5}>暂无数据预览</Title>
          <Text type="secondary">点击"刷新预览"加载数据</Text>
        </div>
      )}
    </Card>
  );

  // 渲染任务进度
  const renderTaskProgress = () => {
    if (taskStatus === 'idle' || !currentTask) return null;

    return (
      <Modal
        title={
          <Space>
            {taskStatus === 'running' ? <PlayCircleOutlined spin /> : 
             taskStatus === 'completed' ? <CheckOutlined /> : 
             <CloseOutlined />}
            预处理任务状态
          </Space>
        }
        open={true}
        footer={
          taskStatus === 'running' ? (
            <Button danger onClick={handleCancelTask}>取消任务</Button>
          ) : (
            <Button onClick={() => setProcessing(false)}>关闭</Button>
          )
        }
        onCancel={() => taskStatus !== 'running' && setProcessing(false)}
      >
        {currentTask.progress && (
          <>
            <Progress
              percent={(currentTask.progress.current_step / currentTask.progress.total_steps) * 100}
              status={taskStatus === 'error' ? 'exception' : taskStatus === 'completed' ? 'success' : 'active'}
              format={() => currentTask.progress.current_action}
            />
            
            <Descriptions column={1} size="small" className="mt-4">
              <Descriptions.Item label="任务 ID">{currentTask.task_id}</Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={
                  taskStatus === 'running' ? 'blue' :
                  taskStatus === 'completed' ? 'green' : 'red'
                }>
                  {taskStatus}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="进度">
                {currentTask.progress.current_step} / {currentTask.progress.total_steps}
              </Descriptions.Item>
              {currentTask.result && (
                <>
                  <Descriptions.Item label="处理行数">
                    {currentTask.result.processed_rows}
                  </Descriptions.Item>
                  <Descriptions.Item label="特征数">
                    {currentTask.result.feature_count}
                  </Descriptions.Item>
                  <Descriptions.Item label="处理时间">
                    {currentTask.result.processing_time_seconds}s
                  </Descriptions.Item>
                </>
              )}
            </Descriptions>

            {currentTask.error && (
              <Alert
                message="错误"
                description={currentTask.error}
                type="error"
                showIcon
                className="mt-4"
              />
            )}
          </>
        )}
      </Modal>
    );
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <Title level={2}>数据预处理配置</Title>
        <Text type="secondary">
          配置数据源、选择特征、设置标准化方法，为深度学习模型准备训练数据
        </Text>
      </div>

      {/* 任务进度弹窗 */}
      {renderTaskProgress()}

      {/* 保存配置弹窗 */}
      <Modal
        title="保存预处理配置"
        open={showSaveModal}
        onOk={handleSaveConfig}
        onCancel={() => {
          setShowSaveModal(false);
          setConfigName('');
          setConfigDescription('');
        }}
        okText="保存"
        cancelText="取消"
      >
        <Form layout="vertical">
          <Form.Item label="配置名称" required>
            <Input
              value={configName}
              onChange={e => setConfigName(e.target.value)}
              placeholder="例如：A 股全市场标准化配置"
            />
          </Form.Item>
          <Form.Item label="描述 (可选)">
            <TextArea
              value={configDescription}
              onChange={e => setConfigDescription(e.target.value)}
              placeholder="描述此配置的用途..."
              rows={3}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 加载配置弹窗 */}
      <Modal
        title="加载预处理配置"
        open={showLoadModal}
        footer={null}
        onCancel={() => setShowLoadModal(false)}
      >
        {savedConfigs.length > 0 ? (
          <div className="space-y-2">
            {savedConfigs.map(config => (
              <Card
                key={config.id}
                size="small"
                className="cursor-pointer hover:border-purple-500 transition-all"
                onClick={() => handleLoadConfig(config.id)}
              >
                <div className="flex justify-between items-center">
                  <div>
                    <Title level={5} className="mb-1">{config.name}</Title>
                    <Text type="secondary" className="text-xs">
                      {config.description || '无描述'}
                    </Text>
                  </div>
                  <Text type="secondary" className="text-xs">
                    {new Date(config.updated_at).toLocaleDateString()}
                  </Text>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Text type="secondary">暂无已保存的配置</Text>
          </div>
        )}
      </Modal>

      {/* 主内容区 */}
      {renderDataSourceConfig()}
      {renderFeatureSelector()}
      {renderNormalizationConfig()}
      {renderDataPreview()}

      {/* 底部操作栏 */}
      <Card className="sticky bottom-4 shadow-lg">
        <div className="flex justify-between items-center">
          <Space>
            <Button
              icon={<SaveOutlined />}
              onClick={() => setShowSaveModal(true)}
            >
              保存配置
            </Button>
            <Button
              icon={<FolderOpenOutlined />}
              onClick={() => setShowLoadModal(true)}
            >
              加载配置
            </Button>
          </Space>

          <Space>
            <Text type="secondary">
              已选特征：{selectedFeatures.size}/38
            </Text>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              size="large"
              loading={processing && taskStatus === 'running'}
              onClick={handleApplyPreprocessing}
              disabled={selectedFeatures.size === 0}
            >
              {processing ? '处理中...' : '应用并处理数据'}
            </Button>
          </Space>
        </div>
      </Card>
    </div>
  );
};

export default PreprocessingPage;
