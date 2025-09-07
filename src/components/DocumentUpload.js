import React, { useState } from 'react';
import { Upload, Button, message, Card, Typography, Space, Progress, Input, Tabs } from 'antd';
import { InboxOutlined, UploadOutlined, FileTextOutlined, LinkOutlined } from '@ant-design/icons';

const { Dragger } = Upload;
const { Title, Text } = Typography;
const { TextArea } = Input;
const { TabPane } = Tabs;

const DocumentUpload = ({ onSessionCreated }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [url, setUrl] = useState('');

  const handleDocumentUpload = async (file) => {
    console.log('handleDocumentUpload called with file:', file.name);
    setUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      console.log('Making API call to /upload_document...');
      const response = await fetch('/upload_document', {
        method: 'POST',
        body: formData,
      });
      console.log('API response status:', response.status);

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Create session object
      const sessionData = {
        id: result.session_id,
        data_source_type: 'document',
        data_source_info: {
          filename: file.name,
          file_type: result.document_info.type,
          file_size: result.document_info.size_bytes,
          word_count: result.document_info.word_count,
          pages: result.document_info.pages,
          uploaded_at: new Date().toISOString()
        },
        document_info: result.document_info,
        document_preview: result.document_preview,
        created_at: new Date().toISOString()
      };

      onSessionCreated(sessionData);
      message.success('Document uploaded successfully!');
      
    } catch (error) {
      console.error('Document upload error:', error);
      message.error('Document upload failed: ' + error.message);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleUrlUpload = async () => {
    if (!url.trim()) {
      message.error('Please enter a valid URL');
      return;
    }

    console.log('handleUrlUpload called with URL:', url);
    setUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('url', url);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      console.log('Making API call to /upload_url...');
      const response = await fetch('/upload_url', {
        method: 'POST',
        body: formData,
      });
      console.log('API response status:', response.status);

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Create session object
      const sessionData = {
        id: result.session_id,
        data_source_type: 'url',
        data_source_info: {
          url: url,
          word_count: result.document_info.word_count,
          uploaded_at: new Date().toISOString()
        },
        document_info: result.document_info,
        document_preview: result.document_preview,
        created_at: new Date().toISOString()
      };

      onSessionCreated(sessionData);
      message.success('Website processed successfully!');
      setUrl('');
      
    } catch (error) {
      console.error('URL upload error:', error);
      message.error('URL processing failed: ' + error.message);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const documentUploadProps = {
    name: 'file',
    multiple: false,
    accept: '.pdf,.docx,.md',
    beforeUpload: (file) => {
      console.log('beforeUpload called with file:', file.name, 'type:', file.type);
      // Check file size (50MB limit)
      const isLt50M = file.size / 1024 / 1024 < 50;
      if (!isLt50M) {
        message.error('File must be smaller than 50MB!');
        return false;
      }
      
      // Check file type
      const fileExtension = file.name.toLowerCase().split('.').pop();
      const isValidType = ['pdf', 'docx', 'md'].includes(fileExtension);
      
      if (!isValidType) {
        message.error('Only PDF, DOCX, and MD files are allowed!');
        return false;
      }
      
      // Trigger our custom upload
      console.log('Calling handleDocumentUpload...');
      handleDocumentUpload(file);
      return false; // Prevent auto upload
    },
    onChange: (info) => {
      if (info.file.status === 'uploading') {
        setUploading(true);
        setUploadProgress(0);
      }
    },
  };

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
              <FileTextOutlined style={{ color: '#ffffff', fontSize: '24px' }} />
            </div>
            <div>
              <div style={{ 
                color: '#ffffff', 
                fontSize: '24px', 
                fontWeight: '600',
                margin: 0
              }}>
                Upload Documents & URLs
              </div>
              <div style={{ 
                color: '#8c8c8c', 
                fontSize: '14px',
                margin: 0
              }}>
                PDF, DOCX, Markdown files or website URLs
              </div>
            </div>
          </div>
        </div>

        {/* Tabs for different upload types */}
        <Tabs 
          defaultActiveKey="documents" 
          centered
          style={{ 
            background: 'rgba(45, 45, 45, 0.3)',
            borderRadius: '16px',
            padding: '20px'
          }}
          tabBarStyle={{ 
            background: 'transparent',
            marginBottom: '20px'
          }}
        >
          <TabPane tab="📄 Documents" key="documents">
            {/* Document Upload Area */}
            <div style={{
              background: 'rgba(45, 45, 45, 0.5)',
              borderRadius: '20px',
              border: '2px dashed #404040',
              padding: '60px 40px',
              textAlign: 'center',
              transition: 'all 0.3s ease',
              cursor: 'pointer',
              position: 'relative',
              overflow: 'hidden'
            }}
            onDrop={(e) => {
              e.preventDefault();
              const files = e.dataTransfer.files;
              if (files.length > 0) {
                handleDocumentUpload(files[0]);
              }
            }}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => {
              const input = document.createElement('input');
              input.type = 'file';
              input.accept = '.pdf,.docx,.md';
              input.onchange = (e) => {
                if (e.target.files.length > 0) {
                  handleDocumentUpload(e.target.files[0]);
                }
              };
              input.click();
            }}
            >
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'linear-gradient(135deg, rgba(0, 212, 170, 0.05) 0%, rgba(0, 168, 255, 0.05) 100%)',
                opacity: 0,
                transition: 'opacity 0.3s ease'
              }} />
              
              <div style={{ position: 'relative', zIndex: 1 }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 24px',
                  boxShadow: '0 8px 24px rgba(0, 212, 170, 0.3)'
                }}>
                  <InboxOutlined style={{ color: '#ffffff', fontSize: '36px' }} />
                </div>
                
                <div style={{ 
                  color: '#ffffff', 
                  fontSize: '20px', 
                  fontWeight: '600',
                  marginBottom: '12px'
                }}>
                  Drop your document here or click to browse
                </div>
                
                <div style={{ 
                  color: '#8c8c8c', 
                  fontSize: '14px',
                  marginBottom: '24px'
                }}>
                  Support for PDF, DOCX, and Markdown files
                </div>
                
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  background: 'rgba(0, 212, 170, 0.1)',
                  padding: '8px 16px',
                  borderRadius: '12px',
                  border: '1px solid rgba(0, 212, 170, 0.3)',
                  color: '#00d4aa',
                  fontSize: '12px',
                  fontWeight: '500'
                }}>
                  <UploadOutlined />
                  Choose Document
                </div>
              </div>
            </div>
          </TabPane>

          <TabPane tab="🌐 Website URL" key="url">
            {/* URL Upload Area */}
            <div style={{
              background: 'rgba(45, 45, 45, 0.5)',
              borderRadius: '20px',
              border: '2px dashed #404040',
              padding: '40px',
              textAlign: 'center'
            }}>
              <div style={{
                width: '80px',
                height: '80px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 24px',
                boxShadow: '0 8px 24px rgba(0, 212, 170, 0.3)'
              }}>
                <LinkOutlined style={{ color: '#ffffff', fontSize: '36px' }} />
              </div>
              
              <div style={{ 
                color: '#ffffff', 
                fontSize: '20px', 
                fontWeight: '600',
                marginBottom: '12px'
              }}>
                Enter Website URL
              </div>
              
              <div style={{ 
                color: '#8c8c8c', 
                fontSize: '14px',
                marginBottom: '24px'
              }}>
                We'll extract and analyze the content from any website
              </div>
              
              <Space.Compact style={{ width: '100%', maxWidth: '500px' }}>
                <Input
                  placeholder="https://example.com/article"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onPressEnter={handleUrlUpload}
                  style={{
                    background: 'rgba(45, 45, 45, 0.8)',
                    border: '1px solid #404040',
                    color: '#ffffff',
                    fontSize: '16px',
                    padding: '12px 16px'
                  }}
                />
                <Button 
                  type="primary" 
                  onClick={handleUrlUpload}
                  loading={uploading}
                  style={{
                    background: 'linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%)',
                    border: 'none',
                    height: '40px',
                    padding: '0 24px'
                  }}
                >
                  Process URL
                </Button>
              </Space.Compact>
            </div>
          </TabPane>
        </Tabs>

        {/* Upload Progress */}
        {uploading && (
          <div style={{
            background: 'rgba(45, 45, 45, 0.8)',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid #404040',
            textAlign: 'center'
          }}>
            <div style={{ 
              color: '#00d4aa', 
              fontSize: '16px', 
              fontWeight: '500',
              marginBottom: '16px'
            }}>
              Processing your content...
            </div>
            <Progress 
              percent={uploadProgress} 
              status="active"
              strokeColor={{
                '0%': '#00d4aa',
                '100%': '#00a8ff',
              }}
            />
          </div>
        )}

        {/* Features */}
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
            What you get with Document Analysis
          </div>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px' 
          }}>
            <div style={{
              background: 'rgba(0, 212, 170, 0.1)',
              border: '1px solid rgba(0, 212, 170, 0.3)',
              borderRadius: '12px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>📄</div>
              <div style={{ color: '#00d4aa', fontSize: '14px', fontWeight: '500' }}>
                Multi-Format Support
              </div>
            </div>
            
            <div style={{
              background: 'rgba(0, 212, 170, 0.1)',
              border: '1px solid rgba(0, 212, 170, 0.3)',
              borderRadius: '12px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>🔍</div>
              <div style={{ color: '#00d4aa', fontSize: '14px', fontWeight: '500' }}>
                Semantic Search
              </div>
            </div>
            
            <div style={{
              background: 'rgba(0, 212, 170, 0.1)',
              border: '1px solid rgba(0, 212, 170, 0.3)',
              borderRadius: '12px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>💬</div>
              <div style={{ color: '#00d4aa', fontSize: '14px', fontWeight: '500' }}>
                AI-Powered Q&A
              </div>
            </div>
          </div>
        </div>
      </Space>
    </div>
  );
};

export default DocumentUpload;
