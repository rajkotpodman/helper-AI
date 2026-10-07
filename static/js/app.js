let ws = null;
let isRunning = false;

// DOM Elements
const goalInput = document.getElementById('goal-input');
const btnRun = document.getElementById('btn-run');
const btnCancel = document.getElementById('btn-cancel');
const executionSection = document.getElementById('execution-section');
const timeline = document.getElementById('timeline');
const stepCounter = document.getElementById('step-counter');
const executionStatusText = document.getElementById('execution-status-text');
const completionBox = document.getElementById('completion-box');
const completionMessage = document.getElementById('completion-message');
const systemStatus = document.getElementById('system-status');
const systemDot = document.getElementById('system-dot');
const currentProviderLabel = document.getElementById('current-provider-label');
const safeModeLabel = document.getElementById('safe-mode-label');

// Settings Modal Elements
const settingsModal = document.getElementById('settings-modal');
const btnOpenSettings = document.getElementById('btn-open-settings');
const btnCloseSettings = document.getElementById('btn-close-settings');
const btnCancelSettings = document.getElementById('btn-cancel-settings');
const btnSaveSettings = document.getElementById('btn-save-settings');
const settingProvider = document.getElementById('setting-provider');
const settingGeminiKey = document.getElementById('setting-gemini-key');
const settingOpenaiKey = document.getElementById('setting-openai-key');
const settingGroqKey = document.getElementById('setting-groq-key');
const settingOllamaUrl = document.getElementById('setting-ollama-url');
const settingSafeMode = document.getElementById('setting-safe-mode');

// Groups
const groupGemini = document.getElementById('group-gemini');
const groupOpenai = document.getElementById('group-openai');
const groupGroq = document.getElementById('group-groq');
const groupOllama = document.getElementById('group-ollama');

const btnVoice = document.getElementById('btn-voice');
const btnOpenMetrics = document.getElementById('btn-open-metrics');
const btnCloseMetrics = document.getElementById('btn-close-metrics');
const metricsModal = document.getElementById('metrics-modal');
const metricsContent = document.getElementById('metrics-content');
const btnExportMd = document.getElementById('btn-export-md');
const btnExportJson = document.getElementById('btn-export-json');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  setupWebSocket();
  fetchStatus();
  setupEventListeners();
});

function setupEventListeners() {
  btnRun.addEventListener('click', handleRun);
  btnCancel.addEventListener('click', handleCancel);
  btnOpenSettings.addEventListener('click', () => settingsModal.style.display = 'flex');
  btnCloseSettings.addEventListener('click', () => settingsModal.style.display = 'none');
  btnCancelSettings.addEventListener('click', () => settingsModal.style.display = 'none');
  btnSaveSettings.addEventListener('click', handleSaveSettings);

  btnOpenMetrics.addEventListener('click', handleOpenMetrics);
  btnCloseMetrics.addEventListener('click', () => metricsModal.style.display = 'none');
  btnVoice.addEventListener('click', handleVoiceInput);

  if (btnExportMd) btnExportMd.addEventListener('click', () => downloadReport('markdown'));
  if (btnExportJson) btnExportJson.addEventListener('click', () => downloadReport('json'));

  settingProvider.addEventListener('change', updateProviderFormVisibility);

  // Ctrl+Enter to submit goal
  goalInput.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
      handleRun();
    }
  });
}

function updateProviderFormVisibility() {
  const p = settingProvider.value;
  groupGemini.style.display = p === 'gemini' ? 'block' : 'none';
  groupOpenai.style.display = p === 'openai' ? 'block' : 'none';
  groupGroq.style.display = p === 'groq' ? 'block' : 'none';
  groupOllama.style.display = p === 'ollama' ? 'block' : 'none';
}

function setGoal(text) {
  goalInput.value = text;
  goalInput.focus();
}

async function fetchStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    currentProviderLabel.textContent = data.provider.toUpperCase();
    settingProvider.value = data.provider;
    updateProviderFormVisibility();
  } catch (e) {
    console.error('Failed to fetch status:', e);
  }
}

function setupWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    systemStatus.textContent = 'PC Control Online';
    systemDot.style.backgroundColor = 'var(--accent-green)';
  };

  ws.onclose = () => {
    systemStatus.textContent = 'Disconnected';
    systemDot.style.backgroundColor = 'var(--accent-red)';
    setTimeout(setupWebSocket, 3000);
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      handleAgentEvent(msg.event, msg.data);
    } catch (e) {
      console.error('Error parsing WS message:', e);
    }
  };
}

