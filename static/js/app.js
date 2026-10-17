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
const settingDeepseekKey = document.getElementById('setting-deepseek-key');
const settingCustomName = document.getElementById('setting-custom-name');
const settingCustomUrl = document.getElementById('setting-custom-url');
const settingCustomKey = document.getElementById('setting-custom-key');
const settingCustomModel = document.getElementById('setting-custom-model');
const settingOpenaiKey = document.getElementById('setting-openai-key');
const settingGroqKey = document.getElementById('setting-groq-key');
const settingOllamaUrl = document.getElementById('setting-ollama-url');
const settingOllamaModel = document.getElementById('setting-ollama-model');
const ollamaDetectedModels = document.getElementById('ollama-detected-models');
const settingSafeMode = document.getElementById('setting-safe-mode');

// Groups
const groupGemini = document.getElementById('group-gemini');
const groupDeepseek = document.getElementById('group-deepseek');
const groupCustom = document.getElementById('group-custom');
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

// Language & Universal Google Translate Elements
const btnLangToggle = document.getElementById('btn-lang-toggle');
const langDropdown = document.getElementById('lang-dropdown');
const langSearchInput = document.getElementById('lang-search-input');
const langList = document.getElementById('lang-list');
const currentLangLabel = document.getElementById('current-lang-label');
let currentAppLanguage = localStorage.getItem('helper_language') || 'en';
let currentAppLanguageName = localStorage.getItem('helper_language_name') || 'English';
let allLanguages = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  setupWebSocket();
  fetchStatus();
  fetchMemoryStatus();
  setupEventListeners();
  initLanguageSystem();
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
  if (groupDeepseek) groupDeepseek.style.display = p === 'deepseek' ? 'block' : 'none';
  if (groupCustom) groupCustom.style.display = p === 'custom' ? 'block' : 'none';
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
    case 'init':
      if (data && !data.is_running && isRunning) {
        setRunningState(false);
        fetchStatus();
      }
      break;

    case 'started':
      setRunningState(true);
      timeline.innerHTML = '';
      completionBox.style.display = 'none';
      executionSection.style.display = 'block';
      const execMsg = `Helper is executing: "${data.goal}"`;
      executionStatusText.textContent = execMsg;
      if (currentAppLanguage !== 'en') {
        translateText(execMsg, currentAppLanguage).then(t => { executionStatusText.textContent = t; });
      }
      break;

    case 'step_start':
      const stepTxt = `Step ${data.step} of ${data.max_steps || 50}`;
      stepCounter.textContent = stepTxt;
      if (currentAppLanguage !== 'en') {
        translateText(stepTxt, currentAppLanguage).then(t => { stepCounter.textContent = t; });
      }
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
      const statusTitle = isSuccess ? 'Goal Completed' : 'Goal Execution Halted';
      executionStatusText.textContent = statusTitle;
      if (currentAppLanguage !== 'en') {
        translateText(statusTitle, currentAppLanguage).then(t => { executionStatusText.textContent = t; });
      }
      completionBox.style.display = 'block';
      const titleElem = completionBox.querySelector('h3');
      if (titleElem) {
        const rawTitle = isSuccess ? '🎉 Mission Accomplished!' : '⚠️ Goal Execution Incomplete / Limit Reached';
        titleElem.textContent = rawTitle;
        titleElem.style.color = isSuccess ? '#10b981' : '#f59e0b';
        if (currentAppLanguage !== 'en') {
          translateText(rawTitle, currentAppLanguage).then(t => { titleElem.textContent = t; });
        }
      }
      const rawMsg = data.message || (isSuccess ? 'Execution finished successfully.' : 'Goal was not fully completed before reaching step limit.');
      completionMessage.textContent = rawMsg;
      completionBox.dataset.originalMessage = rawMsg;
      if (currentAppLanguage !== 'en') {
        translateText(rawMsg, currentAppLanguage).then(t => { completionMessage.textContent = t; });
      }
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
  card.dataset.originalThought = data.thought || '';
  card.dataset.stepNumber = data.step;

  const top = document.createElement('div');
  top.className = 'step-top';
  const stepLabel = `Step ${data.step}`;
  const toolBadge = data.action !== 'none' ? '⚡ ' + data.action : '🏁 Complete';
  top.innerHTML = `
    <span class="step-number">${stepLabel}</span>
    <span class="tool-badge">${toolBadge}</span>
  `;

  const thought = document.createElement('div');
  thought.className = 'thought-text';
  thought.textContent = data.thought;

  card.appendChild(top);
  card.appendChild(thought);

  timeline.appendChild(card);
  card.scrollIntoView({ behavior: 'smooth' });

  if (currentAppLanguage !== 'en' && data.thought) {
    translateText(data.thought, currentAppLanguage).then(t => {
      thought.textContent = t;
    });
    translateText(stepLabel, currentAppLanguage).then(t => {
      const numElem = top.querySelector('.step-number');
      if (numElem) numElem.textContent = t;
    });
  }
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
    deepseek_key: settingDeepseekKey ? (settingDeepseekKey.value || null) : null,
    custom_name: settingCustomName ? (settingCustomName.value || null) : null,
    custom_url: settingCustomUrl ? (settingCustomUrl.value || null) : null,
    custom_key: settingCustomKey ? (settingCustomKey.value || null) : null,
    custom_model: settingCustomModel ? (settingCustomModel.value || null) : null,
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

