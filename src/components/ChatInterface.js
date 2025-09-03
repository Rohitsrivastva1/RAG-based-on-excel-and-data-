import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, Card, Typography, Space, message, Spin, Tag, Tooltip } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined, CopyOutlined, CheckOutlined } from '@ant-design/icons';
import TypingAnimation from './TypingAnimation';

const { TextArea } = Input;
const { Title, Text } = Typography;

const ChatInterface = ({ sessionId }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [typingMessage, setTypingMessage] = useState(null);
  const [copiedStates, setCopiedStates] = useState({});
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('question', inputValue);
      formData.append('session_id', sessionId);

      const response = await fetch('/ask_question', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: {
          question: result.question,
          answer: result.answer,
          query_type: result.query_type,
          data: result.data,
          visualization: result.visualization,
          sql_query: result.sql_query,
          row_count: result.row_count,
          timestamp: result.timestamp
        },
        timestamp: new Date().toISOString()
      };

      // Start typing animation
      setTypingMessage(assistantMessage);
      setMessages(prev => [...prev, assistantMessage]);
      
      // Store visualization data for Visualization component
      if (result.visualization && result.visualization.data) {
        const vizData = {
          config: result.visualization,
          chart_type: result.visualization.type || 'bar',
          query_id: Date.now(),
          timestamp: new Date().toISOString()
        };
        localStorage.setItem(`viz_${sessionId}`, JSON.stringify(vizData));
        // Trigger storage event for Visualization component
        window.dispatchEvent(new StorageEvent('storage', {
          key: `viz_${sessionId}`,
          newValue: JSON.stringify(vizData),
          storageArea: localStorage
        }));
      }
      
    } catch (error) {
      console.error('Error asking question:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: `Error: ${error.message}`,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
      message.error('Failed to process question');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleCopy = async (text, messageId) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedStates(prev => ({ ...prev, [messageId]: true }));
      setTimeout(() => {
        setCopiedStates(prev => ({ ...prev, [messageId]: false }));
      }, 2000);
      message.success('Copied to clipboard!');
    } catch (err) {
      message.error('Failed to copy text');
    }
  };

  const handleTypingComplete = () => {
    setTypingMessage(null);
  };

  const renderMessage = (msg) => {
    const isUser = msg.type === 'user';
    const isError = msg.type === 'error';
    const isTyping = typingMessage && typingMessage.id === msg.id;
    
    return (
      <div key={msg.id} style={{ 
        marginBottom: '24px',
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        alignItems: 'flex-start',
        gap: '12px'
      }}>
        {/* Avatar */}
        <div style={{ 
          width: '36px', 
          height: '36px', 
          borderRadius: '50%', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          background: isUser 
            ? 'linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%)' 
            : isError 
            ? 'linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%)'
            : 'linear-gradient(135deg, #2d2d2d 0%, #404040 100%)',
          color: 'white',
          flexShrink: 0,
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
          border: '2px solid rgba(255, 255, 255, 0.1)'
        }}>
          {isUser ? <UserOutlined style={{ fontSize: '16px' }} /> : 
           isError ? <RobotOutlined style={{ fontSize: '16px' }} /> : 
           <RobotOutlined style={{ fontSize: '16px' }} />}
        </div>
        
        {/* Message Content */}
        <div style={{ 
          flex: 1,
          maxWidth: '80%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: isUser ? 'flex-end' : 'flex-start'
        }}>
          {/* Message Bubble */}
          <div style={{
            background: isUser 
              ? 'linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%)'
              : isError
              ? 'linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%)'
              : 'linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%)',
            borderRadius: '18px',
            padding: '16px 20px',
            color: '#ffffff',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            position: 'relative',
            wordWrap: 'break-word'
          }}>
            {isUser ? (
              <div style={{ fontSize: '15px', lineHeight: '1.5' }}>
                {msg.content}
              </div>
            ) : isError ? (
              <div style={{ fontSize: '15px', lineHeight: '1.5' }}>
                {msg.content}
              </div>
            ) : (
              <div>
                {/* Question */}
                <div style={{ 
                  marginBottom: '12px',
                  fontSize: '14px',
                  opacity: 0.9,
                  fontWeight: '500'
                }}>
                  <strong>Question:</strong> {msg.content.question || 'No question provided'}
                </div>
                
                {/* Answer with typing animation */}
                <div style={{ 
                  marginBottom: '12px',
                  fontSize: '15px',
                  lineHeight: '1.6'
                }}>
                  {isTyping ? (
                    <TypingAnimation 
                      text={msg.content.answer || 'No answer provided'} 
                      speed={20}
                      onComplete={handleTypingComplete}
                    />
                  ) : (
                    msg.content.answer || 'No answer provided'
                  )}
                </div>
                
                {/* Copy Button */}
                <div style={{ 
                  position: 'absolute',
                  top: '8px',
                  right: '8px',
                  opacity: 0.7,
                  transition: 'opacity 0.2s'
                }}>
                  <Tooltip title={copiedStates[msg.id] ? "Copied!" : "Copy"}>
                    <Button
                      type="text"
                      size="small"
                      icon={copiedStates[msg.id] ? <CheckOutlined /> : <CopyOutlined />}
                      onClick={() => handleCopy(msg.content.answer || '', msg.id)}
                      style={{ 
                        color: '#ffffff',
                        border: 'none',
                        background: 'rgba(255, 255, 255, 0.1)',
                        borderRadius: '6px'
                      }}
                    />
                  </Tooltip>
                </div>
                
                {/* Query Type Badge */}
                {msg.content.query_type && (
                  <div style={{ marginBottom: '12px' }}>
                    <Tag 
                      color="blue" 
                      style={{ 
                        background: 'rgba(24, 144, 255, 0.2)',
                        border: '1px solid rgba(24, 144, 255, 0.3)',
                        color: '#ffffff',
                        borderRadius: '8px'
                      }}
                    >
                      {msg.content.query_type}
                    </Tag>
                  </div>
                )}
                
                {/* SQL Query */}
                {msg.content.sql_query && (
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ 
                      fontSize: '13px',
                      marginBottom: '6px',
                      opacity: 0.9
                    }}>
                      <strong>SQL Query:</strong>
                    </div>
                    <div style={{ 
                      padding: '12px',
                      background: 'rgba(0, 0, 0, 0.3)',
                      borderRadius: '8px',
                      fontFamily: 'Monaco, Consolas, monospace',
                      fontSize: '12px',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      overflow: 'auto'
                    }}>
                      {msg.content.sql_query}
                    </div>
                  </div>
                )}
                
                {/* Row Count */}
                {msg.content.row_count && (
                  <div style={{ marginBottom: '12px' }}>
                    <Tag 
                      color="green"
                      style={{ 
                        background: 'rgba(82, 196, 26, 0.2)',
                        border: '1px solid rgba(82, 196, 26, 0.3)',
                        color: '#ffffff',
                        borderRadius: '8px'
                      }}
                    >
                      Rows: {msg.content.row_count}
                    </Tag>
                  </div>
                )}
                
                {/* Data Summary */}
                {msg.content.data && msg.content.data.summary && (
                  <div style={{ 
                    marginTop: '12px',
                    padding: '12px',
                    background: 'rgba(0, 0, 0, 0.2)',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}>
                    <div style={{ 
                      fontSize: '13px',
                      marginBottom: '8px',
                      opacity: 0.9
                    }}>
                      <strong>Data Summary:</strong>
                    </div>
                    <div style={{ fontSize: '12px', lineHeight: '1.5' }}>
                      <div>Total Rows: {msg.content.data.summary.total_rows || 'N/A'}</div>
                      <div>Total Columns: {msg.content.data.summary.total_columns || 'N/A'}</div>
                      <div>Columns: {msg.content.data.summary.column_names ? msg.content.data.summary.column_names.join(', ') : 'N/A'}</div>
                    </div>
                  </div>
                )}
                
                {/* Data Preview Table */}
                {msg.content.visualization && msg.content.visualization.data && msg.content.visualization.data.length > 0 && msg.content.visualization.data[0] && (
                  <div style={{ 
                    marginTop: '12px',
                    background: 'rgba(0, 0, 0, 0.2)',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    overflow: 'hidden'
                  }}>
                    <div style={{ 
                      padding: '12px',
                      fontSize: '13px',
                      opacity: 0.9,
                      borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
                    }}>
                      <strong>Data Preview:</strong>
                    </div>
                    <div style={{ 
                      maxHeight: '200px', 
                      overflow: 'auto'
                    }}>
                      <table style={{ width: '100%', fontSize: '11px' }}>
                        <thead style={{ background: 'rgba(0, 0, 0, 0.3)' }}>
                          <tr>
                            {Object.keys(msg.content.visualization.data[0]).map(key => (
                              <th key={key} style={{ 
                                padding: '8px 12px', 
                                textAlign: 'left',
                                borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                                color: '#ffffff'
                              }}>
                                {key}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {msg.content.visualization.data.slice(0, 5).map((row, idx) => (
                            <tr key={idx} style={{ 
                              borderBottom: idx < 4 ? '1px solid rgba(255, 255, 255, 0.05)' : 'none'
                            }}>
                              {Object.values(row).map((value, valIdx) => (
                                <td key={valIdx} style={{ 
                                  padding: '8px 12px',
                                  color: '#ffffff',
                                  opacity: 0.9
                                }}>
                                  {String(value || '')}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {msg.content.visualization.data.length > 5 && (
                        <div style={{ 
                          padding: '12px', 
                          textAlign: 'center', 
                          color: '#ffffff',
                          opacity: 0.7,
                          fontSize: '12px',
                          borderTop: '1px solid rgba(255, 255, 255, 0.1)'
                        }}>
                          ... and {msg.content.visualization.data.length - 5} more rows
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Timestamp */}
          <div style={{ 
            fontSize: '11px', 
            color: '#8c8c8c', 
            marginTop: '6px',
            marginLeft: isUser ? '0' : '8px',
            marginRight: isUser ? '8px' : '0'
          }}>
            {new Date(msg.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div style={{
      background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
      borderRadius: '20px',
      padding: '24px',
      border: '1px solid #404040',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
      minHeight: '600px',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Header */}
      <div style={{ 
        marginBottom: '24px',
        textAlign: 'center',
        paddingBottom: '20px',
        borderBottom: '1px solid #404040'
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
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <RobotOutlined style={{ color: '#ffffff', fontSize: '16px' }} />
          </div>
          <div>
            <div style={{ 
              color: '#ffffff', 
              fontSize: '18px', 
              fontWeight: '600',
              margin: 0
            }}>
              AI Data Assistant
            </div>
            <div style={{ 
              color: '#8c8c8c', 
              fontSize: '12px',
              margin: 0
            }}>
              Ask natural language questions about your data
            </div>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div style={{ 
        flex: 1,
        overflowY: 'auto',
        padding: '0 8px',
        marginBottom: '24px',
        maxHeight: '500px'
      }}>
        {messages.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            color: '#8c8c8c', 
            padding: '60px 20px',
            background: 'rgba(45, 45, 45, 0.3)',
            borderRadius: '16px',
            border: '1px solid #404040'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.5 }}>💬</div>
            <div style={{ fontSize: '16px', marginBottom: '8px', color: '#ffffff' }}>
              Start a conversation with your data
            </div>
            <div style={{ fontSize: '14px', marginBottom: '16px' }}>
              Ask questions like:
            </div>
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              gap: '8px',
              alignItems: 'center'
            }}>
              <div style={{
                background: 'rgba(0, 212, 170, 0.1)',
                border: '1px solid rgba(0, 212, 170, 0.3)',
                borderRadius: '8px',
                padding: '8px 16px',
                fontSize: '12px',
                color: '#00d4aa'
              }}>
                "What are the top 10 sales by region?"
              </div>
              <div style={{
                background: 'rgba(0, 212, 170, 0.1)',
                border: '1px solid rgba(0, 212, 170, 0.3)',
                borderRadius: '8px',
                padding: '8px 16px',
                fontSize: '12px',
                color: '#00d4aa'
              }}>
                "Show me trends over time"
              </div>
              <div style={{
                background: 'rgba(0, 212, 170, 0.1)',
                border: '1px solid rgba(0, 212, 170, 0.3)',
                borderRadius: '8px',
                padding: '8px 16px',
                fontSize: '12px',
                color: '#00d4aa'
              }}>
                "How many rows are in each category?"
              </div>
            </div>
          </div>
        ) : (
          messages.map(renderMessage)
        )}
        
        {loading && (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px 20px',
            background: 'rgba(45, 45, 45, 0.3)',
            borderRadius: '16px',
            border: '1px solid #404040',
            margin: '20px 0'
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
                AI is thinking...
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div style={{ 
        background: 'rgba(45, 45, 45, 0.5)',
        borderRadius: '16px',
        padding: '16px',
        border: '1px solid #404040',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <TextArea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your data..."
              autoSize={{ minRows: 1, maxRows: 4 }}
              disabled={loading}
              style={{ 
                background: 'rgba(26, 26, 26, 0.8)',
                border: '1px solid #404040',
                borderRadius: '12px',
                color: '#ffffff',
                fontSize: '14px',
                padding: '12px 16px',
                resize: 'none'
              }}
              styles={{
                textarea: {
                  background: 'transparent',
                  border: 'none',
                  color: '#ffffff',
                  fontSize: '14px',
                  lineHeight: '1.5'
                }
              }}
            />
          </div>
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSendMessage}
            loading={loading}
            disabled={!inputValue.trim()}
            style={{ 
              height: '48px',
              width: '48px',
              borderRadius: '12px',
              background: inputValue.trim() 
                ? 'linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%)'
                : 'rgba(64, 64, 64, 0.5)',
              border: 'none',
              boxShadow: inputValue.trim() 
                ? '0 4px 12px rgba(0, 212, 170, 0.3)'
                : 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
