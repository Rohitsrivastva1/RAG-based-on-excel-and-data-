import React, { useState, useEffect } from 'react';
import { Layout, Tabs, message, ConfigProvider } from 'antd';
import { DatabaseOutlined, FileExcelOutlined, BarChartOutlined } from '@ant-design/icons';
import FileUpload from './components/FileUpload';
import DatabaseConnection from './components/DatabaseConnection';
import ChatInterface from './components/ChatInterface';
import Visualization from './components/Visualization';
import SessionManager from './components/SessionManager';
import './App.css';

const { Header, Content } = Layout;
const { TabPane } = Tabs;

function App() {
  const [currentSession, setCurrentSession] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [activeTab, setActiveTab] = useState('upload');

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await fetch('/sessions');
      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const handleSessionCreated = (sessionData) => {
    setCurrentSession(sessionData);
    setActiveTab('chat');
    loadSessions();
    message.success('Data source connected successfully!');
  };

  const handleSessionSelected = (session) => {
    setCurrentSession(session);
    setActiveTab('chat');
  };

  const handleTabChange = (key) => {
    setActiveTab(key);
  };

  const darkTheme = {
    token: {
      colorBgBase: '#1a1a1a',
      colorBgContainer: '#2d2d2d',
      colorBgElevated: '#3a3a3a',
      colorBorder: '#404040',
      colorText: '#ffffff',
      colorTextSecondary: '#b3b3b3',
      colorTextTertiary: '#8c8c8c',
      colorPrimary: '#00d4aa',
      colorSuccess: '#52c41a',
      colorWarning: '#faad14',
      colorError: '#ff4d4f',
      colorInfo: '#1890ff',
      borderRadius: 12,
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
    },
    components: {
      Layout: {
        headerBg: '#1a1a1a',
        bodyBg: '#1a1a1a',
        siderBg: '#2d2d2d',
      },
      Tabs: {
        itemColor: '#b3b3b3',
        itemHoverColor: '#ffffff',
        itemSelectedColor: '#00d4aa',
        inkBarColor: '#00d4aa',
        cardBg: '#2d2d2d',
      },
      Card: {
        colorBgContainer: '#2d2d2d',
        colorBorderSecondary: '#404040',
      },
    },
  };

  return (
    <ConfigProvider theme={darkTheme}>
      <div className="app-container dark-theme">
        <Header style={{ 
          background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)', 
          padding: '0 24px', 
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
          borderBottom: '1px solid #404040'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '16px',
                boxShadow: '0 4px 12px rgba(0, 212, 170, 0.3)'
              }}>
                <BarChartOutlined style={{ fontSize: '20px', color: '#ffffff' }} />
              </div>
              <h1 style={{ 
                margin: 0, 
                color: '#ffffff',
                fontSize: '24px',
                fontWeight: '600',
                background: 'linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>RAG Analytics</h1>
            </div>
            {currentSession && (
              <div style={{
                background: 'rgba(0, 212, 170, 0.1)',
                border: '1px solid rgba(0, 212, 170, 0.3)',
                borderRadius: '8px',
                padding: '8px 16px',
                color: '#00d4aa',
                fontSize: '14px',
                fontWeight: '500'
              }}>
                <strong>Active:</strong> {currentSession.data_source_type} - {currentSession.id.slice(0, 8)}...
              </div>
            )}
          </div>
        </Header>

        <Content style={{ 
          padding: '24px',
          background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
          minHeight: 'calc(100vh - 64px)'
        }}>
          <Tabs 
            activeKey={activeTab} 
            onChange={handleTabChange} 
            size="large"
            style={{
              '& .ant-tabs-tab': {
                color: '#b3b3b3 !important',
              },
              '& .ant-tabs-tab-active': {
                color: '#00d4aa !important',
              }
            }}
          >
            <TabPane 
              tab={<span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileExcelOutlined />Upload Data
              </span>} 
              key="upload"
            >
              <FileUpload onSessionCreated={handleSessionCreated} />
            </TabPane>
            
            <TabPane 
              tab={<span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <DatabaseOutlined />Connect Database
              </span>} 
              key="database"
            >
              <DatabaseConnection onSessionCreated={handleSessionCreated} />
            </TabPane>
            
            <TabPane 
              tab={<span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BarChartOutlined />Ask Questions
              </span>} 
              key="chat"
              disabled={!currentSession}
            >
              {currentSession ? (
                <div>
                  <ChatInterface sessionId={currentSession.id} />
                  <Visualization sessionId={currentSession.id} />
                </div>
              ) : (
                <div style={{ 
                  textAlign: 'center', 
                  padding: '60px 40px', 
                  color: '#8c8c8c',
                  background: 'rgba(45, 45, 45, 0.5)',
                  borderRadius: '16px',
                  border: '1px solid #404040'
                }}>
                  <div style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.5 }}>📊</div>
                  <div style={{ fontSize: '18px', marginBottom: '8px' }}>No Active Session</div>
                  <div>Please upload a file or connect to a database first</div>
                </div>
              )}
            </TabPane>
            
            <TabPane 
              tab="Sessions" 
              key="sessions"
            >
              <SessionManager 
                sessions={sessions} 
                onSessionSelected={handleSessionSelected}
                onSessionsUpdated={loadSessions}
              />
            </TabPane>
          </Tabs>
        </Content>
      </div>
    </ConfigProvider>
  );
}

export default App;
