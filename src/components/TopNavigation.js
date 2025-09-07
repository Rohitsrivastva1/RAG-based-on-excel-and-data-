import React from 'react';
import { Menu } from 'antd';
import { 
  FileExcelOutlined, 
  DatabaseOutlined, 
  QuestionCircleOutlined, 
  BarChartOutlined, 
  UserOutlined 
} from '@ant-design/icons';

const TopNavigation = ({ activeTab, onTabChange }) => {
  const menuItems = [
    {
      key: 'upload',
      icon: <FileExcelOutlined />,
      label: 'Upload Data',
    },
    {
      key: 'database',
      icon: <DatabaseOutlined />,
      label: 'Database',
    },
    {
      key: 'chat',
      icon: <QuestionCircleOutlined />,
      label: 'Ask Questions',
    },
    {
      key: 'visualizations',
      icon: <BarChartOutlined />,
      label: 'Visualizations',
    },
    {
      key: 'sessions',
      icon: <UserOutlined />,
      label: 'Sessions',
    },
  ];

  return (
    <Menu
      mode="horizontal"
      selectedKeys={[activeTab]}
      onClick={({ key }) => onTabChange(key)}
      items={menuItems}
      className="top-nav-menu"
    />
  );
};

export default TopNavigation;
