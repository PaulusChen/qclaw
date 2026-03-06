// 训练日志组件
import React, { useEffect, useRef } from 'react';
import { Typography, Space } from 'antd';
import {
  InfoCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';

const { Text } = Typography;

interface LogEntry {
  timestamp: string;
  message: string;
  level?: 'info' | 'warning' | 'error' | 'success';
}

interface TrainingLogsProps {
  logs: LogEntry[];
  maxLines?: number;
}

const TrainingLogs: React.FC<TrainingLogsProps> = ({ logs, maxLines = 100 }) => {
  const logsEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // 自动滚动到最新日志
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const getIcon = (level: string = 'info') => {
    switch (level) {
      case 'error':
        return <CloseCircleOutlined style={{ color: '#f5222d' }} />;
      case 'warning':
        return <WarningOutlined style={{ color: '#faad14' }} />;
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      default:
        return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
    }
  };

  const getColor = (level: string = 'info') => {
    switch (level) {
      case 'error':
        return '#f5222d';
      case 'warning':
        return '#faad14';
      case 'success':
        return '#52c41a';
      default:
        return '#333';
    }
  };

  // 自动检测日志级别
  const detectLogLevel = (message: string): 'info' | 'warning' | 'error' | 'success' => {
    const lowerMessage = message.toLowerCase();
    if (lowerMessage.includes('error') || lowerMessage.includes('failed') || lowerMessage.includes('exception')) {
      return 'error';
    }
    if (lowerMessage.includes('warning') || lowerMessage.includes('warn')) {
      return 'warning';
    }
    if (lowerMessage.includes('success') || lowerMessage.includes('completed') || lowerMessage.includes('saved') || lowerMessage.includes('✨')) {
      return 'success';
    }
    return 'info';
  };

  const displayLogs = logs.slice(-maxLines);

  return (
    <div
      ref={containerRef}
      style={{
        height: '300px',
        overflowY: 'auto',
        background: '#1e1e1e',
        borderRadius: 4,
        padding: 12,
        fontFamily: 'Monaco, Menlo, Courier New, monospace',
        fontSize: '12px',
      }}
    >
      {displayLogs.length === 0 ? (
        <div style={{ textAlign: 'center', color: '#666', padding: '40px 0' }}>
          暂无日志
        </div>
      ) : (
        <div>
          {displayLogs.map((log, index) => {
            const level = log.level || detectLogLevel(log.message);
            return (
              <div
                key={index}
                style={{
                  marginBottom: 4,
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 8,
                }}
              >
                <span style={{ color: '#666', flexShrink: 0 }}>[{log.timestamp}]</span>
                <span style={{ flexShrink: 0 }}>{getIcon(level)}</span>
                <Text
                  style={{
                    color: getColor(level),
                    wordBreak: 'break-all',
                    lineHeight: 1.5,
                  }}
                >
                  {log.message}
                </Text>
              </div>
            );
          })}
          <div ref={logsEndRef} />
        </div>
      )}
    </div>
  );
};

export default TrainingLogs;
