import React, { useState, useEffect } from 'react';
import { Layout, Menu, Card, Row, Col, Button, Dropdown, Space, Typography, Badge, Avatar, Tooltip, Switch, ConfigProvider, message } from 'antd';
import { 
  DatabaseOutlined, 
  FileExcelOutlined, 
  BarChartOutlined, 
  QuestionCircleOutlined,
  UserOutlined,
  SettingOutlined,
  DownloadOutlined,
  ShareAltOutlined,
  PushpinOutlined,
  BulbOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  SunOutlined,
  MoonOutlined
} from '@ant-design/icons';
import FileUpload from './components/FileUpload';
import DatabaseConnection from './components/DatabaseConnection';
import ChatInterface from './components/ChatInterface';
import Visualization from './components/Visualization';
import SessionManager from './components/SessionManager';
import Sidebar from './components/Sidebar';
import TopNavigation from './components/TopNavigation';
import './App.css';

const { Header, Content, Sider } = Layout;
const { Title, Text } = Typography;

function App() {
  const [currentSession, setCurrentSession] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [activeTab, setActiveTab] = useState('upload');
  const [collapsed, setCollapsed] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [pinnedInsights, setPinnedInsights] = useState([]);
  const [visualizations, setVisualizations] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);

  useEffect(() => {
    loadSessions();
    loadPinnedInsights();
    loadChatMessages();
  }, []);

  const loadChatMessages = () => {
    const savedMessages = localStorage.getItem(`chat_${currentSession?.id}`);
    if (savedMessages) {
      try {
        setChatMessages(JSON.parse(savedMessages));
      } catch (error) {
        console.error('Error loading chat messages:', error);
      }
    }
  };

  useEffect(() => {
    loadChatMessages();
  }, [currentSession?.id]);

  const loadSessions = async () => {
    try {
      const response = await fetch('/sessions');
      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const loadPinnedInsights = () => {
    const pinned = localStorage.getItem('pinnedInsights');
    if (pinned) {
      setPinnedInsights(JSON.parse(pinned));
    }
  };

  const handleSessionCreated = (sessionData) => {
    setCurrentSession(sessionData);
    setActiveTab('chat');
    setChatMessages([]); // Clear chat messages for new session
    loadSessions();
  };

  const handleSessionSelected = (session) => {
    setCurrentSession(session);
    setActiveTab('chat');
  };

  const handleTabChange = (key) => {
    setActiveTab(key);
  };

  const handlePinInsight = (insight) => {
    const newPinned = [...pinnedInsights, { ...insight, id: Date.now() }];
    setPinnedInsights(newPinned);
    localStorage.setItem('pinnedInsights', JSON.stringify(newPinned));
    message.success('Insight pinned successfully!');
  };

  const handleUnpinInsight = (id) => {
    const newPinned = pinnedInsights.filter(insight => insight.id !== id);
    setPinnedInsights(newPinned);
    localStorage.setItem('pinnedInsights', JSON.stringify(newPinned));
  };

  const handleVisualizationCreated = (viz) => {
    setVisualizations(prev => [viz, ...prev]);
  };

  const handleChatMessagesChange = (newMessages) => {
    setChatMessages(newMessages);
    if (currentSession?.id) {
      localStorage.setItem(`chat_${currentSession.id}`, JSON.stringify(newMessages));
    }
  };

  const darkTheme = {
    token: {
      colorPrimary: '#00d4aa',
      colorBgBase: '#1a1a1a',
      colorBgContainer: '#2d2d2d',
      colorText: '#ffffff',
      colorTextSecondary: '#8c8c8c',
      colorBorder: '#404040',
      colorBorderSecondary: '#303030',
      borderRadius: 8,
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
    },
    components: {
      Layout: {
        bodyBg: '#1a1a1a',
        headerBg: '#2d2d2d',
        siderBg: '#2d2d2d',
      },
      Card: {
        headerBg: '#404040',
        bodyBg: '#2d2d2d',
      },
      Menu: {
        itemBg: 'transparent',
        itemSelectedBg: '#00d4aa20',
        itemHoverBg: '#00d4aa10',
      }
    }
  };

  const lightTheme = {
    token: {
      colorPrimary: '#1890ff',
      colorBgBase: '#ffffff',
      colorBgContainer: '#f8f9fa',
      colorText: '#333333',
      colorTextSecondary: '#666666',
      colorBorder: '#d9d9d9',
      colorBorderSecondary: '#f0f0f0',
      borderRadius: 8,
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
    }
  };

  const renderMainContent = () => {
    switch (activeTab) {
      case 'upload':
        return (
          <Card 
            title={
              <Space>
                <FileExcelOutlined style={{ color: '#00d4aa' }} />
                <span>Upload Data</span>
              </Space>
            }
            extra={
              <Button type="text" icon={<SettingOutlined />}>
                Settings
              </Button>
            }
            className="main-card"
          >
            <FileUpload onSessionCreated={handleSessionCreated} />
          </Card>
        );
      
      case 'database':
        return (
          <Card 
            title={
              <Space>
                <DatabaseOutlined style={{ color: '#00d4aa' }} />
                <span>Database Connection</span>
              </Space>
            }
            extra={
              <Button type="text" icon={<SettingOutlined />}>
                Settings
              </Button>
            }
            className="main-card"
          >
            <DatabaseConnection onSessionCreated={handleSessionCreated} />
          </Card>
        );
      
      case 'chat':
        return (
          <Row gutter={[24, 24]}>
            <Col xs={24} lg={16}>
              <Card 
                title={
                  <Space>
                    <Avatar 
                      size="small" 
                      style={{ backgroundColor: '#00d4aa' }}
                      icon={<UserOutlined />}
                    />
                    <span>AI Assistant</span>
                  </Space>
                }
                extra={
                  <Space>
                    <Button type="text" icon={<PushpinOutlined />}>
                      Pin Insights
                    </Button>
                    <Button type="text" icon={<SettingOutlined />}>
                      Settings
                    </Button>
                  </Space>
                }
                className="main-card chat-card"
              >
                <ChatInterface 
                  sessionId={currentSession?.id} 
                  onVisualizationCreated={handleVisualizationCreated}
                  messages={chatMessages}
                  onMessagesChange={handleChatMessagesChange}
                />
              </Card>
            </Col>
            <Col xs={24} lg={8}>
              <Space direction="vertical" style={{ width: '100%' }} size="large">
                <Card 
                  title={
                    <Space>
                      <BarChartOutlined style={{ color: '#00d4aa' }} />
                      <span>Quick Actions</span>
                    </Space>
                  }
                  className="main-card"
                >
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Button 
                      block 
                      type="primary" 
                      icon={<BarChartOutlined />}
                      onClick={() => {/* Quick action */}}
                    >
                      Generate Bar Chart
                    </Button>
                    <Button 
                      block 
                      icon={<BarChartOutlined />}
                      onClick={() => {/* Quick action */}}
                    >
                      Show Correlation
                    </Button>
                    <Button 
                      block 
                      icon={<BulbOutlined />}
                      onClick={() => {/* Quick action */}}
                    >
                      Summarize Data
                    </Button>
                    <Button 
                      block 
                      icon={<QuestionCircleOutlined />}
                      onClick={() => {/* Quick action */}}
                    >
                      Ask Questions
                    </Button>
                  </Space>
                </Card>

                <Card 
                  title={
                    <Space>
                      <BarChartOutlined style={{ color: '#00d4aa' }} />
                      <span>Visualization</span>
                      <Badge count={visualizations.length} />
                    </Space>
                  }
                  extra={
                    <Space>
                      <Dropdown
                        menu={{
                          items: [
                            { key: 'csv', label: 'Export CSV', icon: <DownloadOutlined /> },
                            { key: 'png', label: 'Export PNG', icon: <DownloadOutlined /> },
                            { key: 'pdf', label: 'Export PDF', icon: <DownloadOutlined /> },
                          ]
                        }}
                      >
                        <Button size="small" icon={<DownloadOutlined />}>
                          Export
                        </Button>
                      </Dropdown>
                      <Button size="small" icon={<ShareAltOutlined />}>
                        Share
                      </Button>
                    </Space>
                  }
                  className="main-card"
                >
                  <Visualization 
                    sessionId={currentSession?.id}
                    visualizations={visualizations}
                    onPinInsight={handlePinInsight}
                    compact={true}
                    currentViz={visualizations.length > 0 ? visualizations[0] : null}
                  />
                </Card>
              </Space>
            </Col>
          </Row>
        );
      
      case 'visualizations':
        return (
          <div className="full-width-visualization">
            <div className="visualization-header-full">
              <div className="visualization-title-section">
                <Space>
                  <BarChartOutlined style={{ color: '#00d4aa' }} />
                  <span style={{ color: '#ffffff', fontSize: '18px', fontWeight: '600' }}>Visualizations</span>
                  <Badge count={visualizations.length} />
                </Space>
              </div>
              <div className="visualization-actions-full">
                <Space>
                  <Dropdown
                    menu={{
                      items: [
                        { key: 'csv', label: 'Export CSV', icon: <DownloadOutlined /> },
                        { key: 'png', label: 'Export PNG', icon: <DownloadOutlined /> },
                        { key: 'pdf', label: 'Export PDF', icon: <DownloadOutlined /> },
                      ]
                    }}
                  >
                    <Button icon={<DownloadOutlined />}>
                      Export
                    </Button>
                  </Dropdown>
                  <Button icon={<ShareAltOutlined />}>
                    Share
                  </Button>
                  <Button type="text" icon={<SettingOutlined />}>
                    Settings
                  </Button>
                </Space>
              </div>
            </div>
            <Visualization 
              sessionId={currentSession?.id}
              visualizations={visualizations}
              onPinInsight={handlePinInsight}
              currentViz={visualizations.length > 0 ? visualizations[0] : null}
            />
          </div>
        );
      
      case 'sessions':
        return (
          <Card 
            title={
              <Space>
                <UserOutlined style={{ color: '#00d4aa' }} />
                <span>Session Management</span>
              </Space>
            }
            className="main-card"
          >
            <SessionManager 
              sessions={sessions}
              onSessionSelected={handleSessionSelected}
              currentSession={currentSession}
            />
          </Card>
        );
      
      default:
        return null;
    }
  };

  return (
    <ConfigProvider theme={darkMode ? darkTheme : lightTheme}>
      <Layout style={{ minHeight: '100vh' }}>
        {/* Top Navigation */}
        <Header className="top-navigation">
          <div className="nav-content">
            <div className="nav-left">
              <Space>
                <Button
                  type="text"
                  icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                  onClick={() => setCollapsed(!collapsed)}
                  style={{ color: '#ffffff' }}
                />
                <Title level={3} style={{ color: '#ffffff', margin: 0 }}>
                  📊 RAG Analytics
                </Title>
              </Space>
            </div>
            
            <div className="nav-center">
              <TopNavigation 
                activeTab={activeTab}
                onTabChange={handleTabChange}
              />
            </div>
            
            <div className="nav-right">
              <Space>
                <Tooltip title="Toggle Theme">
                  <Switch
                    checked={darkMode}
                    onChange={setDarkMode}
                    checkedChildren={<MoonOutlined />}
                    unCheckedChildren={<SunOutlined />}
                  />
                </Tooltip>
                <Avatar 
                  size="small" 
                  style={{ backgroundColor: '#00d4aa' }}
                  icon={<UserOutlined />}
                />
              </Space>
            </div>
          </div>
        </Header>

        <Layout>
          {/* Sidebar */}
          <Sider 
            trigger={null} 
            collapsible 
            collapsed={collapsed}
            width={280}
            className="sidebar"
          >
            <Sidebar 
              currentSession={currentSession}
              pinnedInsights={pinnedInsights}
              onUnpinInsight={handleUnpinInsight}
              onSessionSelected={handleSessionSelected}
              sessions={sessions}
              visualizations={visualizations}
            />
          </Sider>

          {/* Main Content */}
          <Layout>
            <Content className={`main-content ${activeTab === 'visualizations' ? 'visualization-mode' : ''}`}>
              {activeTab === 'visualizations' ? (
                <div className="visualization-container">
                  {renderMainContent()}
                </div>
              ) : (
                <div className="content-wrapper">
                  {renderMainContent()}
                </div>
              )}
            </Content>
          </Layout>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}

export default App;