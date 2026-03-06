// 模型管理页面单元测试
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ManagementPage from './ManagementPage';
import { managementApi } from '../../../services/dl/managementApi';

// Mock managementApi
vi.mock('../../../services/dl/managementApi', () => ({
  managementApi: {
    getModels: vi.fn(),
    activateModel: vi.fn(),
    archiveModel: vi.fn(),
    deleteModel: vi.fn(),
    exportModel: vi.fn(),
    compareModels: vi.fn(),
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

const mockModels = [
  {
    version: 'v1.0.0',
    name: 'LSTM Base',
    type: 'LSTM',
    status: 'active',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    metrics: {
      val_accuracy: 0.85,
      sharpe_ratio: 2.1,
      max_drawdown: 0.15,
    },
    is_active: true,
  },
  {
    version: 'v1.1.0',
    name: 'Transformer Base',
    type: 'Transformer',
    status: 'archived',
    created_at: '2024-02-01T00:00:00Z',
    updated_at: '2024-02-01T00:00:00Z',
    metrics: {
      val_accuracy: 0.87,
      sharpe_ratio: 2.3,
      max_drawdown: 0.12,
    },
    is_active: false,
  },
];

describe('ManagementPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock getModels to return mock data
    vi.mocked(managementApi.getModels).mockResolvedValue({
      models: mockModels,
      total: 2,
      page: 1,
      page_size: 10,
    });
  });

  it('renders management page with title', async () => {
    render(<ManagementPage />);
    await waitFor(() => {
      expect(screen.getByText('模型管理')).toBeInTheDocument();
    });
  });

  it('renders upload model button', async () => {
    render(<ManagementPage />);
    await waitFor(() => {
      expect(screen.getByText('上传模型')).toBeInTheDocument();
    });
  });

  it('renders compare button', async () => {
    render(<ManagementPage />);
    await waitFor(() => {
      expect(screen.getByText(/对比选中/)).toBeInTheDocument();
    });
  });

  it('renders search input', async () => {
    render(<ManagementPage />);
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/搜索模型版本或名称/)).toBeInTheDocument();
    });
  });

  it('renders status filter dropdown', async () => {
    render(<ManagementPage />);
    await waitFor(() => {
      expect(screen.getByText('全部状态')).toBeInTheDocument();
    });
  });

  it('renders model list table', async () => {
    render(<ManagementPage />);
    await waitFor(() => {
      // Table should show model data
      expect(screen.getByText('v1.0.0')).toBeInTheDocument();
      expect(screen.getByText('LSTM Base')).toBeInTheDocument();
    });
  });

  it('displays model type badges', async () => {
    render(<ManagementPage />);
    await waitFor(() => {
      expect(screen.getByText('LSTM')).toBeInTheDocument();
      expect(screen.getByText('Transformer')).toBeInTheDocument();
    });
  });

  it('displays model status tags', async () => {
    render(<ManagementPage />);
    await waitFor(() => {
      expect(screen.getByText('激活')).toBeInTheDocument();
    });
  });

  it('shows model metrics in table', async () => {
    render(<ManagementPage />);
    await waitFor(() => {
      // Metrics should be displayed
      expect(screen.getByText(/85.0%/)).toBeInTheDocument();
    });
  });

  it('allows selecting models for comparison', async () => {
    render(<ManagementPage />);
    await waitFor(() => {
      // Checkbox for selecting models should exist
      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes.length).toBeGreaterThan(0);
    });
  });

  it('updates compare button count when models selected', async () => {
    render(<ManagementPage />);
    await waitFor(async () => {
      // Select a model
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[0]);
      
      await waitFor(() => {
        expect(screen.getByText('对比选中 (1)')).toBeInTheDocument();
      });
    });
  });

  it('renders model detail modal trigger', async () => {
    render(<ManagementPage />);
    await waitFor(() => {
      // Detail button should exist for each row
      const detailButtons = screen.getAllByText('详情');
      expect(detailButtons.length).toBeGreaterThan(0);
    });
  });

  it('has responsive layout classes', async () => {
    const { container } = render(<ManagementPage />);
    await waitFor(() => {
      const mainDiv = container.firstChild as HTMLElement;
      
      // Check for responsive padding classes
      expect(mainDiv).toHaveClass('p-4');
      expect(mainDiv).toHaveClass('sm:p-6');
      expect(mainDiv).toHaveClass('lg:p-8');
    });
  });

  it('renders clear comparison button when models selected', async () => {
    render(<ManagementPage />);
    await waitFor(async () => {
      // Select a model
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[0]);
      
      await waitFor(() => {
        expect(screen.getByText('清空对比')).toBeInTheDocument();
      });
    });
  });

  it('filters models by search text', async () => {
    render(<ManagementPage />);
    await waitFor(async () => {
      const searchInput = screen.getByPlaceholderText(/搜索模型版本或名称/);
      fireEvent.change(searchInput, { target: { value: 'LSTM' } });
      
      await waitFor(() => {
        expect(screen.getByText('LSTM Base')).toBeInTheDocument();
      });
    });
  });

  it('filters models by status', async () => {
    render(<ManagementPage />);
    await waitFor(async () => {
      const statusFilter = screen.getByText('全部状态');
      fireEvent.mouseDown(statusFilter);
      
      await waitFor(() => {
        const activeOption = screen.getByText('激活');
        fireEvent.click(activeOption);
      });
      
      await waitFor(() => {
        expect(screen.getByText('v1.0.0')).toBeInTheDocument();
      });
    });
  });
});
