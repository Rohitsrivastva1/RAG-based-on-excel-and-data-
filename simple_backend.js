#!/usr/bin/env node
/**
 * Simple Node.js backend for RAG Analytics
 * This works without Python dependencies
 */

const express = require('express');
const multer = require('multer');
const csv = require('csv-parser');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = 8000;

// Middleware
app.use(cors({
    origin: 'http://localhost:3000',
    credentials: true
}));
app.use(express.json());

// In-memory storage
const sessions = {};
const uploadedFiles = {};

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + '-' + file.originalname);
    }
});

const upload = multer({ storage: storage });

// Create uploads directory if it doesn't exist
if (!fs.existsSync('uploads')) {
    fs.mkdirSync('uploads');
}

// Routes
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        message: 'RAG Analytics API is running',
        timestamp: new Date().toISOString()
    });
});

app.get('/sessions', (req, res) => {
    res.json({ sessions: Object.keys(sessions) });
});

app.post('/upload_excel', upload.single('file'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No file uploaded' });
        }

        const filePath = req.file.path;
        const fileName = req.file.originalname;
        
        // Read CSV file
        const results = [];
        fs.createReadStream(filePath)
            .pipe(csv())
            .on('data', (data) => results.push(data))
            .on('end', () => {
                // Create session
                const sessionId = `session_${Date.now()}`;
                sessions[sessionId] = {
                    type: 'file',
                    filename: fileName,
                    data: results,
                    filePath: filePath
                };

                // Get basic info
                const fileInfo = {
                    filename: fileName,
                    rows: results.length,
                    columns: results.length > 0 ? Object.keys(results[0]).length : 0,
                    column_names: results.length > 0 ? Object.keys(results[0]) : [],
                    sample_data: results.slice(0, 5),
                    data_types: results.length > 0 ? 
                        Object.keys(results[0]).reduce((acc, key) => {
                            acc[key] = typeof results[0][key];
                            return acc;
                        }, {}) : {}
                };

                res.json({
                    message: 'File uploaded successfully',
                    session_id: sessionId,
                    file_info: fileInfo
                });
            })
            .on('error', (error) => {
                console.error('Error reading file:', error);
                res.status(500).json({ error: 'Error reading file' });
            });

    } catch (error) {
        console.error('Upload error:', error);
        res.status(500).json({ error: 'Upload failed' });
    }
});

app.post('/ask_question', (req, res) => {
    try {
        const { question, session_id } = req.body;

        if (!question) {
            return res.status(400).json({ error: 'Question is required' });
        }

        if (!session_id || !sessions[session_id]) {
            return res.status(404).json({ error: 'Session not found' });
        }

        const session = sessions[session_id];
        const data = session.data;

        // Simple response for demo
        const response = {
            question: question,
            answer: `Processed question: "${question}" on dataset with ${data.length} rows and ${data.length > 0 ? Object.keys(data[0]).length : 0} columns`,
            data: {
                summary: {
                    total_rows: data.length,
                    total_columns: data.length > 0 ? Object.keys(data[0]).length : 0,
                    column_names: data.length > 0 ? Object.keys(data[0]) : []
                }
            },
            visualization: {
                type: 'table',
                data: data.slice(0, 10)
            }
        };

        res.json(response);

    } catch (error) {
        console.error('Question processing error:', error);
        res.status(500).json({ error: 'Error processing question' });
    }
});

app.get('/', (req, res) => {
    res.json({ 
        message: 'RAG Analytics API', 
        version: '1.0.0',
        endpoints: [
            'GET /health',
            'GET /sessions',
            'POST /upload_excel',
            'POST /ask_question'
        ]
    });
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Server error:', error);
    res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
    console.log('🚀 Starting Simple RAG Analytics Backend');
    console.log('==========================================');
    console.log(`Backend is running at: http://localhost:${PORT}`);
    console.log(`API docs available at: http://localhost:${PORT}`);
    console.log('Press Ctrl+C to stop the server');
    console.log();
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down server...');
    process.exit(0);
});