// ==========================================
// UNIVERSAL GOOGLE TRANSLATE & AI REPLAY
// ==========================================

const UI_TRANSLATIONS = {
  en: {
    system_ready: "System Ready",
    pc_online: "PC Control Online",
    disconnected: "Disconnected",
    project_browser: "Project Browser",
    memory: "Memory",
    metrics: "Metrics",
    settings: "Settings",
    goal_prompt: "🎯 What goal would you like Helper to achieve?",
    voice_input: "Voice Input",
    goal_placeholder: "Example: give me the list of my google blogs, or research AI models and write a report to my Desktop...",
    quick_ideas: "Quick Ideas:",
    safe_mode: "Safe Mode:",
    provider: "Provider:",
    stop_agent: "⏹ Stop Agent",
    execute_goal: "🚀 Execute Goal",
    executing_prefix: "Helper is working autonomously on your goal...",
    mission_accomplished: "🎉 Mission Accomplished!",
    exec_halted: "⚠️ Goal Execution Incomplete / Limit Reached",
    download_md: "Download Markdown Report",
    download_json: "Download JSON History",
    auth_req: "Authorization Request",
    deny: "✕ Deny Action",
    approve: "✓ One-Click Approve",
    save_settings: "Save Settings",
    cancel: "Cancel"
  },
  gu: {
    system_ready: "સિસ્ટમ તૈયાર",
    pc_online: "પીસી કંટ્રોલ ઓનલાઇન",
    disconnected: "ડિસ્કનેક્ટ થયું",
    project_browser: "પ્રોજેક્ટ બ્રાઉઝર",
    memory: "મેમરી",
    metrics: "મેટ્રિક્સ",
    settings: "સેટિંગ્સ",
    goal_prompt: "🎯 તમે હેલ્પર પાસે શું કામ કરાવવા માંગો છો?",
    voice_input: "અવાજ ઇનપુટ",
    goal_placeholder: "ઉદાહરણ: મારા ગૂગલ બ્લોગ્સની યાદી આપો, અથવા AI મોડલ્સ પર રિસર્ચ કરીને ડેસ્કટોપ પર રિપોર્ટ લખો...",
    quick_ideas: "ઝડપી વિચારો:",
    safe_mode: "સુરક્ષિત મોડ:",
    provider: "પ્રદાતા:",
    stop_agent: "⏹ એજન્ટ અટકાવો",
    execute_goal: "🚀 લક્ષ્ય ચલાવો",
    executing_prefix: "હેલ્પર તમારા લક્ષ્ય પર સ્વાયત્ત રીતે કામ કરી રહ્યો છે...",
    mission_accomplished: "🎉 કાર્ય સફળતાપૂર્વક પૂર્ણ થયું!",
    exec_halted: "⚠️ કાર્ય અધૂરું રહ્યું / મર્યાદા પહોંચી ગઈ",
    download_md: "માર્કડાઉન રિપોર્ટ ડાઉનલોડ કરો",
    download_json: "JSON ઇતિહાસ ડાઉનલોડ કરો",
    auth_req: "મંજૂરી વિનંતી",
    deny: "✕ અસ્વીકાર",
    approve: "✓ ૧-ક્લિક મંજૂરી",
    save_settings: "સેટિંગ્સ સાચવો",
    cancel: "રદ કરો"
  },
  hi: {
    system_ready: "सिस्टम तैयार",
    pc_online: "पीसी नियंत्रण ऑनलाइन",
    disconnected: "डिस्कनेक्ट हो गया",
    project_browser: "प्रोजेक्ट ब्राउज़र",
    memory: "मेमोरी",
    metrics: "मेट्रिक्स",
    settings: "सेटिंग्स",
    goal_prompt: "🎯 आप हेल्पर से क्या कार्य करवाना चाहते हैं?",
    voice_input: "वॉयस इनपुट",
    goal_placeholder: "उदाहरण: मेरे गूगल ब्लॉग्स की सूची दें, या AI मॉडल पर शोध करके डेस्कटॉप पर रिपोर्ट लिखें...",
    quick_ideas: "त्वरित विचार:",
    safe_mode: "सुरक्षित मोड:",
    provider: "प्रदाता:",
    stop_agent: "⏹ एजेंट रोकें",
    execute_goal: "🚀 लक्ष्य शुरू करें",
    executing_prefix: "हेल्पर आपके लक्ष्य पर स्वायत्त रूप से काम कर रहा है...",
    mission_accomplished: "🎉 मिशन सफलतापूर्वक पूरा हुआ!",
    exec_halted: "⚠️ कार्य अधूरा रहा / सीमा समाप्त",
    download_md: "मार्कडाउन रिपोर्ट डाउनलोड करें",
    download_json: "JSON इतिहास डाउनलोड करें",
    auth_req: "अनुमति अनुरोध",
    deny: "✕ अस्वीकार करें",
    approve: "✓ १-क्लिक अनुमोदन",
    save_settings: "सेटिंग्स सहेजें",
    cancel: "रद्द करें"
  },
  es: {
    system_ready: "Sistema listo",
    pc_online: "Control de PC en línea",
    disconnected: "Desconectado",
    project_browser: "Navegador del proyecto",
    memory: "Memoria",
    metrics: "Métricas",
    settings: "Configuración",
    goal_prompt: "🎯 ¿Qué objetivo te gustaría que Helper logre?",
    voice_input: "Entrada de voz",
    goal_placeholder: "Ejemplo: dame la lista de mis blogs de Google o investiga modelos de IA...",
    quick_ideas: "Ideas rápidas:",
    safe_mode: "Modo seguro:",
    provider: "Proveedor:",
    stop_agent: "⏹ Detener agente",
    execute_goal: "🚀 Ejecutar objetivo",
    executing_prefix: "Helper está trabajando de forma autónoma en tu objetivo...",
    mission_accomplished: "🎉 ¡Misión cumplida!",
    exec_halted: "⚠️ Ejecución incompleta",
    download_md: "Descargar informe Markdown",
    download_json: "Descargar historial JSON",
    auth_req: "Solicitud de autorización",
    deny: "✕ Denegar acción",
    approve: "✓ Aprobación en 1 clic",
    save_settings: "Guardar configuración",
    cancel: "Cancelar"
  },
  fr: {
    system_ready: "Système prêt",
    pc_online: "Contrôle PC en ligne",
    disconnected: "Déconnecté",
    project_browser: "Navigateur du projet",
    memory: "Mémoire",
    metrics: "Métriques",
    settings: "Paramètres",
    goal_prompt: "🎯 Quel objectif souhaitez-vous que Helper atteigne ?",
    voice_input: "Entrée vocale",
    goal_placeholder: "Exemple: donnez-moi la liste de mes blogs Google ou recherchez des modèles IA...",
    quick_ideas: "Idées rapides:",
    safe_mode: "Mode sécurisé:",
    provider: "Fournisseur:",
    stop_agent: "⏹ Arrêter l'agent",
    execute_goal: "🚀 Exécuter l'objectif",
    executing_prefix: "Helper travaille de manière autonome sur votre objectif...",
    mission_accomplished: "🎉 Mission accomplie !",
    exec_halted: "⚠️ Exécution incomplète",
    download_md: "Télécharger le rapport Markdown",
    download_json: "Télécharger l'historique JSON",
    auth_req: "Demande d'autorisation",
    deny: "✕ Refuser l'action",
    approve: "✓ Approuver en 1 clic",
    save_settings: "Enregistrer les paramètres",
    cancel: "Annuler"
  },
  de: {
    system_ready: "System bereit",
    pc_online: "PC-Steuerung online",
    disconnected: "Getrennt",
    project_browser: "Projekt-Browser",
    memory: "Speicher",
    metrics: "Metriken",
    settings: "Einstellungen",
    goal_prompt: "🎯 Welches Ziel soll Helper erreichen?",
    voice_input: "Spracheingabe",
    goal_placeholder: "Beispiel: Gib mir die Liste meiner Google-Blogs oder recherchiere KI-Modelle...",
    quick_ideas: "Schnelle Ideen:",
    safe_mode: "Sicherer Modus:",
    provider: "Anbieter:",
    stop_agent: "⏹ Agent stoppen",
    execute_goal: "🚀 Ziel ausführen",
    executing_prefix: "Helper arbeitet autonom an Ihrem Ziel...",
    mission_accomplished: "🎉 Mission erfüllt!",
    exec_halted: "⚠️ Ausführung unvollständig",
    download_md: "Markdown-Bericht herunterladen",
    download_json: "JSON-Verlauf herunterladen",
    auth_req: "Autorisierungsanfrage",
    deny: "✕ Aktion ablehnen",
    approve: "✓ 1-Klick genehmigen",
    save_settings: "Einstellungen speichern",
    cancel: "Abbrechen"
  }
};

