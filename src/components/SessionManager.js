import React, { useState, useEffect } from 'react';
import { Card, List, Typography, Space, Button, Tag, message, Empty, Modal } from 'antd';
import { DatabaseOutlined, FileExcelOutlined, DeleteOutlined, EyeOutlined, ClockCircleOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const SessionManager = ({ sessions, onSessionSelected, onSessionsUpdated }) => {
  const [loading, setLoading] = useState(false);

  const handleSessionClick = (session) => {
    onSessionSelected(session);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch (error) {
      return 'Invalid Date';
    }
  };

  const getDataSourceIcon = (type) => {
    return type === 'database' ? <DatabaseOutlined /> : <FileExcelOutlined />;
  };

  const getDataSourceColor = (type) => {
    if (!type) return 'default';
    return type === 'database' ? 'blue' : 'green';
  };

  const renderSessionItem = (session) => (
    <List.Item
      style={{
        background: 'rgba(45, 45, 45, 0.5)',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '12px',
        border: '1px solid #404040',
        transition: 'all 0.3s ease'
      }}
      actions={[
        <Button
          key="view"
          type="primary"
          icon={<EyeOutlined />}
          onClick={() => handleSessionClick(session)}
          style={{
            background: 'linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%)',
            border: 'none',
            borderRadius: '8px',
            fontWeight: '500'
          }}
        >
          Open
        </Button>
      ]}
    >
      <List.Item.Meta
        avatar={
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '50%',
            background: getDataSourceColor(session.data_source_type) === 'blue' 
              ? 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)'
              : 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
            fontSize: '20px'
          }}>
            {getDataSourceIcon(session.data_source_type)}
          </div>
        }
        title={
          <div style={{ marginBottom: '8px' }}>
            <Space>
              <Text strong style={{ color: '#ffffff', fontSize: '16px' }}>
                {session.data_source_type ? session.data_source_type.toUpperCase() : 'UNKNOWN'}
              </Text>
              <Tag 
                color={getDataSourceColor(session.data_source_type)}
                style={{
                  background: getDataSourceColor(session.data_source_type) === 'blue' 
                    ? 'rgba(24, 144, 255, 0.2)'
                    : 'rgba(82, 196, 26, 0.2)',
                  border: getDataSourceColor(session.data_source_type) === 'blue' 
                    ? '1px solid rgba(24, 144, 255, 0.3)'
                    : '1px solid rgba(82, 196, 26, 0.3)',
                  color: getDataSourceColor(session.data_source_type) === 'blue' 
                    ? '#1890ff'
                    : '#52c41a',
                  borderRadius: '8px',
                  fontWeight: '500'
                }}
              >
                {session.data_source_type || 'unknown'}
              </Tag>
            </Space>
          </div>
        }
        description={
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <div style={{
              background: 'rgba(0, 0, 0, 0.2)',
              borderRadius: '8px',
              padding: '8px 12px',
              border: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
              <Text style={{ color: '#8c8c8c', fontSize: '12px', fontFamily: 'monospace' }}>
                ID: {session.id ? `${session.id.slice(0, 8)}...${session.id.slice(-4)}` : 'No ID'}
              </Text>
            </div>
            <Space>
              <ClockCircleOutlined style={{ color: '#8c8c8c' }} />
              <Text style={{ color: '#8c8c8c', fontSize: '12px' }}>
                Created: {session.created_at ? formatDate(session.created_at) : 'Unknown'}
              </Text>
            </Space>
            <Space>
              <ClockCircleOutlined style={{ color: '#8c8c8c' }} />
              <Text style={{ color: '#8c8c8c', fontSize: '12px' }}>
                Last activity: {session.last_activity ? formatDate(session.last_activity) : 'Unknown'}
              </Text>
            </Space>
          </Space>
        }
      />
    </List.Item>
  );

  return (
    <div style={{
      background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
      borderRadius: '20px',
      padding: '32px',
      border: '1px solid #404040',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
      minHeight: '500px'
    }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Header */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          paddingBottom: '20px',
          borderBottom: '1px solid #404040'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(0, 212, 170, 0.3)'
            }}>
              <DatabaseOutlined style={{ color: '#ffffff', fontSize: '24px' }} />
            </div>
            <div>
              <div style={{ 
                color: '#ffffff', 
                fontSize: '20px', 
                fontWeight: '600',
                margin: 0
              }}>
                Data Sessions
              </div>
              <div style={{ 
                color: '#8c8c8c', 
                fontSize: '14px',
                margin: 0
              }}>
                Manage your connected data sources and sessions
              </div>
            </div>
          </div>
          <Button 
            onClick={onSessionsUpdated} 
            loading={loading}
            style={{
              background: 'rgba(0, 212, 170, 0.1)',
              border: '1px solid rgba(0, 212, 170, 0.3)',
              color: '#00d4aa',
              borderRadius: '8px',
              fontWeight: '500'
            }}
          >
            Refresh
          </Button>
        </div>

        {/* Sessions List */}
        {sessions.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '60px 20px',
            background: 'rgba(45, 45, 45, 0.3)',
            borderRadius: '16px',
            border: '1px solid #404040'
          }}>
            <div style={{ fontSize: '64px', marginBottom: '24px', opacity: 0.5 }}>📁</div>
            <div style={{ 
              color: '#ffffff', 
              fontSize: '18px', 
              fontWeight: '500',
              marginBottom: '12px'
            }}>
              No Sessions Found
            </div>
            <div style={{ 
              color: '#8c8c8c', 
              fontSize: '14px',
              marginBottom: '24px'
            }}>
              Upload a file or connect to a database to create your first session
            </div>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              background: 'rgba(0, 212, 170, 0.1)',
              padding: '12px 24px',
              borderRadius: '12px',
              border: '1px solid rgba(0, 212, 170, 0.3)',
              color: '#00d4aa',
              fontSize: '14px',
              fontWeight: '500'
            }}>
              <DatabaseOutlined />
              Start by uploading data
            </div>
          </div>
        ) : (
          <div style={{
            background: 'rgba(45, 45, 45, 0.3)',
            borderRadius: '16px',
            padding: '20px',
            border: '1px solid #404040'
          }}>
            <List
              dataSource={sessions}
              renderItem={renderSessionItem}
              loading={loading}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} sessions`,
                style: {
                  color: '#ffffff'
                }
              }}
              style={{
                '& .ant-list-item': {
                  borderBottom: '1px solid #404040'
                }
              }}
            />
          </div>
        )}

        {/* Info Section */}
        <div style={{
          background: 'rgba(45, 45, 45, 0.3)',
          borderRadius: '16px',
          padding: '24px',
          border: '1px solid #404040'
        }}>
          <div style={{ 
            color: '#ffffff', 
            fontSize: '16px', 
            fontWeight: '600',
            marginBottom: '16px',
            textAlign: 'center'
          }}>
            Session Management
          </div>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
            gap: '16px' 
          }}>
            <div style={{
              background: 'rgba(0, 212, 170, 0.1)',
              border: '1px solid rgba(0, 212, 170, 0.3)',
              borderRadius: '12px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>🔗</div>
              <div style={{ color: '#00d4aa', fontSize: '14px', fontWeight: '500' }}>
                Unique Sessions
              </div>
              <div style={{ color: '#8c8c8c', fontSize: '12px', marginTop: '4px' }}>
                Each data source creates a unique session
              </div>
            </div>
            
            <div style={{
              background: 'rgba(0, 212, 170, 0.1)',
              border: '1px solid rgba(0, 212, 170, 0.3)',
              borderRadius: '12px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>💾</div>
              <div style={{ color: '#00d4aa', fontSize: '14px', fontWeight: '500' }}>
                Data Storage
              </div>
              <div style={{ color: '#8c8c8c', fontSize: '12px', marginTop: '4px' }}>
                Sessions store schema and query history
              </div>
            </div>
            
            <div style={{
              background: 'rgba(0, 212, 170, 0.1)',
              border: '1px solid rgba(0, 212, 170, 0.3)',
              borderRadius: '12px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>▶️</div>
              <div style={{ color: '#00d4aa', fontSize: '14px', fontWeight: '500' }}>
                Easy Access
              </div>
              <div style={{ color: '#8c8c8c', fontSize: '12px', marginTop: '4px' }}>
                Click "Open" to continue working
              </div>
            </div>
          </div>
        </div>
      </Space>
    </div>
  );
};

export default SessionManager;
