const express = require('express');
const http = require('http');
const { Server: SocketIOServer } = require('socket.io');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Ensure logs directory exists (store logs inside node_vui/logs for reliability)
const logsDir = path.join(__dirname, 'logs');
try {
    fs.mkdirSync(logsDir, { recursive: true });
} catch (e) {
    // ignore
}

const logFile = path.join(logsDir, 'vui.log');
function logToFile(msg) {
    const line = `[${new Date().toISOString()}] ${msg}\n`;
    try {
        fs.appendFileSync(logFile, line, { encoding: 'utf8' });
    } catch (e) {
        console.error('Failed to write log:', e.message || e);
    }
}

const app = express();
const server = http.createServer(app);
// Configure Socket.IO with CORS and transports explicitly to support websocket clients
const io = new SocketIOServer(server, {
    cors: { origin: '*', methods: ['GET', 'POST'] },
    transports: ['websocket', 'polling']
});

app.use(express.static('public'));

io.on('connection', (socket) => {
    console.log('User connected to Voice UI:', socket.id);
    logToFile(`connect ${socket.id}`);

    socket.on('voice-data', async (text) => {
        console.log(`[${socket.id}] Received voice text: "${text}"`);
        logToFile(`${socket.id} RECEIVED: ${text}`);
        
        try {
            console.log(`[${socket.id}] Forwarding to Python Brain...`);
            logToFile(`${socket.id} FORWARDING to Python Brain`);
            // Notify client that processing has started
            socket.emit('maya-status', { status: 'processing' });
            const response = await axios.post('http://127.0.0.1:5001/process', { text }, {
                timeout: 120000 // allow up to 120s for complex procedures
            });
            
            // Validate and extract reply text
            // Prefer the brain's Hinglish reply field if present
            const replyRaw = (response && response.data && (typeof response.data.hinglish === 'string')) ? response.data.hinglish :
                             (response && response.data && (typeof response.data.reply === 'string')) ? response.data.reply : String(response && response.data ? response.data : '') || '';

            // Sanitize reply to keep VUI concise (strip owner mentions, collapse lines)
            function cleanReply(text) {
                if (!text) return '';
                // Normalize whitespace first
                text = String(text).replace(/\r\n|\r|\n/g, ' ');

                // Remove owner/creator mentions and common variants
                const ownerPatterns = [/Abhay Kumar Rudrapaul/ig, /Abhay\b/ig, /meri creator/ig, /my creator/ig];
                for (const p of ownerPatterns) text = text.replace(p, '');

                // Remove common salutations at start
                text = text.replace(/^(Bilkul|Namaste|Hello|Hi|Hey|Mujhe|Main)[,!\s]*/i, '');

                // Collapse extra whitespace
                text = text.replace(/\s+/g, ' ').trim();

                // Keep only first 2 sentences or 400 chars for brevity
                const parts = text.split(/(?<=[.!?])\s+/);
                let short = parts.slice(0, 2).join(' ');
                if (short.length > 400) short = short.slice(0, 397) + '...';

                return short.trim();
            }

            let cleaned = cleanReply(replyRaw);

            // Basic grammar / spelling normalization
            function fixGrammar(text) {
                if (!text) return '';
                // normalize common transliteration/casing errors
                const replacements = [
                    [/\bbHi\b/ig, 'bhi'],
                    [/\bBHi\b/ig, 'bhi'],
                    [/\bnaHi\b/ig, 'nahi'],
                    [/\bNaHi\b/ig, 'nahi'],
                    [/\bsaHi\b/ig, 'sahi'],
                    [/\bSaHi\b/ig, 'sahi'],
                    [/\bmulayam\b/ig, 'multiply'],
                    [/\bJawaab hai:?\b/ig, 'Jawaab: '],
                    [/\bToh,?\s*jawaab\s*hai:?/ig, 'Jawaab: '],
                    [/\bUttar\s*hai\s*yah:?/ig, 'Uttar: '],
                    [/\baur\s+bhi\b/ig, 'aur bhi']
                ];

                for (const [pat, repl] of replacements) {
                    try { text = text.replace(pat, repl); } catch (e) {}
                }

                // remove creator mentions more aggressively
                try { text = text.replace(/(Abhay\s*Kumar\s*Rudrapaul|Abhay|meri\s+creator|my\s+creator)/ig, ''); } catch (e) {}

                // unify whitespace and punctuation
                text = text.replace(/[\t\r\n]+/g, ' ');
                text = text.replace(/\s+([,.!?;:])/g, '$1');
                text = text.replace(/\s{2,}/g, ' ');

                // correct common Hindi-English mixed tokens
                try {
                    text = text.replace(/\bKi\b/ig, 'ki');
                    text = text.replace(/\bMain\b/ig, 'main');
                    text = text.replace(/\bMaine\b/ig, 'maine');
                    text = text.replace(/\bKya\b/ig, 'kya');
                } catch (e) {}

                // Balance parentheses/brackets (simple): remove unmatched trailing opens
                try {
                    const opens = (text.match(/[\(\[]/g) || []).length;
                    const closes = (text.match(/[\)\]]/g) || []).length;
                    if (opens > closes) {
                        text += ')'.repeat(opens - closes);
                    }
                } catch (e) {}

                // If this looks like code (def/class/import/return or code-style), preserve casing
                const codePattern = /^(def\s+|class\s+|import\s+|from\s+|\t|\s{4}|\{|\}|return\s+|=>|console\.log\(|function\s+)/i;
                if (!codePattern.test(text) && text.length < 2000) {
                    // Sentence-case each sentence
                    const parts = text.split(/(?<=[.!?])\s+/);
                    for (let i = 0; i < parts.length; i++) {
                        const p = parts[i].trim();
                        if (!p) continue;
                        parts[i] = p.charAt(0).toUpperCase() + p.slice(1);
                    }
                    text = parts.join(' ');
                }

                // collapse duplicate colons/spacing
                try { text = text.replace(/:{2,}/g, ':'); } catch (e) {}
                try { text = text.replace(/:\s*:/g, ':'); } catch (e) {}

                // If this is recognized as code, ensure leading 'Def' is lowercased to 'def'
                if (codePattern.test(text)) {
                    try { text = text.replace(/^[\s\n]*(Def|DEF)\b/, 'def'); } catch (e) {}
                }

                // ensure ends with punctuation for natural replies (not code)
                if (!codePattern.test(text) && text && !/[.!?]$/.test(text)) text = text + '.';
                return text.trim();
            }

            cleaned = fixGrammar(cleaned);
            logToFile(`${socket.id} REPLY: ${cleaned}`);
            // send final reply and a done status to client
            socket.emit('maya-reply', cleaned);
            socket.emit('maya-status', { status: 'done' });
        } catch (error) {
            console.error(`[${socket.id}] Brain Error:`, error.message);
            logToFile(`${socket.id} BRAIN_ERROR: ${error.message}`);
            socket.emit('maya-status', { status: 'error', error: error.message });
            if (error.code === 'ECONNREFUSED') {
                socket.emit('maya-reply', 'Bhai, lagta hai mera dimaag (Python server) band hai. Please check kijiye.');
            } else {
                socket.emit('maya-reply', 'Sorry bhai, kuch technical error aa gaya hai.');
            }
        }
    });

    socket.on('disconnect', () => {
        console.log('User disconnected:', socket.id);
        logToFile(`disconnect ${socket.id}`);
    });
});

server.listen(3000, () => {
    console.log('Node.js VUI running at http://localhost:3000');
});
