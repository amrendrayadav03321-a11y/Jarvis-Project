/**
 * J.A.R.V.I.S. // STARK INDUSTRIES HOLOGRAPHIC HUD CONTROLLER
 * Canvas Arc Reactor, Audio Visualizer, and Real-Time Telemetry Engine
 */

// Global State
const state = {
    mode: 'standby', // 'standby' | 'listening' | 'processing' | 'speaking'
    cpu: 12,
    ramUsed: 9.8,
    ramTotal: 16.0,
    battery: 85,
    isCharging: false,
    diskFree: 301,
    aiModel: 'Gemini 3.5 Flash',
    lastMessageCount: 0
};

// Canvas references
let reactorCanvas, reactorCtx;
let waveformCanvas, waveformCtx;
let reactorAngle = 0;
let innerAngle = 0;
let pulsePhase = 0;
let wavePhase = 0;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initClock();
    initCanvases();
    initEventListeners();
    startAnimationLoops();
    fetchTelemetry();
    fetchHistory();
    setInterval(fetchTelemetry, 2000);
    setInterval(fetchHistory, 1000);
});

/* ==========================================================================
   1. CLOCK & TELEMETRY TIMERS
   ========================================================================== */

function initClock() {
    function update() {
        const now = new Date();
        const timeStr = now.toTimeString().split(' ')[0];
        const dateStr = now.toLocaleDateString('en-US', { month: 'long', day: '2-digit', year: 'numeric' }).toUpperCase();
        
        document.getElementById('current-time').textContent = timeStr;
        document.getElementById('current-date').textContent = dateStr;
    }
    update();
    setInterval(update, 1000);
}

/* ==========================================================================
   2. CANVAS ARC REACTOR ENGINE (MARK 85)
   ========================================================================== */

function initCanvases() {
    reactorCanvas = document.getElementById('reactor-canvas');
    reactorCtx = reactorCanvas.getContext('2d');
    
    waveformCanvas = document.getElementById('waveform-canvas');
    waveformCtx = waveformCanvas.getContext('2d');
}

