// 模型训练页面单元测试
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import TrainingPage from './TrainingPage';
import { trainingApi } from '../../../services/dl/trainingApi';

// Mock trainingApi
vi.mock('../../../services/dl/trainingApi', () => ({
  trainingApi: {
    startTraining: vi.fn(),
    stopTraining: vi.fn(),
    getTrainingStatus: vi.fn(),
    createTrainingWebSocket: vi.fn(),
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

describe('TrainingPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders training page with title', () => {
    render(<TrainingPage />);
    expect(screen.getByText('模型训练')).toBeInTheDocument();
  });

  it('renders model selection dropdown', () => {
    render(<TrainingPage />);
    expect(screen.getByText('模型架构')).toBeInTheDocument();
    expect(screen.getByText('LSTM')).toBeInTheDocument();
    expect(screen.getByText('Transformer')).toBeInTheDocument();
  });

  it('renders training parameters', () => {
    render(<TrainingPage />);
    expect(screen.getByText('训练参数')).toBeInTheDocument();
    expect(screen.getByText('batch_size')).toBeInTheDocument();
    expect(screen.getByText('learning_rate')).toBeInTheDocument();
    expect(screen.getByText('epochs')).toBeInTheDocument();
  });

  it('renders data configuration section', () => {
    render(<TrainingPage />);
    expect(screen.getByText('数据配置')).toBeInTheDocument();
    expect(screen.getByText('数据源')).toBeInTheDocument();
    expect(screen.getByText('开始日期')).toBeInTheDocument();
    expect(screen.getByText('结束日期')).toBeInTheDocument();
  });

  it('renders advanced options collapsible panel', () => {
    render(<TrainingPage />);
    expect(screen.getByText('高级选项')).toBeInTheDocument();
  });

  it('renders start training button', () => {
    render(<TrainingPage />);
    expect(screen.getByText('开始训练')).toBeInTheDocument();
  });

  it('renders reset button', () => {
    render(<TrainingPage />);
    expect(screen.getByText('重置')).toBeInTheDocument();
  });

  it('disables start button when training is running', async () => {
    const { container } = render(<TrainingPage />);
    
    // Mock startTraining to return a task
    vi.mocked(trainingApi.startTraining).mockResolvedValue({
      task_id: 'test-task-123',
      status: 'running',
    });

    // Click start training button
    const startButton = screen.getByText('开始训练');
    fireEvent.click(startButton);

    await waitFor(() => {
      // Button should be disabled during training
      expect(startButton).toBeDisabled();
    });
  });

  it('shows model-specific parameters for Transformer', () => {
    render(<TrainingPage />);
    // Transformer is default, should show d_model and num_heads
    expect(screen.getByText('d_model')).toBeInTheDocument();
    expect(screen.getByText('num_heads')).toBeInTheDocument();
  });

  it('shows model-specific parameters for LSTM when selected', async () => {
    render(<TrainingPage />);
    
    // Select LSTM model
    const modelSelect = screen.getByRole('combobox', { name: /模型架构/i });
    fireEvent.mouseDown(modelSelect);
    
    await waitFor(() => {
      const lstmOption = screen.getByText('LSTM');
      fireEvent.click(lstmOption);
    });

    // Should show LSTM-specific parameters
    await waitFor(() => {
      expect(screen.getByText('hidden_size')).toBeInTheDocument();
      expect(screen.getByText('双向 LSTM')).toBeInTheDocument();
    });
  });

  it('renders training status statistics', () => {
    render(<TrainingPage />);
    expect(screen.getByText('状态')).toBeInTheDocument();
    expect(screen.getByText('Epoch')).toBeInTheDocument();
    expect(screen.getByText('当前损失')).toBeInTheDocument();
  });

  it('renders training monitoring card', () => {
    render(<TrainingPage />);
    expect(screen.getByText('训练监控')).toBeInTheDocument();
  });

  it('renders training logs card', () => {
    render(<TrainingPage />);
    expect(screen.getByText('训练日志')).toBeInTheDocument();
  });

  it('has responsive layout classes', () => {
    const { container } = render(<TrainingPage />);
    const mainDiv = container.firstChild as HTMLElement;
    
    // Check for responsive padding classes
    expect(mainDiv).toHaveClass('p-4');
    expect(mainDiv).toHaveClass('sm:p-6');
    expect(mainDiv).toHaveClass('lg:p-8');
  });
});
