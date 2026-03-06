<!-- ARCHIVED: 已合并到 design-overview.md -->

<!-- ARCHIVED: 已压缩至 check-history-summary.md -->

# qclaw WebUI 技术方案设计

**任务 ID:** DESIGN-002  
**设计师:** qclaw-designer  
**完成日期:** 2026-03-05  
**版本:** v1.0

---

## 🏗️ 技术架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端展示层                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    React 18 + TypeScript                 │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │    │
│  │  │大盘指标  │ │量化指标  │ │AI 建议    │ │新闻资讯  │   │    │
│  │  │Component │ │Component │ │Component │ │Component │   │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         状态管理层                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Zustand (轻量级状态管理)                     │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │    │
│  │  │ marketStore │ │indicatorStore│ │ aiStore     │      │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API 服务层                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Axios + React Query (数据请求)               │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │    │
│  │  │ market API  │ │ indicator API│ │ ai API      │      │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         后端服务层                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              FastAPI (Python)                            │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │    │
│  │  │ qlib 数据   │ │ 指标计算    │ │ AI 推理      │      │    │
│  │  │ 服务        │ │ 引擎        │ │ 服务        │      │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 技术栈选型

### 前端技术栈

| 类别 | 技术 | 版本 | 选型理由 |
|------|------|------|----------|
| 框架 | React | 18.x | 生态成熟、组件丰富、性能优秀 |
| 语言 | TypeScript | 5.x | 类型安全、IDE 支持好、减少运行时错误 |
| 构建工具 | Vite | 5.x | 极速启动、热更新、打包优化 |
| 状态管理 | Zustand | 4.x | 轻量、API 简洁、无需 Provider 嵌套 |
| 数据请求 | React Query | 5.x | 缓存、重试、乐观更新、devtools |
| HTTP 客户端 | Axios | 1.x | 拦截器、取消请求、类型支持 |
| UI 组件库 | Ant Design | 5.x | 金融类常用、组件齐全、主题定制 |
| 图表库 | ECharts | 5.x | 功能强大、K 线图支持好、中文文档 |
| 样式方案 | Tailwind CSS | 3.x | 原子化 CSS、开发效率高、易维护 |
| 路由 | React Router | 6.x | 标准方案、嵌套路由、懒加载 |

### 后端技术栈

| 类别 | 技术 | 版本 | 选型理由 |
|------|------|------|----------|
| 框架 | FastAPI | 0.100+ | 高性能、自动文档、类型推导 |
| 量化引擎 | qlib | 最新 | 微软开源、A 股支持好、算法丰富 |
| 数据处理 | pandas | 2.x | 数据分析标准库 |
| AI 推理 | ONNX Runtime | 1.x | 跨平台、高性能推理 |
| 缓存 | Redis | 7.x | 高频数据缓存、会话存储 |
| 数据库 | PostgreSQL | 15.x | 时序数据支持、JSONB 灵活查询 |

---

## 📁 项目结构