function startAnimationLoops() {
    function loop() {
        drawArcReactor();
        drawWaveform();
        requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
}

function drawArcReactor() {
    const ctx = reactorCtx;
    const w = reactorCanvas.width;
    const h = reactorCanvas.height;
    const cx = w / 2;
    const cy = h / 2;

    ctx.clearRect(0, 0, w, h);

    // Speed depends on state
    let rotSpeed = 0.008;
    let mainColor = '#00f0ff';
    let glowColor = 'rgba(0, 240, 255, 0.4)';

    if (state.mode === 'listening') {
        rotSpeed = 0.035;
        mainColor = '#ffaa00';
        glowColor = 'rgba(255, 170, 0, 0.6)';
    } else if (state.mode === 'processing') {
        rotSpeed = 0.05;
        mainColor = '#0088ff';
        glowColor = 'rgba(0, 136, 255, 0.6)';
    } else if (state.mode === 'speaking') {
        rotSpeed = 0.02;
        mainColor = '#00f0ff';
        glowColor = 'rgba(0, 240, 255, 0.7)';
    }

    reactorAngle += rotSpeed;
    innerAngle -= rotSpeed * 1.5;
    pulsePhase += 0.05;

    // 1. OUTSIDE PULSE AURA
    const pulseRadius = 140 + Math.sin(pulsePhase) * 6;
    const gradient = ctx.createRadialGradient(cx, cy, 30, cx, cy, pulseRadius);
    gradient.addColorStop(0, glowColor);
    gradient.addColorStop(0.6, 'rgba(0, 240, 255, 0.08)');
    gradient.addColorStop(1, 'transparent');
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(cx, cy, pulseRadius, 0, Math.PI * 2);
    ctx.fill();

    // 2. OUTER MECHANICAL RING
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(reactorAngle);

    ctx.strokeStyle = mainColor;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(0, 0, 150, 0, Math.PI * 2);
    ctx.stroke();

    // Outer notches
    const notches = 12;
    for (let i = 0; i < notches; i++) {
        const theta = (i * Math.PI * 2) / notches;
        const x1 = Math.cos(theta) * 145;
        const y1 = Math.sin(theta) * 145;
        const x2 = Math.cos(theta) * 155;
        const y2 = Math.sin(theta) * 155;
        
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.lineWidth = 3;
        ctx.strokeStyle = mainColor;
        ctx.stroke();
    }
    ctx.restore();

    // 3. INNER COILS / CHEST SEGMENTS (10 Stark Energy Blocks)
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(innerAngle);

    const coilCount = 10;
    for (let i = 0; i < coilCount; i++) {
        const angle = (i * Math.PI * 2) / coilCount;
        ctx.save();
        ctx.rotate(angle);
        
        // Arc coil trapezoid
        ctx.fillStyle = (i % 2 === 0) ? mainColor : 'rgba(0, 240, 255, 0.7)';
        ctx.shadowColor = mainColor;
        ctx.shadowBlur = 10;
        
        ctx.beginPath();
        ctx.rect(-10, 95, 20, 16);
        ctx.fill();
        ctx.restore();
    }

    // Inner rail circle
    ctx.beginPath();
    ctx.arc(0, 0, 90, 0, Math.PI * 2);
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = mainColor;
    ctx.stroke();
    ctx.restore();

    // 4. INNER TRIANGLE & ENERGY CORE
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(reactorAngle * 0.8);

    ctx.beginPath();
    const triRadius = 60;
    for (let i = 0; i < 3; i++) {
        const a = (i * 2 * Math.PI) / 3 - Math.PI / 2;
        const x = Math.cos(a) * triRadius;
        const y = Math.sin(a) * triRadius;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();

    // 5. CENTER BRIGHT FUSION POINT
    const coreGlow = ctx.createRadialGradient(cx, cy, 0, cx, cy, 38);
    coreGlow.addColorStop(0, '#ffffff');
    coreGlow.addColorStop(0.4, mainColor);
    coreGlow.addColorStop(1, 'transparent');
    
    ctx.fillStyle = coreGlow;
    ctx.beginPath();
    ctx.arc(cx, cy, 38, 0, Math.PI * 2);
    ctx.fill();
}

/* ==========================================================================
   3. AUDIO WAVEFORM OSCILLATOR CANVAS
   ========================================================================== */

function drawWaveform() {
    const ctx = waveformCtx;
    const w = waveformCanvas.width;
    const h = waveformCanvas.height;
    const cy = h / 2;

    ctx.clearRect(0, 0, w, h);

    wavePhase += 0.08;
    const bars = 48;
    const barWidth = 6;
    const spacing = (w - (bars * barWidth)) / (bars - 1);

    let ampMultiplier = 0.25;
    let barColor = '#00f0ff';

    if (state.mode === 'listening') {
        ampMultiplier = 0.85;
        barColor = '#ffaa00';
    } else if (state.mode === 'speaking') {
        ampMultiplier = 1.0;
        barColor = '#00f0ff';
    } else if (state.mode === 'processing') {
        ampMultiplier = 0.5;
        barColor = '#0088ff';
    }

    for (let i = 0; i < bars; i++) {
        const distFromCenter = Math.abs(i - bars / 2) / (bars / 2);
        const envelope = Math.cos(distFromCenter * (Math.PI / 2));
        
        const wave1 = Math.sin(wavePhase + i * 0.35);
        const wave2 = Math.cos(wavePhase * 1.5 + i * 0.2);
        const rawAmp = Math.abs(wave1 * 0.6 + wave2 * 0.4);
        
        const barHeight = Math.max(4, rawAmp * (h * 0.8) * envelope * ampMultiplier);
        const x = i * (barWidth + spacing);
        const y = cy - barHeight / 2;

        ctx.fillStyle = barColor;
        ctx.shadowColor = barColor;
        ctx.shadowBlur = 6;
        
        ctx.beginPath();
        ctx.roundRect(x, y, barWidth, barHeight, 3);
        ctx.fill();
    }
}

/* ==========================================================================
   4. EVENT LISTENERS & USER COMMAND HANDLING
   ========================================================================== */

function initEventListeners() {
    const input = document.getElementById('command-input');
    const sendBtn = document.getElementById('send-btn');
    const micBtn = document.getElementById('mic-toggle-btn');

    sendBtn.addEventListener('click', () => {
        submitCommand();
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            submitCommand();
        }
    });

    micBtn.addEventListener('click', () => {
        triggerManualMic();
    });
}

function submitCommand() {
    const input = document.getElementById('command-input');
    const query = input.value.trim();
    if (!query) return;

    input.value = '';
    sendQueryToServer(query);
}

function sendQuickCommand(cmd) {
    sendQueryToServer(cmd);
}

function triggerManualMic() {
    const micBtn = document.getElementById('mic-toggle-btn');
    micBtn.classList.add('listening');
    setUiState('listening', 'LISTENING // SPEAK YOUR COMMAND NOW');

    fetch('/api/listen', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            micBtn.classList.remove('listening');
            if (data.command) {
                // Refresh log immediately
                fetchHistory();
            }
        })
        .catch(() => {
            micBtn.classList.remove('listening');
            setUiState('standby', 'STANDBY // SAY "HEY JARVIS"');
        });
}

function sendQueryToServer(query) {
    // Add user message to UI immediately for instant feedback
    appendMessage('USER', query);
    setUiState('processing', 'EXECUTING PROTOCOL: ' + query.toUpperCase());

    fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
    })
    .then(res => res.json())
    .then(data => {
        setUiState('speaking', 'TRANSMITTING AUDIO...');
        appendMessage('JARVIS', data.response);
        setTimeout(() => {
            setUiState('standby', 'STANDBY // SAY "HEY JARVIS" TO ACTIVATE');
        }, 3000);
    })
    .catch(err => {
        appendMessage('SYSTEM', 'Execution anomaly: ' + err.message);
        setUiState('standby', 'STANDBY // SAY "HEY JARVIS" TO ACTIVATE');
    });
}