function handleAgentEvent(eventType, data) {
  switch (eventType) {
    case 'started':
      setRunningState(true);
      timeline.innerHTML = '';
      completionBox.style.display = 'none';
      executionSection.style.display = 'block';
      executionStatusText.textContent = `Helper is executing: "${data.goal}"`;
      break;

    case 'step_start':
      stepCounter.textContent = `Step ${data.step} of ${data.max_steps}`;
      break;

    case 'thought':
      createStepCard(data);
      break;

    case 'action_result':
      updateStepCardResult(data);
      break;

    case 'completed':
      setRunningState(false);
      executionStatusText.textContent = 'Goal Finished';
      completionBox.style.display = 'block';
      completionMessage.textContent = data.message;
      completionBox.scrollIntoView({ behavior: 'smooth' });
      break;

    case 'cancelled':
      setRunningState(false);
      executionStatusText.textContent = 'Goal Cancelled';
      break;

    case 'error':
      setRunningState(false);
      alert('Error: ' + data.error);
      break;
  }
}

function setRunningState(running) {
  isRunning = running;
  btnRun.disabled = running;
  btnRun.innerHTML = running ? '<span>⏳ Executing...</span>' : '<span>🚀 Execute Goal</span>';
  btnCancel.style.display = running ? 'inline-block' : 'none';
}

function createStepCard(data) {
  const card = document.createElement('div');
  card.className = 'step-card';
  card.id = `step-${data.step}`;

  const top = document.createElement('div');
  top.className = 'step-top';
  top.innerHTML = `
    <span class="step-number">Step ${data.step}</span>
    <span class="tool-badge">${data.action !== 'none' ? '⚡ ' + data.action : '🏁 Complete'}</span>
  `;

  const thought = document.createElement('div');
  thought.className = 'thought-text';
  thought.textContent = data.thought;

  card.appendChild(top);
  card.appendChild(thought);

  timeline.appendChild(card);
  card.scrollIntoView({ behavior: 'smooth' });
}

function updateStepCardResult(data) {
  const card = document.getElementById(`step-${data.step}`);
  if (!card) return;

  if (data.success) {
    card.classList.add('success');
  } else {
    card.classList.add('failure');
  }

  const term = document.createElement('div');
  term.className = 'result-terminal';
  term.textContent = data.output;

  card.appendChild(term);
}

async function handleRun() {
  const goal = goalInput.value.trim();
  if (!goal) {
    alert('Please enter a goal for Helper.');
    return;
  }

  try {
    const res = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        goal: goal,
        provider: settingProvider.value,
        safe_mode: settingSafeMode.checked
      })
    });
    const data = await res.json();
    if (!res.ok) {
      alert(data.error || 'Failed to start agent.');
    }
  } catch (e) {
    alert('Network error starting agent: ' + e.message);
  }
}

async function handleCancel() {
  try {
    await fetch('/api/cancel', { method: 'POST' });
  } catch (e) {
    console.error('Cancel failed:', e);
  }
}

async function handleSaveSettings() {
  const payload = {
    provider: settingProvider.value,
    gemini_key: settingGeminiKey.value || null,
    openai_key: settingOpenaiKey.value || null,
    groq_key: settingGroqKey.value || null,
    ollama_url: settingOllamaUrl.value || null,
    safe_mode: settingSafeMode.checked
  };

  try {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      settingsModal.style.display = 'none';
      currentProviderLabel.textContent = payload.provider.toUpperCase();
      safeModeLabel.textContent = payload.safe_mode ? 'On (Restricted)' : 'Off (Full Autonomous)';
      alert('Settings saved successfully!');
    }
  } catch (e) {
    alert('Failed to save settings: ' + e.message);
  }
}

// Voice-to-Text via Web Speech API
function handleVoiceInput() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert('Voice input is not supported in this browser. Try Google Chrome or Microsoft Edge.');
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;

  btnVoice.style.borderColor = 'var(--accent-red)';
  btnVoice.innerHTML = '🎙️ <span>Listening...</span>';

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    goalInput.value = transcript;
    goalInput.focus();
  };

  recognition.onerror = (event) => {
    console.error('Speech error:', event.error);
  };

  recognition.onend = () => {
    btnVoice.style.borderColor = '';
    btnVoice.innerHTML = '🎙️ <span>Voice Input</span>';
  };

  recognition.start();
}

// Operational Telemetry Viewer
async function handleOpenMetrics() {
  metricsModal.style.display = 'flex';
  metricsContent.textContent = 'Loading live telemetry...';
  try {
    const res = await fetch('/api/metrics');
    const data = await res.json();
    metricsContent.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    metricsContent.textContent = 'Failed to load telemetry: ' + e.message;
  }
}

// Download Execution Report
async function downloadReport(format) {
  try {
    const res = await fetch(`/api/export?format=${format}`);
    const data = await res.json();
    let content = '';
    let filename = '';
    let mimeType = '';

    if (format === 'markdown') {
      content = data.markdown;
      filename = 'helper_execution_report.md';
      mimeType = 'text/markdown';
    } else {
      content = JSON.stringify(data, null, 2);
      filename = 'helper_execution_history.json';
      mimeType = 'application/json';
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (e) {
    alert('Export failed: ' + e.message);
  }
}
