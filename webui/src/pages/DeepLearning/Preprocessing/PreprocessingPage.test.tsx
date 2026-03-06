// 数据预处理页面单元测试
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import PreprocessingPage from './PreprocessingPage';
import { preprocessingApi } from '../../../services/dl/preprocessingApi';

// Mock preprocessingApi
vi.mock('../../../services/dl/preprocessingApi', () => ({
  preprocessingApi: {
    getDataSources: vi.fn(),
    getFeatures: vi.fn(),
    applyPreprocessing: vi.fn(),
    saveConfig: vi.fn(),
    loadConfig: vi.fn(),
    getConfigs: vi.fn(),
  },
}));

// Mock antd message
vi.mock('antd', async () => {
  const actual = await vi.importActual('antd');
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn(),
    },
  };
});

const mockFeatures = [
  { id: 'price_return_1d', name: '1 日收益率', category: '价格动量', description: '过去 1 天的收益率' },
  { id: 'price_return_5d', name: '5 日收益率', category: '价格动量', description: '过去 5 天的收益率' },
  { id: 'volume_ma_ratio', name: '成交量均线比', category: '成交量', description: '成交量与均值的比率' },
  { id: 'macd', name: 'MACD', category: '技术指标', description: '移动平均收敛散度' },
  { id: 'rsi', name: 'RSI', category: '技术指标', description: '相对强弱指数' },
  { id: 'kdj_k', name: 'KDJ-K', category: '技术指标', description: 'KDJ 指标的 K 值' },
];

describe('PreprocessingPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock getFeatures to return mock data
    vi.mocked(preprocessingApi.getFeatures).mockResolvedValue({
      features: mockFeatures,
    });
  });

  it('renders preprocessing page with title', () => {
    render(<PreprocessingPage />);
    expect(screen.getByText('数据预处理配置')).toBeInTheDocument();
  });

  it('renders page description', () => {
    render(<PreprocessingPage />);
    expect(screen.getByText(/配置数据源、选择特征/)).toBeInTheDocument();
  });

  it('renders data source configuration section', () => {
    render(<PreprocessingPage />);
    expect(screen.getByText('数据源配置')).toBeInTheDocument();
  });

  it('renders data source selector', () => {
    render(<PreprocessingPage />);
    expect(screen.getByText('数据源类型')).toBeInTheDocument();
  });

  it('renders date range inputs', () => {
    render(<PreprocessingPage />);
    expect(screen.getByText('开始日期')).toBeInTheDocument();
    expect(screen.getByText('结束日期')).toBeInTheDocument();
  });

  it('renders feature selector section', () => {
    render(<PreprocessingPage />);
    expect(screen.getByText('特征选择')).toBeInTheDocument();
  });

  it('renders feature categories', async () => {
    render(<PreprocessingPage />);
    await waitFor(() => {
      expect(screen.getByText('价格动量')).toBeInTheDocument();
      expect(screen.getByText('技术指标')).toBeInTheDocument();
    });
  });

  it('renders feature checkboxes', async () => {
    render(<PreprocessingPage />);
    await waitFor(() => {
      expect(screen.getByText('1 日收益率')).toBeInTheDocument();
      expect(screen.getByText('MACD')).toBeInTheDocument();
      expect(screen.getByText('RSI')).toBeInTheDocument();
    });
  });

  it('renders normalization configuration section', () => {
    render(<PreprocessingPage />);
    expect(screen.getByText('标准化配置')).toBeInTheDocument();
  });

  it('renders normalization method selector', () => {
    render(<PreprocessingPage />);
    expect(screen.getByText('标准化方法')).toBeInTheDocument();
  });

  it('renders data preview section', () => {
    render(<PreprocessingPage />);
    expect(screen.getByText('数据预览')).toBeInTheDocument();
  });

  it('renders save configuration button', () => {
    render(<PreprocessingPage />);
    expect(screen.getByText('保存配置')).toBeInTheDocument();
  });

  it('renders load configuration button', () => {
    render(<PreprocessingPage />);
    expect(screen.getByText('加载配置')).toBeInTheDocument();
  });

  it('renders apply preprocessing button', () => {
    render(<PreprocessingPage />);
    expect(screen.getByText('应用并处理数据')).toBeInTheDocument();
  });

  it('shows selected features count', () => {
    render(<PreprocessingPage />);
    expect(screen.getByText(/已选特征：\d+\/38/)).toBeInTheDocument();
  });

  it('allows selecting features', async () => {
    render(<PreprocessingPage />);
    await waitFor(async () => {
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[0]);
      
      await waitFor(() => {
        expect(screen.getByText(/已选特征：1\/38/)).toBeInTheDocument();
      });
    });
  });

  it('opens save config modal when save button clicked', () => {
    render(<PreprocessingPage />);
    const saveButton = screen.getByText('保存配置');
    fireEvent.click(saveButton);
    
    expect(screen.getByText('保存预处理配置')).toBeInTheDocument();
  });

  it('opens load config modal when load button clicked', () => {
    render(<PreprocessingPage />);
    const loadButton = screen.getByText('加载配置');
    fireEvent.click(loadButton);
    
    expect(screen.getByText('加载预处理配置')).toBeInTheDocument();
  });

  it('has responsive layout classes', () => {
    const { container } = render(<PreprocessingPage />);
    const mainDiv = container.firstChild as HTMLElement;
    
    // Check for responsive padding classes
    expect(mainDiv).toHaveClass('p-4');
    expect(mainDiv).toHaveClass('sm:p-6');
    expect(mainDiv).toHaveClass('lg:p-8');
  });

  it('renders feature category collapse panels', async () => {
    render(<PreprocessingPage />);
    await waitFor(() => {
      expect(screen.getByText('价格动量')).toBeInTheDocument();
      expect(screen.getByText('技术指标')).toBeInTheDocument();
      expect(screen.getByText('成交量')).toBeInTheDocument();
    });
  });

  it('renders normalization parameters', () => {
    render(<PreprocessingPage />);
    expect(screen.getByText('参数配置')).toBeInTheDocument();
  });

  it('disables apply button when no features selected', () => {
    render(<PreprocessingPage />);
    const applyButton = screen.getByText('应用并处理数据');
    expect(applyButton).toBeDisabled();
  });

  it('shows advanced options section', () => {
    render(<PreprocessingPage />);
    expect(screen.getByText('高级选项')).toBeInTheDocument();
  });

  it('renders outlier handling options', async () => {
    render(<PreprocessingPage />);
    await waitFor(() => {
      expect(screen.getByText('异常值处理')).toBeInTheDocument();
    });
  });

  it('renders missing value handling options', async () => {
    render(<PreprocessingPage />);
    await waitFor(() => {
      expect(screen.getByText('缺失值处理')).toBeInTheDocument();
    });
  });
});