/* ==========================================================================
   5. UI STATE UPDATER & TELEMETRY SYNC
   ========================================================================== */

function setUiState(mode, text) {
    state.mode = mode;
    const banner = document.getElementById('status-banner');
    const bannerText = document.getElementById('status-text');
    const coreStatus = document.getElementById('reactor-status-text');

    bannerText.textContent = text;
    coreStatus.textContent = mode.toUpperCase();

    if (mode === 'listening') {
        banner.style.borderColor = '#ffaa00';
        bannerText.style.color = '#ffaa00';
    } else if (mode === 'processing') {
        banner.style.borderColor = '#0088ff';
        bannerText.style.color = '#0088ff';
    } else {
        banner.style.borderColor = '#00f0ff';
        bannerText.style.color = '#00f0ff';
    }
}

function fetchTelemetry() {
    fetch('/api/status')
        .then(res => res.json())
        .then(data => {
            // Update CPU
            document.getElementById('cpu-value').textContent = data.cpu_percent + '%';
            document.getElementById('cpu-bar').style.width = data.cpu_percent + '%';

            // Update RAM
            document.getElementById('ram-value').textContent = data.ram_percent + '%';
            document.getElementById('ram-bar').style.width = data.ram_percent + '%';
            document.getElementById('ram-detail').textContent = `${data.ram_used_gb} GB / ${data.ram_total_gb} GB`;

            // Update Battery
            document.getElementById('battery-value').textContent = data.battery_percent + '%';
            document.getElementById('battery-bar').style.width = data.battery_percent + '%';
            document.getElementById('battery-status').textContent = data.battery_charging ? '⚡ Power Adapter Connected' : 'Discharging';

            // Update Storage
            document.getElementById('disk-value').textContent = data.disk_free_gb + ' GB Free';

            // Voice state sync if provided
            if (data.voice_state && data.voice_state !== state.mode) {
                if (data.voice_state === 'listening') {
                    setUiState('listening', 'LISTENING // SPEAK YOUR COMMAND NOW');
                } else if (data.voice_state === 'processing') {
                    setUiState('processing', 'PROCESSING COMMAND...');
                } else if (data.voice_state === 'speaking') {
                    setUiState('speaking', 'SPEAKING AUDIO RESPONSE...');
                } else if (data.voice_state === 'standby') {
                    setUiState('standby', 'STANDBY // SAY "HEY JARVIS" TO ACTIVATE');
                }
            }
        })
        .catch(() => {});
}

function fetchHistory() {
    fetch('/api/history')
        .then(res => res.json())
        .then(data => {
            if (!data.messages) return;
            if (data.messages.length > state.lastMessageCount) {
                const feed = document.getElementById('chat-feed');
                feed.innerHTML = '';
                data.messages.forEach(msg => {
                    appendMessage(msg.role, msg.text, msg.time);
                });
                state.lastMessageCount = data.messages.length;
                feed.scrollTop = feed.scrollHeight;
            }
        })
        .catch(() => {});
}

function appendMessage(role, text, timeStr) {
    const feed = document.getElementById('chat-feed');
    const msgDiv = document.createElement('div');
    const nowTime = timeStr || new Date().toTimeString().split(' ')[0];

    if (role.toLowerCase() === 'user') {
        msgDiv.className = 'chat-message msg-user';
        msgDiv.innerHTML = `
            <div class="msg-header">
                <span class="msg-author">👤 COMMAND RECEIVED</span>
                <span class="msg-time">${nowTime}</span>
            </div>
            <div class="msg-body">${escapeHtml(text)}</div>
        `;
    } else if (role.toLowerCase() === 'jarvis') {
        msgDiv.className = 'chat-message msg-jarvis';
        msgDiv.innerHTML = `
            <div class="msg-header">
                <span class="msg-author">◈ J.A.R.V.I.S.</span>
                <span class="msg-time">${nowTime}</span>
            </div>
            <div class="msg-body">${escapeHtml(text)}</div>
        `;
    } else {
        msgDiv.className = 'chat-message msg-tool';
        msgDiv.innerHTML = `
            <div class="msg-header">
                <span class="msg-author">⚡ PROTOCOL EVENT</span>
                <span class="msg-time">${nowTime}</span>
            </div>
            <div class="msg-body">${escapeHtml(text)}</div>
        `;
    }

    feed.appendChild(msgDiv);
    feed.scrollTop = feed.scrollHeight;
}

function escapeHtml(string) {
    const div = document.createElement('div');
    div.textContent = string;
    return div.innerHTML;
}