```
qclaw-webui/
├── public/                      # 静态资源
│   ├── favicon.ico
│   └── logo.svg
├── src/
│   ├── assets/                  # 资源文件
│   │   ├── images/
│   │   └── styles/
│   ├── components/              # 通用组件
│   │   ├── common/
│   │   │   ├── Card.tsx
│   │   │   ├── Button.tsx
│   │   │   ├── Table.tsx
│   │   │   └── Loading.tsx
│   │   ├── chart/
│   │   │   ├── KLineChart.tsx
│   │   │   ├── LineChart.tsx
│   │   │   └── BarChart.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       └── ResponsiveGrid.tsx
│   ├── pages/                   # 页面组件
│   │   ├── Dashboard.tsx        # 首页大盘
│   │   ├── Indicators.tsx       # 指标详情
│   │   ├── AIAdvice.tsx         # AI 建议
│   │   └── News.tsx             # 新闻资讯
│   ├── modules/                 # 业务模块
│   │   ├── market/              # 大盘指标模块
│   │   │   ├── MarketOverview.tsx
│   │   │   ├── MarketChart.tsx
│   │   │   └── MarketStats.tsx
│   │   ├── indicators/          # 量化指标模块
│   │   │   ├── IndicatorPanel.tsx
│   │   │   ├── TrendIndicators.tsx
│   │   │   ├── MomentumIndicators.tsx
│   │   │   └── VolumeIndicators.tsx
│   │   ├── ai/                  # AI 建议模块
│   │   │   ├── AIRecommendation.tsx
│   │   │   ├── StockList.tsx
│   │   │   └── RiskWarning.tsx
│   │   └── news/                # 新闻资讯模块
│   │       ├── NewsFeed.tsx
│   │       ├── NewsItem.tsx
│   │       └── NewsFilter.tsx
│   ├── stores/                  # 状态管理
│   │   ├── marketStore.ts
│   │   ├── indicatorStore.ts
│   │   ├── aiStore.ts
│   │   └── newsStore.ts
│   ├── services/                # API 服务
│   │   ├── api.ts               # Axios 实例配置
│   │   ├── marketApi.ts
│   │   ├── indicatorApi.ts
│   │   ├── aiApi.ts
│   │   └── newsApi.ts
│   ├── hooks/                   # 自定义 Hooks
│   │   ├── useMarketData.ts
│   │   ├── useIndicatorData.ts
│   │   └── useAIAdvice.ts
│   ├── types/                   # TypeScript 类型定义
│   │   ├── market.ts
│   │   ├── indicator.ts
│   │   ├── ai.ts
│   │   └── common.ts
│   ├── utils/                   # 工具函数
│   │   ├── format.ts            # 数据格式化
│   │   ├── request.ts           # 请求封装
│   │   └── storage.ts           # 本地存储
│   ├── config/                  # 配置文件
│   │   ├── env.ts
│   │   └── constants.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── tests/                       # 测试文件
│   ├── components/
│   ├── pages/
│   └── utils/
├── .env.example
├── .eslintrc.cjs
├── .prettierrc
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

---

## 🔌 API 接口定义

### 基础配置

```typescript
// src/services/api.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 统一错误处理
    if (error.response?.status === 401) {
      // 跳转登录
    }
    return Promise.reject(error);
  }
);
```

### 大盘指标 API

```typescript
// src/services/marketApi.ts
import { apiClient } from './api';
import type { MarketIndex, MarketStats } from '@/types/market';

export const marketApi = {
  // 获取主要指数
  getIndices: () => 
    apiClient.get<MarketIndex[]>('/api/v1/market/indices'),
  
  // 获取指数 K 线数据
  getKlineData: (indexCode: string, period: 'day' | 'week' | 'month') =>
    apiClient.get(`/api/v1/market/kline/${indexCode}`, { params: { period } }),
  
  // 获取市场统计
  getMarketStats: () =>
    apiClient.get<MarketStats>('/api/v1/market/stats'),
  
  // 获取实时行情
  getRealTimeQuote: (symbol: string) =>
    apiClient.get(`/api/v1/market/quote/${symbol}`),
};
```

### 量化指标 API

```typescript
// src/services/indicatorApi.ts
import { apiClient } from './api';
import type { IndicatorData } from '@/types/indicator';

export const indicatorApi = {
  // 获取指标列表
  getIndicators: (category?: 'trend' | 'momentum' | 'volume') =>
    apiClient.get('/api/v1/indicators', { params: { category } }),
  
  // 计算指标值
  calculateIndicator: (symbol: string, indicator: string, params: Record<string, any>) =>
    apiClient.post<IndicatorData>('/api/v1/indicators/calculate', {
      symbol,
      indicator,
      params,
    }),
  
  // 获取指标历史
  getIndicatorHistory: (symbol: string, indicator: string, days: number) =>
    apiClient.get(`/api/v1/indicators/history/${symbol}/${indicator}`, {
      params: { days },
    }),
};
```

### AI 建议 API

```typescript
// src/services/aiApi.ts
import { apiClient } from './api';
import type { AIAdvice, StockRecommendation } from '@/types/ai';

export const aiApi = {
  // 获取 AI 投资建议
  getAdvice: () =>
    apiClient.get<AIAdvice>('/api/v1/ai/advice'),
  
  // 获取推荐股票列表
  getRecommendations: () =>
    apiClient.get<StockRecommendation[]>('/api/v1/ai/recommendations'),
  
  // 获取详细分析
  getAnalysis: (symbol: string) =>
    apiClient.get(`/api/v1/ai/analysis/${symbol}`),
  
  // 策略回测
  backtest: (strategy: string, params: Record<string, any>) =>
    apiClient.post('/api/v1/ai/backtest', { strategy, params }),
};
```

### 新闻资讯 API

```typescript
// src/services/newsApi.ts
import { apiClient } from './api';
import type { NewsItem } from '@/types/news';

