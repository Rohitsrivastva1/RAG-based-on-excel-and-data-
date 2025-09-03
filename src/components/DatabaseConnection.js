import React, { useState } from 'react';
  import { Form, Input, Button, Select, Card, Typography, Space, message, Row, Col, Divider, Tooltip } from 'antd';
import { DatabaseOutlined, LinkOutlined, InfoCircleOutlined, CheckCircleOutlined, SecurityScanOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;
const { Option } = Select;

const DatabaseConnection = ({ onSessionCreated }) => {
  const [form] = Form.useForm();
  const [connecting, setConnecting] = useState(false);

  const onFinish = async (values) => {
    setConnecting(true);
    
    try {
      const response = await fetch('/connect_db', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Create session object
      const sessionData = {
        id: result.session_id,
        data_source_type: 'database',
        data_source_info: {
          host: values.host,
          port: values.port,
          database: values.database,
          username: values.username,
          db_type: values.db_type,
          connected_at: new Date().toISOString()
        },
        schema_info: result.schema,
        created_at: new Date().toISOString()
      };

      onSessionCreated(sessionData);
      message.success('Database connected successfully!');
      form.resetFields();
      
    } catch (error) {
      console.error('Connection error:', error);
      message.error('Connection failed: ' + error.message);
    } finally {
      setConnecting(false);
    }
  };

  return (
    <div style={{
      background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
      borderRadius: '20px',
      padding: '32px',
      border: '1px solid #404040',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
      minHeight: '600px'
    }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '16px',
            background: 'rgba(0, 212, 170, 0.1)',
            padding: '16px 32px',
            borderRadius: '20px',
            border: '1px solid rgba(0, 212, 170, 0.3)',
            marginBottom: '16px'
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
                fontSize: '24px', 
                fontWeight: '600',
                margin: 0
              }}>
                Connect to Database
              </div>
              <div style={{ 
                color: '#8c8c8c', 
                fontSize: '14px',
                margin: 0
              }}>
                Connect to your database to start asking questions and generating insights
              </div>
            </div>
          </div>
        </div>

        {/* Connection Form */}
        <div style={{
          background: 'rgba(45, 45, 45, 0.5)',
          borderRadius: '20px',
          padding: '32px',
          border: '1px solid #404040',
          backdropFilter: 'blur(10px)'
        }}>
          <Form
            form={form}
            layout="vertical"
            onFinish={onFinish}
            className="connection-form"
            style={{ maxWidth: '700px', margin: '0 auto' }}
          >
            {/* Database Type & Port Row */}
            <Row gutter={24}>
              <Col span={12}>
                <Form.Item
                  label={
                    <span style={{ color: '#ffffff', fontWeight: '500' }}>
                      Database Type <span style={{ color: '#ff4d4f' }}>*</span>
                    </span>
                  }
                  name="db_type"
                  rules={[{ required: true, message: 'Please select database type!' }]}
                >
                  <Select 
                    placeholder="Select database type"
                    size="large"
                    style={{
                      background: 'rgba(26, 26, 26, 0.8)',
                      border: '1px solid #404040',
                      borderRadius: '12px'
                    }}
                  >
                    <Option value="postgresql">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ 
                          width: '8px', 
                          height: '8px', 
                          borderRadius: '50%', 
                          background: '#336791' 
                        }} />
                        PostgreSQL
                      </div>
                    </Option>
                    <Option value="mysql">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ 
                          width: '8px', 
                          height: '8px', 
                          borderRadius: '50%', 
                          background: '#00758f' 
                        }} />
                        MySQL
                      </div>
                    </Option>
                    <Option value="sqlite">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ 
                          width: '8px', 
                          height: '8px', 
                          borderRadius: '50%', 
                          background: '#003b57' 
                        }} />
                        SQLite
                      </div>
                    </Option>
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label={
                    <span style={{ color: '#ffffff', fontWeight: '500' }}>
                      Port <span style={{ color: '#ff4d4f' }}>*</span>
                    </span>
                  }
                  name="port"
                  rules={[{ required: true, message: 'Please input port!' }]}
                  initialValue={5432}
                >
                  <Input 
                    type="number" 
                    placeholder="Port" 
                    size="large"
                    style={{
                      background: 'rgba(26, 26, 26, 0.8)',
                      border: '1px solid #404040',
                      borderRadius: '12px',
                      color: '#ffffff'
                    }}
                  />
                </Form.Item>
              </Col>
            </Row>

            {/* Host */}
            <Form.Item
              label={
                <span style={{ color: '#ffffff', fontWeight: '500' }}>
                  Host <span style={{ color: '#ff4d4f' }}>*</span>
                </span>
              }
              name="host"
              rules={[{ required: true, message: 'Please input host!' }]}
            >
              <Input 
                placeholder="localhost" 
                size="large"
                style={{
                  background: 'rgba(26, 26, 26, 0.8)',
                  border: '1px solid #404040',
                  borderRadius: '12px',
                  color: '#ffffff'
                }}
              />
            </Form.Item>

            {/* Database Name */}
            <Form.Item
              label={
                <span style={{ color: '#ffffff', fontWeight: '500' }}>
                  Database Name <span style={{ color: '#ff4d4f' }}>*</span>
                </span>
              }
              name="database"
              rules={[{ required: true, message: 'Please input database name!' }]}
            >
              <Input 
                placeholder="Database name" 
                size="large"
                style={{
                  background: 'rgba(26, 26, 26, 0.8)',
                  border: '1px solid #404040',
                  borderRadius: '12px',
                  color: '#ffffff'
                }}
              />
            </Form.Item>

            {/* Username & Password Row */}
            <Row gutter={24}>
              <Col span={12}>
                <Form.Item
                  label={
                    <span style={{ color: '#ffffff', fontWeight: '500' }}>
                      Username <span style={{ color: '#ff4d4f' }}>*</span>
                    </span>
                  }
                  name="username"
                  rules={[{ required: true, message: 'Please input username!' }]}
                >
                  <Input 
                    placeholder="Username" 
                    size="large"
                    style={{
                      background: 'rgba(26, 26, 26, 0.8)',
                      border: '1px solid #404040',
                      borderRadius: '12px',
                      color: '#ffffff'
                    }}
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label={
                    <span style={{ color: '#ffffff', fontWeight: '500' }}>
                      Password <span style={{ color: '#ff4d4f' }}>*</span>
                    </span>
                  }
                  name="password"
                  rules={[{ required: true, message: 'Please input password!' }]}
                >
                  <Input.Password 
                    placeholder="Password" 
                    size="large"
                    style={{
                      background: 'rgba(26, 26, 26, 0.8)',
                      border: '1px solid #404040',
                      borderRadius: '12px',
                      color: '#ffffff'
                    }}
                  />
                </Form.Item>
              </Col>
            </Row>

            {/* Connect Button */}
            <Form.Item style={{ textAlign: 'center', marginTop: '32px' }}>
              <Button
                type="primary"
                htmlType="submit"
                loading={connecting}
                icon={<LinkOutlined />}
                size="large"
                style={{
                  height: '56px',
                  padding: '0 48px',
                  fontSize: '16px',
                  fontWeight: '600',
                  background: 'linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%)',
                  border: 'none',
                  borderRadius: '16px',
                  boxShadow: '0 8px 24px rgba(0, 212, 170, 0.3)',
                  transition: 'all 0.3s ease'
                }}
              >
                {connecting ? 'Connecting...' : 'Connect to Database'}
              </Button>
            </Form.Item>
          </Form>
        </div>

        {/* Features Section */}
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
            marginBottom: '20px',
            textAlign: 'center'
          }}>
            Database Connection Features
          </div>
          
          <Row gutter={24}>
            <Col span={8}>
              <div style={{
                background: 'rgba(0, 212, 170, 0.1)',
                border: '1px solid rgba(0, 212, 170, 0.3)',
                borderRadius: '12px',
                padding: '20px',
                textAlign: 'center',
                height: '100%'
              }}>
                <div style={{ fontSize: '32px', marginBottom: '12px' }}>🗄️</div>
                <div style={{ color: '#00d4aa', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                  Supported Databases
                </div>
                <div style={{ color: '#8c8c8c', fontSize: '12px' }}>
                  PostgreSQL, MySQL, SQLite
                </div>
              </div>
            </Col>
            
            <Col span={8}>
              <div style={{
                background: 'rgba(0, 212, 170, 0.1)',
                border: '1px solid rgba(0, 212, 170, 0.3)',
                borderRadius: '12px',
                padding: '20px',
                textAlign: 'center',
                height: '100%'
              }}>
                <div style={{ fontSize: '32px', marginBottom: '12px' }}>🔍</div>
                <div style={{ color: '#00d4aa', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                  Auto Schema Detection
                </div>
                <div style={{ color: '#8c8c8c', fontSize: '12px' }}>
                  Automatic table exploration
                </div>
              </div>
            </Col>
            
            <Col span={8}>
              <div style={{
                background: 'rgba(0, 212, 170, 0.1)',
                border: '1px solid rgba(0, 212, 170, 0.3)',
                borderRadius: '12px',
                padding: '20px',
                textAlign: 'center',
                height: '100%'
              }}>
                <div style={{ fontSize: '32px', marginBottom: '12px' }}>🔒</div>
                <div style={{ color: '#00d4aa', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                  Secure Connection
                </div>
                <div style={{ color: '#8c8c8c', fontSize: '12px' }}>
                  Read-only access, encrypted
                </div>
              </div>
            </Col>
          </Row>
        </div>

        {/* Security Notice */}
        <div style={{
          background: 'rgba(24, 144, 255, 0.1)',
          border: '1px solid rgba(24, 144, 255, 0.3)',
          borderRadius: '12px',
          padding: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <SecurityScanOutlined style={{ color: '#1890ff', fontSize: '20px' }} />
          <div>
            <div style={{ color: '#1890ff', fontSize: '14px', fontWeight: '500', marginBottom: '4px' }}>
              Security Notice
            </div>
            <div style={{ color: '#8c8c8c', fontSize: '12px' }}>
              Your database credentials are encrypted and stored securely. We only establish read-only connections for data analysis.
            </div>
          </div>
        </div>
      </Space>
    </div>
  );
};

export default DatabaseConnection;
