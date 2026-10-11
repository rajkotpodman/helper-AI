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
const settingOllamaModel = document.getElementById('setting-ollama-model');
const ollamaDetectedModels = document.getElementById('ollama-detected-models');
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

// Permission Modal Elements (1-Click Human-in-the-Loop)
const permissionModal = document.getElementById('permission-modal');
const permissionDescription = document.getElementById('permission-description');
const permissionDetailsBox = document.getElementById('permission-details-box');
const btnApprovePermission = document.getElementById('btn-approve-permission');
const btnDenyPermission = document.getElementById('btn-deny-permission');
let currentPermissionRequestId = null;

// Memory Modal Elements
const btnOpenMemory = document.getElementById('btn-open-memory');
const memoryModal = document.getElementById('memory-modal');
const btnCloseMemory = document.getElementById('btn-close-memory');
const btnCloseMemoryBtn = document.getElementById('btn-close-memory-btn');
const btnResetMemory = document.getElementById('btn-reset-memory');
const memoryStatSize = document.getElementById('memory-stat-size');
const memoryStatPrompts = document.getElementById('memory-stat-prompts');
const memoryProgressBar = document.getElementById('memory-progress-bar');
const memorySizeBadge = document.getElementById('memory-size-badge');

const memoryAlertModal = document.getElementById('memory-alert-modal');
const btnCloseMemoryAlert = document.getElementById('btn-close-memory-alert');
const btnDismissMemoryAlert = document.getElementById('btn-dismiss-memory-alert');
const btnDownloadMemoryAlert = document.getElementById('btn-download-memory-alert');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  setupWebSocket();
  fetchStatus();
  fetchMemoryStatus();
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

  const btnOpenBrowser = document.getElementById('btn-open-browser');
  if (btnOpenBrowser) {
    btnOpenBrowser.addEventListener('click', async () => {
      try {
        btnOpenBrowser.innerHTML = '<span>⏳ Opening...</span>';
        const res = await fetch('/api/browser/launch', { method: 'POST' });
        const data = await res.json();
        btnOpenBrowser.innerHTML = '<span>🌐 Project Browser</span>';
        alert(data.message || 'Project Browser is open on your screen.');
      } catch (e) {
        btnOpenBrowser.innerHTML = '<span>🌐 Project Browser</span>';
        alert('Failed to launch browser: ' + e.message);
      }
    });
  }

  if (btnOpenMemory) btnOpenMemory.addEventListener('click', handleOpenMemory);
  if (btnCloseMemory) btnCloseMemory.addEventListener('click', () => memoryModal.style.display = 'none');
  if (btnCloseMemoryBtn) btnCloseMemoryBtn.addEventListener('click', () => memoryModal.style.display = 'none');
  if (btnResetMemory) btnResetMemory.addEventListener('click', handleResetMemory);



  if (btnCloseMemoryAlert) btnCloseMemoryAlert.addEventListener('click', () => memoryAlertModal.style.display = 'none');
  if (btnDismissMemoryAlert) btnDismissMemoryAlert.addEventListener('click', () => memoryAlertModal.style.display = 'none');
  if (btnDownloadMemoryAlert) btnDownloadMemoryAlert.addEventListener('click', () => {
    window.location.href = '/api/memory/download';
    memoryAlertModal.style.display = 'none';
  });

  if (btnApprovePermission) btnApprovePermission.addEventListener('click', () => respondPermission(true));
  if (btnDenyPermission) btnDenyPermission.addEventListener('click', () => respondPermission(false));

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
  if (p === 'ollama') {
    fetchOllamaModels();
  }
}