export const newsApi = {
  // 获取新闻列表
  getNews: (options?: {
    category?: 'important' | 'market' | 'industry' | 'company';
    source?: string;
    limit?: number;
  }) =>
    apiClient.get<NewsItem[]>('/api/v1/news', { params: options }),
  
  // 获取新闻详情
  getNewsDetail: (id: string) =>
    apiClient.get(`/api/v1/news/${id}`),
};
```

---

## 📦 类型定义

### 大盘指标类型

```typescript
// src/types/market.ts
export interface MarketIndex {
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  turnover: number;
  high: number;
  low: number;
  open: number;
  prevClose: number;
  updateTime: string;
}

export interface MarketStats {
  totalVolume: number;        // 总成交量 (亿)
  advanceDeclineRatio: number; // 涨跌比
  limitUp: number;            // 涨停家数
  limitDown: number;          // 跌停家数
  northboundFlow: number;     // 北向资金 (亿)
}

export interface KlineData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}
```

### 量化指标类型

```typescript
// src/types/indicator.ts
export type IndicatorCategory = 'trend' | 'momentum' | 'volume';

export interface Indicator {
  id: string;
  name: string;
  category: IndicatorCategory;
  description: string;
  formula?: string;
  params: IndicatorParam[];
}

export interface IndicatorParam {
  name: string;
  type: 'number' | 'select';
  defaultValue: number | string;
  options?: string[];
  min?: number;
  max?: number;
}

export interface IndicatorData {
  indicator: string;
  value: number;
  signal: 'buy' | 'sell' | 'hold' | 'warning';
  timestamp: string;
}
```

### AI 建议类型

```typescript
// src/types/ai.ts
export type ConfidenceLevel = 'high' | 'medium' | 'low';

export interface AIAdvice {
  summary: string;
  confidence: ConfidenceLevel;
  confidenceScore: number;
  marketView: 'bullish' | 'bearish' | 'neutral';
  suggestedPosition: number;  // 建议仓位 (0-100%)
  resistanceLevel?: number;
  supportLevel?: number;
  risks: string[];
  updateTime: string;
}

export interface StockRecommendation {
  code: string;
  name: string;
  action: 'buy' | 'add' | 'hold' | 'sell';
  targetPrice: number;
  currentPrice: number;
  upside: number;
  reason: string;
}
```

---

## 🔄 数据流设计

### 状态管理 (Zustand)

```typescript
// src/stores/marketStore.ts
import { create } from 'zustand';
import { marketApi } from '@/services/marketApi';
import type { MarketIndex, MarketStats, KlineData } from '@/types/market';

interface MarketState {
  indices: MarketIndex[];
  stats: MarketStats | null;
  klineData: Record<string, KlineData[]>;
  loading: boolean;
  error: string | null;
  lastUpdate: string | null;
  
  // Actions
  fetchIndices: () => Promise<void>;
  fetchStats: () => Promise<void>;
  fetchKlineData: (indexCode: string, period: string) => Promise<void>;
  refreshAll: () => Promise<void>;
}

export const useMarketStore = create<MarketState>((set, get) => ({
  indices: [],
  stats: null,
  klineData: {},
  loading: false,
  error: null,
  lastUpdate: null,

  fetchIndices: async () => {
    set({ loading: true });
    try {
      const indices = await marketApi.getIndices();
      set({ indices, lastUpdate: new Date().toISOString(), loading: false });
    } catch (error) {
      set({ error: '获取指数数据失败', loading: false });
    }
  },

  fetchStats: async () => {
    try {
      const stats = await marketApi.getMarketStats();
      set({ stats });
    } catch (error) {
      console.error('获取市场统计失败', error);
    }
  },

  fetchKlineData: async (indexCode, period) => {
    try {
      const klineData = await marketApi.getKlineData(indexCode, period);
      set((state) => ({
        klineData: { ...state.klineData, [indexCode]: klineData },
      }));
    } catch (error) {
      console.error('获取 K 线数据失败', error);
    }
  },

  refreshAll: async () => {
    await Promise.all([
      get().fetchIndices(),
      get().fetchStats(),
    ]);
  },
}));
```

### 数据请求 (React Query)

```typescript
// src/hooks/useMarketData.ts
import { useQuery } from '@tanstack/react-query';
import { marketApi } from '@/services/marketApi';

