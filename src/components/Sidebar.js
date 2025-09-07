import React from 'react';
import { Card, List, Avatar, Button, Typography, Space, Tag, Divider, Empty } from 'antd';
import { 
  DatabaseOutlined, 
  FileExcelOutlined, 
  BarChartOutlined, 
  BulbOutlined, 
  PushpinOutlined,
  DeleteOutlined,
  EyeOutlined,
  CalendarOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

const Sidebar = ({ 
  currentSession, 
  pinnedInsights, 
  onUnpinInsight, 
  onSessionSelected,
  sessions = [],
  visualizations = []
}) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getSessionIcon = (type) => {
    switch (type) {
      case 'database':
        return <DatabaseOutlined style={{ color: '#00d4aa' }} />;
      case 'file':
        return <FileExcelOutlined style={{ color: '#00d4aa' }} />;
      default:
        return <BarChartOutlined style={{ color: '#00d4aa' }} />;
    }
  };

  const getInsightTypeIcon = (type) => {
    switch (type) {
      case 'chart':
        return <BarChartOutlined style={{ color: '#00d4aa' }} />;
      case 'insight':
        return <BulbOutlined style={{ color: '#f39c12' }} />;
      default:
        return <BulbOutlined style={{ color: '#00d4aa' }} />;
    }
  };

  return (
    <div className="sidebar-content">
      {/* Current Session Info */}
      <Card 
        title="Current Session" 
        size="small" 
        className="sidebar-card"
        extra={
          currentSession && (
            <Tag color="green">Active</Tag>
          )
        }
      >
        {currentSession ? (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space>
              {getSessionIcon(currentSession.type)}
              <Text strong>{currentSession.name}</Text>
            </Space>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {currentSession.rows} rows • {currentSession.columns} columns
            </Text>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              <CalendarOutlined /> {formatDate(currentSession.created_at)}
            </Text>
          </Space>
        ) : (
          <Empty 
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="No active session"
            style={{ margin: '16px 0' }}
          />
        )}
      </Card>

      <Divider style={{ margin: '16px 0' }} />

      {/* Quick Stats */}
      <Card title="Quick Stats" size="small" className="sidebar-card">
        <Space direction="vertical" style={{ width: '100%' }}>
          <div className="stat-item">
            <Text style={{ color: '#8c8c8c' }}>Total Sessions</Text>
            <Text strong style={{ color: '#ffffff' }}>{sessions.length}</Text>
          </div>
          <div className="stat-item">
            <Text style={{ color: '#8c8c8c' }}>Charts Created</Text>
            <Text strong style={{ color: '#ffffff' }}>{visualizations.length}</Text>
          </div>
          <div className="stat-item">
            <Text style={{ color: '#8c8c8c' }}>Data Sources</Text>
            <Text strong style={{ color: '#ffffff' }}>{sessions.filter(s => s.type === 'file').length}</Text>
          </div>
        </Space>
      </Card>

      <Divider style={{ margin: '16px 0' }} />

      {/* Pinned Insights */}
      <Card 
        title={
          <Space>
              <PushpinOutlined style={{ color: '#f39c12' }} />
            <span>Pinned Insights</span>
            <Tag color="orange">{pinnedInsights.length}</Tag>
          </Space>
        } 
        size="small" 
        className="sidebar-card"
      >
        {pinnedInsights.length > 0 ? (
          <List
            size="small"
            dataSource={pinnedInsights}
            renderItem={(insight) => (
              <List.Item
                actions={[
                  <Button 
                    type="text" 
                    size="small" 
                    icon={<EyeOutlined />}
                    onClick={() => {/* View insight */}}
                  />,
                  <Button 
                    type="text" 
                    size="small" 
                    icon={<DeleteOutlined />}
                    onClick={() => onUnpinInsight(insight.id)}
                  />
                ]}
                className="insight-item"
              >
                <List.Item.Meta
                  avatar={
                    <Avatar 
                      size="small" 
                      icon={getInsightTypeIcon(insight.type)}
                    />
                  }
                  title={
                    <Text ellipsis style={{ fontSize: '12px' }}>
                      {insight.title}
                    </Text>
                  }
                  description={
                    <Text type="secondary" style={{ fontSize: '11px' }}>
                      {insight.description}
                    </Text>
                  }
                />
              </List.Item>
            )}
          />
        ) : (
          <Empty 
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="No pinned insights"
            style={{ margin: '16px 0' }}
          />
        )}
      </Card>

      <Divider style={{ margin: '16px 0' }} />

      {/* Recent Activity */}
      <Card title="Recent Activity" size="small" className="sidebar-card">
        <List
          size="small"
          dataSource={[
            ...sessions.slice(0, 2).map(session => ({
              action: `Connected ${session.type} source`,
              time: formatDate(session.created_at),
              type: session.type
            })),
            ...visualizations.slice(0, 2).map(viz => ({
              action: `Created ${viz.type || 'chart'}`,
              time: formatDate(viz.timestamp),
              type: 'chart'
            }))
          ].slice(0, 4)}
          renderItem={(item) => (
            <List.Item className="activity-item">
              <List.Item.Meta
                avatar={
                  <Avatar 
                    size="small" 
                    icon={getInsightTypeIcon(item.type)}
                  />
                }
                title={
                  <Text style={{ fontSize: '12px', color: '#ffffff' }}>
                    {item.action}
                  </Text>
                }
                description={
                  <Text style={{ fontSize: '11px', color: '#8c8c8c' }}>
                    {item.time}
                  </Text>
                }
              />
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default Sidebar;
