// 模型推理页面单元测试
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import InferencePage from './InferencePage';
import { inferenceApi } from '../../../services/dl/inferenceApi';

// Mock inferenceApi
vi.mock('../../../services/dl/inferenceApi', () => ({
  inferenceApi: {
    getModels: vi.fn(),
    predictSingle: vi.fn(),
    predictBatch: vi.fn(),
    getBatchStatus: vi.fn(),
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

describe('InferencePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock getModels to return empty list
    vi.mocked(inferenceApi.getModels).mockResolvedValue({
      models: [],
    });
  });

  it('renders inference page with title', () => {
    render(<InferencePage />);
    expect(screen.getByText('模型推理')).toBeInTheDocument();
  });

  it('renders page description', () => {
    render(<InferencePage />);
    expect(screen.getByText(/使用训练好的深度学习模型对股票进行预测/)).toBeInTheDocument();
  });

  it('renders prediction configuration card', () => {
    render(<InferencePage />);
    expect(screen.getByText('预测配置')).toBeInTheDocument();
  });

  it('renders model version selector', () => {
    render(<InferencePage />);
    expect(screen.getByText('模型版本')).toBeInTheDocument();
  });

  it('renders stock code input', () => {
    render(<InferencePage />);
    expect(screen.getByText('股票代码')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('000001.SZ')).toBeInTheDocument();
  });

  it('renders prediction date picker', () => {
    render(<InferencePage />);
    expect(screen.getByText('预测日期')).toBeInTheDocument();
  });

  it('renders prediction horizon selector', () => {
    render(<InferencePage />);
    expect(screen.getByText('预测周期')).toBeInTheDocument();
    expect(screen.getByText('T+1 (明日)')).toBeInTheDocument();
    expect(screen.getByText('T+3 (3 日后)')).toBeInTheDocument();
    expect(screen.getByText('T+5 (周线)')).toBeInTheDocument();
  });

  it('renders start prediction button', () => {
    render(<InferencePage />);
    expect(screen.getByText('开始预测')).toBeInTheDocument();
  });

  it('renders batch prediction button', () => {
    render(<InferencePage />);
    expect(screen.getByText('批量预测')).toBeInTheDocument();
  });

  it('shows advanced batch panel when clicked', async () => {
    render(<InferencePage />);
    
    // Click batch prediction button
    const batchButton = screen.getByText('批量预测');
    fireEvent.click(batchButton);

    await waitFor(() => {
      expect(screen.getByText('批量预测配置')).toBeInTheDocument();
    });
  });

  it('renders stock list input for batch prediction', async () => {
    render(<InferencePage />);
    
    // Click batch prediction button
    const batchButton = screen.getByText('批量预测');
    fireEvent.click(batchButton);

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/每行一只股票/)).toBeInTheDocument();
    });
  });

  it('has responsive layout classes', () => {
    const { container } = render(<InferencePage />);
    const mainDiv = container.firstChild as HTMLElement;
    
    // Check for responsive padding classes
    expect(mainDiv).toHaveClass('p-4');
    expect(mainDiv).toHaveClass('sm:p-6');
    expect(mainDiv).toHaveClass('lg:p-8');
  });

  it('renders prediction result section when available', () => {
    render(<InferencePage />);
    // Result section exists but is hidden when no prediction
    expect(screen.queryByText('预测结果')).not.toBeInTheDocument();
  });

  it('renders feature importance chart section', () => {
    render(<InferencePage />);
    // Chart section exists but is hidden when no prediction
    expect(screen.queryByText('特征重要性')).not.toBeInTheDocument();
  });

  it('renders accuracy trend chart section', () => {
    render(<InferencePage />);
    // Chart section exists but is hidden when no prediction
    expect(screen.queryByText('历史准确率')).not.toBeInTheDocument();
  });

  it('renders export results button', () => {
    render(<InferencePage />);
    // Export button exists but is hidden when no results
    expect(screen.queryByText('导出结果')).not.toBeInTheDocument();
  });
});