export function useMarketIndices() {
  return useQuery({
    queryKey: ['market', 'indices'],
    queryFn: marketApi.getIndices,
    refetchInterval: 30000, // 30 秒自动刷新
    staleTime: 10000,       // 10 秒内认为数据新鲜
  });
}

export function useKlineData(indexCode: string, period: string) {
  return useQuery({
    queryKey: ['market', 'kline', indexCode, period],
    queryFn: () => marketApi.getKlineData(indexCode, period as any),
    enabled: !!indexCode,
  });
}
```

---

## 🎨 主题配置

### Tailwind 配置

```javascript
// tailwind.config.js
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1E3A8A',
          light: '#3B82F6',
          dark: '#1E3A8A',
        },
        market: {
          up: '#DC2626',    // 涨 - 红色
          down: '#16A34A',  // 跌 - 绿色
        },
        neutral: {
          bg: '#F3F4F6',
          card: '#FFFFFF',
          text: '#1F2937',
          textMuted: '#6B7280',
        },
      },
    },
  },
  plugins: [],
};
```

### Ant Design 主题覆盖

```less
// src/assets/styles/antd-overrides.less
@primary-color: #1E3A8A;
@border-radius-base: 8px;
@font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

// 卡片样式
.ant-card {
  border-radius: @border-radius-base;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

// 表格样式
.ant-table-thead > tr > th {
  background: #F9FAFB;
  font-weight: 600;
}
```

---

## 🚀 性能优化

### 代码分割

```typescript
// src/App.tsx
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('@/pages/Dashboard'));
const Indicators = lazy(() => import('@/pages/Indicators'));
const AIAdvice = lazy(() => import('@/pages/AIAdvice'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/indicators" element={<Indicators />} />
        <Route path="/ai" element={<AIAdvice />} />
      </Routes>
    </Suspense>
  );
}
```

### 图表懒加载

```typescript
// 使用 ECharts 按需加载
import { useRegister } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, CandlestickChart } from 'echarts/charts';
import { GridComponent, TooltipComponent } from 'echarts/components';

useRegister([
  CanvasRenderer,
  LineChart,
  CandlestickChart,
  GridComponent,
  TooltipComponent,
]);
```

### 数据缓存策略

```typescript
// React Query 配置
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 10000,      // 10 秒新鲜时间
      cacheTime: 300000,     // 5 分钟缓存
      refetchOnWindowFocus: false,
      retry: 2,
    },
  },
});
```

---

## 🧪 测试策略

### 单元测试

```typescript
// tests/utils/format.test.ts
import { describe, it, expect } from 'vitest';
import { formatNumber, formatPercent } from '@/utils/format';

describe('format utilities', () => {
  it('formats large numbers correctly', () => {
    expect(formatNumber(1234567890)).toBe('12.35 亿');
  });

  it('formats percent with color', () => {
    expect(formatPercent(1.23)).toBe('+1.23%');
    expect(formatPercent(-0.45)).toBe('-0.45%');
  });
});
```

### 组件测试

```typescript
// tests/components/MarketCard.test.tsx
import { render, screen } from '@testing-library/react';
import { MarketCard } from '@/components/market/MarketCard';

describe('MarketCard', () => {
  it('renders index data correctly', () => {
    render(<MarketCard index={mockIndexData} />);
    expect(screen.getByText('上证指数')).toBeInTheDocument();
    expect(screen.getByText('3,245.67')).toBeInTheDocument();
  });
});
```

---

## 📋 验收标准

- ✅ 技术栈符合 PRD 要求 (React + TypeScript + FastAPI + qlib)
- ✅ 架构可扩展 (模块化设计、清晰分层)
- ✅ API 定义清晰 (RESTful 风格、类型完整)
- ✅ 性能优化考虑 (代码分割、缓存策略)
- ✅ 测试策略完善 (单元测试 + 组件测试)

---

*技术方案版本：v1.0 | 下次更新：根据开发反馈迭代*