async function initLanguageSystem() {
  if (currentLangLabel) {
    currentLangLabel.textContent = currentAppLanguageName;
  }

  // Load language list from backend
  try {
    const res = await fetch('/api/translate/languages');
    const data = await res.json();
    if (data.languages && Array.isArray(data.languages)) {
      allLanguages = data.languages;
      renderLanguageList(allLanguages);
    }
  } catch (e) {
    console.warn('Failed to fetch languages list:', e);
  }

  // Toggle Dropdown
  if (btnLangToggle && langDropdown) {
    btnLangToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const isVisible = langDropdown.style.display === 'flex';
      langDropdown.style.display = isVisible ? 'none' : 'flex';
      if (!isVisible && langSearchInput) {
        langSearchInput.value = '';
        renderLanguageList(allLanguages);
        setTimeout(() => langSearchInput.focus(), 50);
      }
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.lang-selector-container')) {
        langDropdown.style.display = 'none';
      }
    });
  }

  // Filter search
  if (langSearchInput) {
    langSearchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      const filtered = allLanguages.filter(l => 
        l.name.toLowerCase().includes(q) || 
        l.native.toLowerCase().includes(q) || 
        l.code.toLowerCase().includes(q)
      );
      renderLanguageList(filtered);
    });
  }

  // Apply current active language immediately
  if (currentAppLanguage && currentAppLanguage !== 'en') {
    applyAppLanguage(currentAppLanguage, currentAppLanguageName);
  }
}

