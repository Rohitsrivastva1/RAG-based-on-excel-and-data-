import React, { useState, useEffect } from 'react';
import { Card, Typography, Space, Button, message, Spin, Empty } from 'antd';
import { BarChartOutlined, DownloadOutlined, EyeOutlined } from '@ant-design/icons';
import Plot from 'react-plotly.js';

const { Title, Text } = Typography;

const Visualization = ({ sessionId }) => {
  const [visualizations, setVisualizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentViz, setCurrentViz] = useState(null);

  useEffect(() => {
    // Listen for new visualizations from chat interface
    const handleStorageChange = () => {
      const latestViz = localStorage.getItem(`viz_${sessionId}`);
      if (latestViz) {
        try {
          const vizData = JSON.parse(latestViz);
          setVisualizations(prev => [vizData, ...prev]);
          setCurrentViz(vizData);
          localStorage.removeItem(`viz_${sessionId}`);
        } catch (error) {
          console.error('Error parsing visualization data:', error);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [sessionId]);

  const handleExport = async (format, vizData) => {
    try {
      const response = await fetch(`/export/${format}?session_id=${sessionId}&query_id=${vizData.query_id}`);
      
      if (!response.ok) {
        throw new Error(`Export failed: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `visualization_${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      message.success(`Exported as ${format.toUpperCase()}`);
    } catch (error) {
      console.error('Export error:', error);
      message.error('Export failed: ' + error.message);
    }
  };

  const renderVisualization = (vizData) => {
    if (!vizData || !vizData.config) {
      return (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="No visualization data available"
          />
        </div>
      );
    }

    try {
      const config = typeof vizData.config === 'string' 
        ? JSON.parse(vizData.config) 
        : vizData.config;

      // Convert our custom format to Plotly format
      let plotlyData = [];
      let plotlyLayout = {};

      if (config.type === 'bar' && config.data) {
        plotlyData = [{
          x: config.data.x || [],
          y: config.data.y || [],
          type: 'bar',
          marker: {
            color: '#00d4aa',
            line: {
              color: '#00a8ff',
              width: 1
            }
          },
          name: config.data.title || 'Data'
        }];

        plotlyLayout = {
          title: {
            text: config.data.title || 'Chart',
            font: { color: '#ffffff', size: 16 }
          },
          xaxis: {
            title: 'Category',
            color: '#ffffff',
            gridcolor: '#404040',
            linecolor: '#404040',
            tickcolor: '#ffffff'
          },
          yaxis: {
            title: 'Value',
            color: '#ffffff',
            gridcolor: '#404040',
            linecolor: '#404040',
            tickcolor: '#ffffff'
          },
          autosize: true,
          margin: { l: 60, r: 50, t: 60, b: 60 },
          showlegend: false,
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: 'rgba(0,0,0,0)',
          font: {
            color: '#ffffff',
            family: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif'
          }
        };
      } else if (config.data && config.data.data) {
        // Handle nested data format
        plotlyData = config.data.data || [];
        plotlyLayout = config.data.layout || {};
      } else {
        // Fallback to original format
        plotlyData = config.data || [];
        plotlyLayout = config.layout || {};
      }

      return (
        <Plot
          data={plotlyData}
          layout={{
            ...plotlyLayout,
            autosize: true,
            margin: { l: 60, r: 50, t: 60, b: 60 },
            showlegend: true,
            // Dark theme for Plotly
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {
              color: '#ffffff',
              family: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif'
            },
            xaxis: {
              ...plotlyLayout.xaxis,
              color: '#ffffff',
              gridcolor: '#404040',
              linecolor: '#404040',
              tickcolor: '#ffffff'
            },
            yaxis: {
              ...plotlyLayout.yaxis,
              color: '#ffffff',
              gridcolor: '#404040',
              linecolor: '#404040',
              tickcolor: '#ffffff'
            },
            legend: {
              bgcolor: 'rgba(0,0,0,0)',
              bordercolor: '#404040',
              font: {
                color: '#ffffff'
              }
            }
          }}
          config={{
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            displaylogo: false,
            toImageButtonOptions: {
              format: 'png',
              filename: 'visualization',
              height: 500,
              width: 700,
              scale: 1
            }
          }}
          style={{ width: '100%', height: '400px' }}
          useResizeHandler={true}
        />
      );
    } catch (error) {
      console.error('Error rendering visualization:', error);
      return (
        <div style={{ textAlign: 'center', padding: '40px', color: '#ff4d4f' }}>
          Error rendering visualization: {error.message}
        </div>
      );
    }
  };

  return (
    <div style={{
      background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
      borderRadius: '20px',
      padding: '24px',
      border: '1px solid #404040',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
      marginTop: '24px'
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
              <BarChartOutlined style={{ color: '#ffffff', fontSize: '24px' }} />
            </div>
            <div>
              <div style={{ 
                color: '#ffffff', 
                fontSize: '20px', 
                fontWeight: '600',
                margin: 0
              }}>
                Data Visualizations
              </div>
              <div style={{ 
                color: '#8c8c8c', 
                fontSize: '14px',
                margin: 0
              }}>
                Interactive charts and insights from your data
              </div>
            </div>
          </div>
          
          {visualizations.length > 0 && (
            <div style={{
              background: 'rgba(0, 212, 170, 0.1)',
              border: '1px solid rgba(0, 212, 170, 0.3)',
              borderRadius: '12px',
              padding: '8px 16px'
            }}>
              <div style={{ 
                color: '#00d4aa', 
                fontSize: '14px', 
                fontWeight: '500'
              }}>
                {visualizations.length} visualization{visualizations.length !== 1 ? 's' : ''}
              </div>
            </div>
          )}
        </div>

        {/* Visualization Selector */}
        {visualizations.length > 0 && (
          <div style={{
            background: 'rgba(45, 45, 45, 0.5)',
            borderRadius: '16px',
            padding: '20px',
            border: '1px solid #404040'
          }}>
            <div style={{ 
              color: '#ffffff', 
              fontSize: '16px', 
              fontWeight: '500',
              marginBottom: '16px'
            }}>
              Recent Visualizations:
            </div>
            <div style={{ 
              display: 'flex', 
              gap: '12px', 
              flexWrap: 'wrap' 
            }}>
              {visualizations.map((viz, index) => (
                <Button
                  key={index}
                  type={currentViz === viz ? 'primary' : 'default'}
                  size="small"
                  icon={<EyeOutlined />}
                  onClick={() => setCurrentViz(viz)}
                  style={{
                    background: currentViz === viz 
                      ? 'linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%)'
                      : 'rgba(45, 45, 45, 0.8)',
                    border: currentViz === viz 
                      ? 'none'
                      : '1px solid #404040',
                    color: '#ffffff',
                    borderRadius: '8px',
                    fontWeight: '500'
                  }}
                >
                  {viz.chart_type} #{index + 1}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Visualization Container */}
        <div style={{
          background: 'rgba(45, 45, 45, 0.3)',
          borderRadius: '16px',
          padding: '24px',
          border: '1px solid #404040',
          minHeight: '400px'
        }}>
          {currentViz ? (
            <div style={{ width: '100%' }}>
              {renderVisualization(currentViz)}
              
              {/* Export Buttons */}
              <div style={{ 
                marginTop: '24px',
                display: 'flex',
                gap: '12px',
                justifyContent: 'center',
                flexWrap: 'wrap'
              }}>
                <Button
                  icon={<DownloadOutlined />}
                  onClick={() => handleExport('csv', currentViz)}
                  style={{
                    background: 'rgba(0, 212, 170, 0.1)',
                    border: '1px solid rgba(0, 212, 170, 0.3)',
                    color: '#00d4aa',
                    borderRadius: '8px',
                    fontWeight: '500'
                  }}
                >
                  Export CSV
                </Button>
                <Button
                  icon={<DownloadOutlined />}
                  onClick={() => handleExport('png', currentViz)}
                  style={{
                    background: 'rgba(0, 212, 170, 0.1)',
                    border: '1px solid rgba(0, 212, 170, 0.3)',
                    color: '#00d4aa',
                    borderRadius: '8px',
                    fontWeight: '500'
                  }}
                >
                  Export PNG
                </Button>
                <Button
                  icon={<DownloadOutlined />}
                  onClick={() => handleExport('pdf', currentViz)}
                  style={{
                    background: 'rgba(0, 212, 170, 0.1)',
                    border: '1px solid rgba(0, 212, 170, 0.3)',
                    color: '#00d4aa',
                    borderRadius: '8px',
                    fontWeight: '500'
                  }}
                >
                  Export PDF
                </Button>
              </div>
            </div>
          ) : (
            <div style={{ 
              textAlign: 'center', 
              padding: '60px 20px',
              background: 'rgba(45, 45, 45, 0.3)',
              borderRadius: '16px',
              border: '1px solid #404040'
            }}>
              <div style={{ fontSize: '64px', marginBottom: '24px', opacity: 0.5 }}>📊</div>
              <div style={{ 
                color: '#ffffff', 
                fontSize: '18px', 
                fontWeight: '500',
                marginBottom: '12px'
              }}>
                Ready to Visualize Your Data
              </div>
              <div style={{ 
                color: '#8c8c8c', 
                fontSize: '14px',
                marginBottom: '24px'
              }}>
                Ask questions to generate interactive charts and insights
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
                <BarChartOutlined />
                Visualizations will appear here
              </div>
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px 20px',
            background: 'rgba(45, 45, 45, 0.3)',
            borderRadius: '16px',
            border: '1px solid #404040'
          }}>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '12px',
              background: 'rgba(0, 212, 170, 0.1)',
              padding: '12px 24px',
              borderRadius: '16px',
              border: '1px solid rgba(0, 212, 170, 0.3)'
            }}>
              <Spin size="small" style={{ color: '#00d4aa' }} />
              <div style={{ color: '#00d4aa', fontSize: '14px' }}>
                Generating visualization...
              </div>
            </div>
          </div>
        )}
      </Space>
    </div>
  );
};

export default Visualization;
