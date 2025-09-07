import React, { useState, useEffect } from 'react';
import { Card, Typography, Space, Button, message, Spin, Empty, Row, Col, Dropdown, Tooltip, Tag, Divider } from 'antd';
import { 
  BarChartOutlined, 
  DownloadOutlined, 
  EyeOutlined, 
  EditOutlined, 
  ShareAltOutlined, 
  PushpinOutlined,
  DeleteOutlined,
  SettingOutlined,
  BulbOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import Plot from 'react-plotly.js';

const { Title, Text } = Typography;

const Visualization = ({ sessionId, visualizations = [], onPinInsight, compact = false, currentViz: propCurrentViz = null }) => {
  const [currentViz, setCurrentViz] = useState(null);
  const [loading, setLoading] = useState(false);
  const [insights, setInsights] = useState([]);

  useEffect(() => {
    // Use propCurrentViz if available, otherwise listen for localStorage changes
    if (propCurrentViz) {
      console.log('Using prop currentViz:', propCurrentViz);
      setCurrentViz(propCurrentViz);
      generateInsights(propCurrentViz);
      return;
    }

    // Listen for new visualizations from chat interface
    const handleStorageChange = () => {
      const latestViz = localStorage.getItem(`viz_${sessionId}`);
      if (latestViz) {
        try {
          const vizData = JSON.parse(latestViz);
          console.log('Received visualization data:', vizData);
          setCurrentViz(vizData);
          generateInsights(vizData);
          localStorage.removeItem(`viz_${sessionId}`);
        } catch (error) {
          console.error('Error parsing visualization data:', error);
        }
      }
    };

    // Also check for existing data on mount
    const existingViz = localStorage.getItem(`viz_${sessionId}`);
    if (existingViz) {
      try {
        const vizData = JSON.parse(existingViz);
        console.log('Found existing visualization data:', vizData);
        setCurrentViz(vizData);
        generateInsights(vizData);
        localStorage.removeItem(`viz_${sessionId}`);
      } catch (error) {
        console.error('Error parsing existing visualization data:', error);
      }
    }

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [sessionId, propCurrentViz]);

  const generateInsights = (vizData) => {
    if (!vizData || !vizData.data) return;

    const newInsights = [];
    const data = vizData.data;

    // Generate insights based on chart type
    if (vizData.type === 'pie') {
      const labels = data.labels || [];
      const values = data.values || [];
      
      if (labels.length > 0 && values.length > 0) {
        const maxIndex = values.indexOf(Math.max(...values));
        const maxValue = values[maxIndex];
        const maxLabel = labels[maxIndex];
        const total = values.reduce((sum, val) => sum + val, 0);
        const percentage = ((maxValue / total) * 100).toFixed(1);
        
        newInsights.push({
          type: 'insight',
          title: 'Key Finding',
          description: `${maxLabel} has the largest share: ${percentage}%`,
          value: percentage,
          color: '#00d4aa'
        });
      }
    } else if (vizData.type === 'bar') {
      const xData = data.x || [];
      const yData = data.y || [];
      
      if (xData.length > 0 && yData.length > 0) {
        const maxIndex = yData.indexOf(Math.max(...yData));
        const maxValue = yData[maxIndex];
        const maxLabel = xData[maxIndex];
        
        newInsights.push({
          type: 'insight',
          title: 'Top Performer',
          description: `${maxLabel} leads with ${maxValue.toLocaleString()}`,
          value: maxValue,
          color: '#f39c12'
        });
      }
    }

    setInsights(newInsights);
  };

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

  const handlePinInsight = (insight) => {
    if (onPinInsight) {
      onPinInsight({
        ...insight,
        title: insight.title,
        description: insight.description,
        type: 'insight'
      });
      message.success('Insight pinned!');
    }
  };

  const renderVisualization = (vizData, isCompact = false) => {
    console.log('Rendering visualization:', vizData, 'isCompact:', isCompact);
    
    if (!vizData) {
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
      // Handle different data structures
      let config;
      if (vizData.config) {
        config = typeof vizData.config === 'string' 
          ? JSON.parse(vizData.config) 
          : vizData.config;
      } else if (vizData.data) {
        // If data is directly in vizData.data, create a config
        config = {
          type: vizData.type || 'bar',
          data: vizData.data
        };
      } else {
        // If vizData itself is the config
        config = vizData;
      }
      
      console.log('Processed config:', config);

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
      } else if (config.type === 'pie' && config.data) {
        // Handle pie chart data structure
        const labels = config.data.labels || config.data.x || [];
        const values = config.data.values || config.data.y || [];
        
        plotlyData = [{
          labels: labels,
          values: values,
          type: 'pie',
          marker: {
            colors: ['#00d4aa', '#00a8ff', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3'],
            line: {
              color: '#ffffff',
              width: 2
            }
          },
          textinfo: 'label+percent',
          textposition: 'outside',
          hovertemplate: '<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percent}<extra></extra>'
        }];

        plotlyLayout = {
          title: {
            text: config.data.title || config.title || 'Pie Chart',
            font: { color: '#ffffff', size: 16 }
          },
          autosize: true,
          margin: { l: 60, r: 60, t: 60, b: 60 },
          showlegend: true,
          legend: {
            orientation: 'v',
            x: 1.02,
            y: 0.5,
            bgcolor: 'rgba(0,0,0,0)',
            bordercolor: '#404040',
            font: { color: '#ffffff' }
          },
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
      } else if (config.data && Array.isArray(config.data)) {
        // Handle direct array format
        plotlyData = config.data;
        plotlyLayout = config.layout || {};
      } else {
        // Fallback to original format
        plotlyData = config.data || [];
        plotlyLayout = config.layout || {};
      }
      
      console.log('Plotly data:', plotlyData);
      console.log('Plotly layout:', plotlyLayout);

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
            displayModeBar: isCompact ? false : true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            displaylogo: false,
            toImageButtonOptions: {
              format: 'png',
              filename: 'visualization',
              height: isCompact ? 200 : 500,
              width: isCompact ? 300 : 800,
              scale: 1
            }
          }}
          style={{ 
            width: '100%', 
            height: isCompact ? '200px' : '500px',
            minHeight: isCompact ? '200px' : '500px'
          }}
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

  // Compact mode for sidebar
  if (compact) {
    return (
      <div className="visualization-container-compact">
        {currentViz ? (
          <div className="compact-viz">
            <div style={{ marginBottom: '12px' }}>
              <Text strong style={{ color: '#ffffff', fontSize: '12px' }}>
                {currentViz.title || 'Data Visualization'}
              </Text>
              <Tag color="blue" size="small" style={{ marginLeft: '8px' }}>
                {currentViz.type?.toUpperCase() || 'CHART'}
              </Tag>
            </div>
            <div style={{ height: '200px', width: '100%', position: 'relative', background: '#1a1a1a', borderRadius: '4px' }}>
              {renderVisualization(currentViz, true)}
            </div>
            {insights.length > 0 && (
              <div style={{ marginTop: '12px' }}>
                <Text style={{ color: '#00d4aa', fontSize: '11px', fontWeight: 'bold' }}>
                  💡 {insights[0].description}
                </Text>
              </div>
            )}
            {/* Debug info */}
            <div style={{ marginTop: '8px', fontSize: '10px', color: '#666' }}>
              Debug: {currentViz.type || 'No type'} - {currentViz.data ? 'Has data' : 'No data'} - {currentViz.config ? 'Has config' : 'No config'}
            </div>
          </div>
        ) : (
          <div style={{ 
            textAlign: 'center', 
            padding: '20px 10px',
            background: 'rgba(45, 45, 45, 0.3)',
            borderRadius: '8px',
            border: '1px solid #404040'
          }}>
            <div style={{ fontSize: '32px', marginBottom: '12px', opacity: 0.5 }}>📊</div>
            <Text style={{ color: '#8c8c8c', fontSize: '12px' }}>
              Ask questions to generate charts
            </Text>
          </div>
        )}
      </div>
    );
  }

  // Full mode for main visualization page
  return (
    <div className="visualization-container">
      {/* Debug info for full mode */}
     
      {/* Key Insights */}
      {insights.length > 0 && (
        <div className="insights-section">
          <Title level={4} style={{ color: '#ffffff', marginBottom: '16px' }}>
            <BulbOutlined style={{ color: '#f39c12', marginRight: '8px' }} />
            Key Insights
          </Title>
          <Row gutter={[16, 16]}>
            {insights.map((insight, index) => (
              <Col xs={24} sm={12} lg={8} key={index}>
                <Card 
                  className="insight-card"
                  style={{ 
                    background: `linear-gradient(135deg, ${insight.color}20 0%, ${insight.color}10 100%)`,
                    border: `1px solid ${insight.color}`,
                    borderRadius: '12px'
                  }}
                >
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Text strong style={{ color: insight.color, fontSize: '14px' }}>
                        {insight.title}
                      </Text>
                      <Space>
                        <Tooltip title="Pin Insight">
                          <Button 
                            type="text" 
                            size="small" 
                            icon={<PushpinOutlined />}
                            onClick={() => handlePinInsight(insight)}
                          />
                        </Tooltip>
                      </Space>
                    </div>
                    <Text style={{ color: '#ffffff', fontSize: '13px' }}>
                      {insight.description}
                    </Text>
                    {insight.value && (
                      <Text style={{ color: insight.color, fontSize: '18px', fontWeight: 'bold' }}>
                        {typeof insight.value === 'number' ? insight.value.toLocaleString() : insight.value}
                      </Text>
                    )}
                  </Space>
                </Card>
              </Col>
            ))}
          </Row>
          <Divider style={{ margin: '24px 0' }} />
        </div>
      )}

      {/* Visualization Grid */}
      <div className="visualization-grid">
        {currentViz ? (
          <div className="visualization-card-full">
            <div className="visualization-body-full">
              {renderVisualization(currentViz, false)}
            </div>
          </div>
        ) : (
          <div className="visualization-card-full">
            <div style={{ 
              textAlign: 'center', 
              padding: '60px 20px',
              background: 'rgba(45, 45, 45, 0.3)',
              borderRadius: '12px',
              border: '1px solid #404040',
              margin: '20px'
            }}>
              <div style={{ fontSize: '64px', marginBottom: '24px', opacity: 0.5 }}>📊</div>
              <Title level={4} style={{ color: '#ffffff', marginBottom: '12px' }}>
                Ready to Visualize Your Data
              </Title>
              <Text style={{ color: '#8c8c8c', fontSize: '14px' }}>
                Ask questions to generate interactive charts and insights
              </Text>
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
          border: '1px solid #404040',
          marginTop: '24px'
        }}>
          <Spin size="large" style={{ color: '#00d4aa' }} />
          <div style={{ color: '#00d4aa', fontSize: '16px', marginTop: '16px' }}>
            Generating visualization...
          </div>
        </div>
      )}
    </div>
  );
};

export default Visualization;