function renderLanguageList(list) {
  if (!langList) return;
  langList.innerHTML = '';

  list.forEach(l => {
    const item = document.createElement('div');
    item.className = 'lang-item' + (l.code === currentAppLanguage ? ' active' : '');
    item.innerHTML = `
      <span>${l.name}</span>
      <span class="lang-native-name">${l.native}</span>
    `;
    item.addEventListener('click', () => {
      selectLanguage(l.code, l.name);
      if (langDropdown) langDropdown.style.display = 'none';
    });
    langList.appendChild(item);
  });
}

function selectLanguage(langCode, langName) {
  currentAppLanguage = langCode;
  currentAppLanguageName = langName;
  localStorage.setItem('helper_language', langCode);
  localStorage.setItem('helper_language_name', langName);

  if (currentLangLabel) {
    currentLangLabel.textContent = langName;
  }

  // Update active state in list
  renderLanguageList(allLanguages);

  // Set Google Translate cookie
  setGoogleTranslateCookie(langCode);

  // Trigger Google Translate widget if available
  triggerGoogleTranslateWidget(langCode);

  // Apply UI translations & translate live AI reply / timeline
  applyAppLanguage(langCode, langName);
}

function setGoogleTranslateCookie(langCode) {
  const cookieValue = `/en/${langCode}`;
  document.cookie = `googtrans=${cookieValue}; path=/;`;
  try {
    document.cookie = `googtrans=${cookieValue}; path=/; domain=${window.location.hostname};`;
  } catch (e) {}
}

function triggerGoogleTranslateWidget(langCode) {
  const gtCombo = document.querySelector('.goog-te-combo');
  if (gtCombo) {
    gtCombo.value = langCode;
    gtCombo.dispatchEvent(new Event('change'));
  }
}