async function fetchOllamaModels() {
  try {
    const res = await fetch('/api/ollama/models');
    if (res.ok) {
      const data = await res.json();
      if (data.models && data.models.length > 0) {
        ollamaDetectedModels.innerHTML = 'Installed models: ' + data.models.map(m => `<span style="text-decoration: underline; cursor: pointer; color: var(--accent); margin-right: 6px;" onclick="document.getElementById('setting-ollama-model').value='${m}'">${m}</span>`).join(' ');
      } else {
        ollamaDetectedModels.innerHTML = 'No models detected yet. Make sure Ollama is installed.';
      }
    }
  } catch (e) {
    console.error('Failed to query ollama models', e);
  }
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
    if (settingOllamaModel && data.ollama_model) {
      settingOllamaModel.value = data.ollama_model;
    }
    if (typeof data.is_running === 'boolean') {
      setRunningState(data.is_running);
    }
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
      stepCounter.textContent = `Step ${data.step} of ${data.max_steps || 50}`;
      break;

    case 'thought':
      createStepCard(data);
      break;

    case 'action_result':
      updateStepCardResult(data);
      break;

    case 'permission_requested':
      currentPermissionRequestId = data.request_id || (data.details && data.details.request_id);
      if (permissionDescription) permissionDescription.textContent = data.description || 'Permission requested for high-risk action';
      if (permissionDetailsBox) {
        permissionDetailsBox.textContent = JSON.stringify(data.details || {}, null, 2);
      }
      if (permissionModal) permissionModal.style.display = 'flex';
      break;

    case 'permission_decided':
      if (permissionModal) permissionModal.style.display = 'none';
      currentPermissionRequestId = null;
      break;

    case 'completed':
    case 'finished':
      if (permissionModal) permissionModal.style.display = 'none';
      setRunningState(false);
      const isSuccess = data.success !== false;
      executionStatusText.textContent = isSuccess ? 'Goal Completed' : 'Goal Execution Halted';
      completionBox.style.display = 'block';
      const titleElem = completionBox.querySelector('h3');
      if (titleElem) {
        titleElem.textContent = isSuccess ? '🎉 Mission Accomplished!' : '⚠️ Goal Execution Incomplete / Limit Reached';
        titleElem.style.color = isSuccess ? '#10b981' : '#f59e0b';
      }
      completionMessage.textContent = data.message || (isSuccess ? 'Execution finished successfully.' : 'Goal was not fully completed before reaching step limit.');
      completionBox.scrollIntoView({ behavior: 'smooth' });
      fetchMemoryStatus();
      break;

    case 'init':
      if (data && typeof data.is_running === 'boolean') {
        setRunningState(data.is_running);
        if (data.is_running && data.current_goal) {
          executionSection.style.display = 'block';
          executionStatusText.textContent = `Helper is executing: "${data.current_goal}"`;
        }
      }
      break;

    case 'memory_limit_reached':
      fetchMemoryStatus();
      if (memoryAlertModal) memoryAlertModal.style.display = 'flex';
      break;

    case 'memory_reset':
      fetchMemoryStatus();
      break;

    case 'cancelled':
      if (permissionModal) permissionModal.style.display = 'none';
      setRunningState(false);
      executionStatusText.textContent = 'Goal Cancelled';
      fetchMemoryStatus();
      break;

    case 'error':
      if (permissionModal) permissionModal.style.display = 'none';
      setRunningState(false);
      alert('Error: ' + data.error);
      break;
  }
}

async function respondPermission(approved) {
  if (!currentPermissionRequestId) {
    // Check if there is an active pending request from backend
    try {
      const res = await fetch('/api/permission/pending');
      const data = await res.json();
      if (data.pending) {
        currentPermissionRequestId = data.pending.request_id;
      }
    } catch (e) {
      console.warn('Failed to fetch pending permission:', e);
    }
  }

  if (!currentPermissionRequestId) {
    if (permissionModal) permissionModal.style.display = 'none';
    return;
  }

  try {
    await fetch('/api/permission/respond', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        request_id: currentPermissionRequestId,
        approved: approved
      })
    });
    if (permissionModal) permissionModal.style.display = 'none';
    currentPermissionRequestId = null;
  } catch (e) {
    console.error('Error responding to permission:', e);
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

  setRunningState(true);
  executionSection.style.display = 'block';
  executionStatusText.textContent = `Helper is executing: "${goal}"`;
  completionBox.style.display = 'none';
  timeline.innerHTML = '';

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
      setRunningState(false);
      alert(data.error || 'Failed to start agent.');
    }
  } catch (e) {
    setRunningState(false);
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
    ollama_model: settingOllamaModel ? (settingOllamaModel.value || null) : null,
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

// Markdown Memory (agent_memory.md) Management
async function fetchMemoryStatus() {
  try {
    const res = await fetch('/api/memory/status');
    const data = await res.json();
    if (memorySizeBadge) memorySizeBadge.textContent = `${data.size_mb} MB`;
    if (memoryStatSize) memoryStatSize.textContent = `${data.size_mb} MB / ${data.limit_mb} MB`;
    if (memoryStatPrompts) memoryStatPrompts.textContent = `${data.total_prompts || 0} recorded prompt${data.total_prompts === 1 ? '' : 's'}`;
    if (memoryProgressBar) {
      const pct = Math.min(100, Math.max(1, (data.size_mb / data.limit_mb) * 100));
      memoryProgressBar.style.width = `${pct}%`;
      if (pct > 90) memoryProgressBar.style.background = '#ef4444';
      else if (pct > 70) memoryProgressBar.style.background = '#f59e0b';
      else memoryProgressBar.style.background = '#3b82f6';
    }
    if (data.is_limit_reached && memoryAlertModal) {
      memoryAlertModal.style.display = 'flex';
    }
  } catch (e) {
    console.error('Failed to fetch memory status:', e);
  }
}

async function handleOpenMemory() {
  await fetchMemoryStatus();
  if (memoryModal) memoryModal.style.display = 'flex';
}

async function handleResetMemory() {
  if (!confirm('Are you sure you want to clear and reset agent_memory.md? All recorded prompts in this file will be wiped.')) return;
  try {
    const res = await fetch('/api/memory/reset', { method: 'POST' });
    if (res.ok) {
      alert('Memory file cleared and reset successfully.');
      await fetchMemoryStatus();
      if (memoryModal) memoryModal.style.display = 'none';
    }
  } catch (e) {
    alert('Failed to reset memory: ' + e.message);
  }
}
