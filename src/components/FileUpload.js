import React, { useState } from 'react';
import { Upload, Button, message, Card, Typography, Space, Progress } from 'antd';
import { InboxOutlined, UploadOutlined, FileExcelOutlined } from '@ant-design/icons';

const { Dragger } = Upload;
const { Title, Text } = Typography;

const FileUpload = ({ onSessionCreated }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleUpload = async (file) => {
    console.log('handleUpload called with file:', file.name);
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

      console.log('Making API call to /upload_excel...');
      const response = await fetch('/upload_excel', {
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
        data_source_type: 'excel',
        data_source_info: {
          filename: file.name,
          file_size: file.size,
          uploaded_at: new Date().toISOString()
        },
        schema_info: result.file_info,
        created_at: new Date().toISOString()
      };

      onSessionCreated(sessionData);
      message.success('File uploaded successfully!');
      
    } catch (error) {
      console.error('Upload error:', error);
      message.error('Upload failed: ' + error.message);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const uploadProps = {
    name: 'file',
    multiple: false,
    accept: '.xlsx,.xls,.csv',
    beforeUpload: (file) => {
      console.log('beforeUpload called with file:', file.name, 'type:', file.type);
      // Check file size (50MB limit)
      const isLt50M = file.size / 1024 / 1024 < 50;
      if (!isLt50M) {
        message.error('File must be smaller than 50MB!');
        return false;
      }
      
      // Check file type
      const isValidType = file.type === 'text/csv' || 
                         file.type === 'application/vnd.ms-excel' ||
                         file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      
      if (!isValidType) {
        message.error('Only Excel and CSV files are allowed!');
        return false;
      }
      
      // Trigger our custom upload
      console.log('Calling handleUpload...');
      handleUpload(file);
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
              <FileExcelOutlined style={{ color: '#ffffff', fontSize: '24px' }} />
            </div>
            <div>
              <div style={{ 
                color: '#ffffff', 
                fontSize: '24px', 
                fontWeight: '600',
                margin: 0
              }}>
                Upload Your Data
              </div>
              <div style={{ 
                color: '#8c8c8c', 
                fontSize: '14px',
                margin: 0
              }}>
                Excel or CSV files up to 50MB
              </div>
            </div>
          </div>
        </div>

        {/* Upload Area */}
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
            handleUpload(files[0]);
          }
        }}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => {
          const input = document.createElement('input');
          input.type = 'file';
          input.accept = '.xlsx,.xls,.csv';
          input.onchange = (e) => {
            if (e.target.files.length > 0) {
              handleUpload(e.target.files[0]);
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
              Drop your file here or click to browse
            </div>
            
            <div style={{ 
              color: '#8c8c8c', 
              fontSize: '14px',
              marginBottom: '24px'
            }}>
              Support for Excel (.xlsx, .xls) and CSV files
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
              Choose File
            </div>
          </div>
        </div>

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
              Uploading your file...
            </div>
            <Progress 
              percent={uploadProgress} 
              status="active"
              strokeColor={{
                '0%': '#00d4aa',
                '100%': '#00a8ff',
              }}
              style={{
                '& .ant-progress-bg': {
                  background: 'linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%)'
                }
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
            What you get with RAG Analytics
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
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>🔍</div>
              <div style={{ color: '#00d4aa', fontSize: '14px', fontWeight: '500' }}>
                Auto Schema Detection
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
                Natural Language Queries
              </div>
            </div>
            
            <div style={{
              background: 'rgba(0, 212, 170, 0.1)',
              border: '1px solid rgba(0, 212, 170, 0.3)',
              borderRadius: '12px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>📊</div>
              <div style={{ color: '#00d4aa', fontSize: '14px', fontWeight: '500' }}>
                Smart Visualizations
              </div>
            </div>
          </div>
        </div>
      </Space>
    </div>
  );
};

export default FileUpload;