async function translateText(text, targetLang) {
  if (!text || !text.trim() || targetLang === 'en') return text;
  try {
    const res = await fetch('/api/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text, target_lang: targetLang })
    });
    const data = await res.json();
    return data.translated_text || text;
  } catch (e) {
    console.debug('Translate text call failed:', e);
    return text;
  }
}

async function applyAppLanguage(langCode, langName) {
  const dict = UI_TRANSLATIONS[langCode];

  // 1. Instant dictionary translation for top languages
  if (dict) {
    const goalLabel = document.querySelector('#goal-card label');
    if (goalLabel) goalLabel.textContent = dict.goal_prompt;
    if (goalInput) goalInput.placeholder = dict.goal_placeholder;
    const btnVoiceSpan = btnVoice ? btnVoice.querySelector('span') : null;
    if (btnVoiceSpan) btnVoiceSpan.textContent = dict.voice_input;
    const quickSpan = document.querySelector('.quick-prompts > span');
    if (quickSpan) quickSpan.textContent = dict.quick_ideas;
    if (btnCancel) btnCancel.textContent = dict.stop_agent;
    const btnRunSpan = btnRun ? btnRun.querySelector('span') : null;
    if (btnRunSpan && !isRunning) btnRunSpan.textContent = dict.execute_goal;

    // Header buttons
    const browserSpan = document.querySelector('#btn-open-browser span');
    if (browserSpan) browserSpan.textContent = dict.project_browser;
    const metricsSpan = document.querySelector('#btn-open-metrics span');
    if (metricsSpan) metricsSpan.textContent = dict.metrics;
    const settingsSpan = document.querySelector('#btn-open-settings span');
    if (settingsSpan) settingsSpan.textContent = dict.settings;

    // Mission accomplished box
    const complTitle = completionBox ? completionBox.querySelector('h3') : null;
    if (complTitle) complTitle.textContent = dict.mission_accomplished;
    const exportMdSpan = document.querySelector('#btn-export-md span');
    if (exportMdSpan) exportMdSpan.textContent = dict.download_md;
    const exportJsonSpan = document.querySelector('#btn-export-json span');
    if (exportJsonSpan) exportJsonSpan.textContent = dict.download_json;
  } else if (langCode !== 'en') {
    // 2. Dynamic translation for any other Google Translate language
    const goalLabel = document.querySelector('#goal-card label');
    if (goalLabel) translateText("🎯 What goal would you like Helper to achieve?", langCode).then(t => goalLabel.textContent = t);
    if (goalInput) translateText("Example: give me the list of my google blogs, or research AI models and write a report to my Desktop...", langCode).then(t => goalInput.placeholder = t);
    const btnVoiceSpan = btnVoice ? btnVoice.querySelector('span') : null;
    if (btnVoiceSpan) translateText("Voice Input", langCode).then(t => btnVoiceSpan.textContent = t);
    const quickSpan = document.querySelector('.quick-prompts > span');
    if (quickSpan) translateText("Quick Ideas:", langCode).then(t => quickSpan.textContent = t);
  }

  // 3. Translate existing timeline step cards
  translateExistingCards(langCode);

  // 4. Translate completion message if present
  if (completionBox && completionBox.style.display !== 'none') {
    const rawMsg = completionBox.dataset.originalMessage || completionMessage.textContent;
    if (rawMsg) {
      translateText(rawMsg, langCode).then(t => {
        completionMessage.textContent = t;
      });
    }
  }
}

function translateExistingCards(targetLang) {
  const cards = document.querySelectorAll('.step-card');
  cards.forEach(card => {
    const rawThought = card.dataset.originalThought;
    const thoughtElem = card.querySelector('.thought-text');
    const stepNumber = card.dataset.stepNumber || '1';
    const numElem = card.querySelector('.step-number');

    if (targetLang === 'en') {
      if (thoughtElem && rawThought) thoughtElem.textContent = rawThought;
      if (numElem) numElem.textContent = `Step ${stepNumber}`;
    } else {
      if (thoughtElem && rawThought) {
        translateText(rawThought, targetLang).then(t => {
          thoughtElem.textContent = t;
        });
      }
      if (numElem) {
        translateText(`Step ${stepNumber}`, targetLang).then(t => {
          numElem.textContent = t;
        });
      }
    }
  });
}

