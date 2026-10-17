/**
 * Helper-AI • Cyber Glassmorphic Frontend Application Engine
 * Autonomous PC Control & Internet Agent
 */

// --- 1. Language Definitions (Google Translate 130+ Languages) ---
let GOOGLE_LANGUAGES = [
  { code: 'en', name: 'English', native: 'English' },
  { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
  { code: 'mr', name: 'Marathi', native: 'मराठी' },
  { code: 'bn', name: 'Bengali', native: 'বাংলা' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்' },
  { code: 'te', name: 'Telugu', native: 'తెలుగు' },
  { code: 'ur', name: 'Urdu', native: 'اردو' },
  { code: 'pa', name: 'Punjabi', native: 'ਪੰਜਾਬੀ' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ' },
  { code: 'ml', name: 'Malayalam', native: 'മലയാളം' },
  { code: 'or', name: 'Odia', native: 'ଓଡ଼ିଆ' },
  { code: 'as', name: 'Assamese', native: 'অসমীয়া' },
  { code: 'bho', name: 'Bhojpuri', native: 'भोजपुरी' },
  { code: 'mai', name: 'Maithili', native: 'मैथिली' },
  { code: 'gom', name: 'Konkani', native: 'कोंकणी' },
  { code: 'sa', name: 'Sanskrit', native: 'संस्कृतम्' },
  { code: 'doi', name: 'Dogri', native: 'डोगरी' },
  { code: 'mni-Mtei', name: 'Meiteilon (Manipuri)', native: 'মৈতৈলোন্' },
  { code: 'lus', name: 'Mizo', native: 'Mizo ṭawng' },
  { code: 'ne', name: 'Nepali', native: 'नेपाली' },
  { code: 'si', name: 'Sinhala', native: 'සිංහල' },
  { code: 'es', name: 'Spanish', native: 'Español' },
  { code: 'fr', name: 'French', native: 'Français' },
  { code: 'de', name: 'German', native: 'Deutsch' },
  { code: 'zh-CN', name: 'Chinese (Simplified)', native: '简体中文' },
  { code: 'zh-TW', name: 'Chinese (Traditional)', native: '繁體中文' },
  { code: 'ja', name: 'Japanese', native: '日本語' },
  { code: 'ko', name: 'Korean', native: '한국어' },
  { code: 'ru', name: 'Russian', native: 'Русский' },
  { code: 'pt', name: 'Portuguese', native: 'Português' },
  { code: 'it', name: 'Italian', native: 'Italiano' },
  { code: 'ar', name: 'Arabic', native: 'العربية' },
  { code: 'nl', name: 'Dutch', native: 'Nederlands' },
  { code: 'tr', name: 'Turkish', native: 'Türkçe' },
  { code: 'pl', name: 'Polish', native: 'Polski' },
  { code: 'vi', name: 'Vietnamese', native: 'Tiếng Việt' },
  { code: 'th', name: 'Thai', native: 'ไทย' },
  { code: 'id', name: 'Indonesian', native: 'Bahasa Indonesia' },
  { code: 'ms', name: 'Malay', native: 'Bahasa Melayu' },
  { code: 'fil', name: 'Filipino', native: 'Filipino' },
  { code: 'sv', name: 'Swedish', native: 'Svenska' },
  { code: 'fa', name: 'Persian', native: 'فارسی' },
  { code: 'he', name: 'Hebrew', native: 'עברית' },
  { code: 'uk', name: 'Ukrainian', native: 'Українська' },
  { code: 'cs', name: 'Czech', native: 'Čeština' },
  { code: 'ro', name: 'Romanian', native: 'Română' },
  { code: 'hu', name: 'Hungarian', native: 'Magyar' },
  { code: 'el', name: 'Greek', native: 'Ελληνικά' },
  { code: 'da', name: 'Danish', native: 'Dansk' },
  { code: 'fi', name: 'Finnish', native: 'Suomi' },
  { code: 'no', name: 'Norwegian', native: 'Norsk' },
  { code: 'af', name: 'Afrikaans', native: 'Afrikaans' },
  { code: 'ak', name: 'Twi', native: 'Twi' },
  { code: 'am', name: 'Amharic', native: 'አማርኛ' },
  { code: 'ay', name: 'Aymara', native: 'Aymar aru' },
  { code: 'az', name: 'Azerbaijani', native: 'Azərbaycan' },
  { code: 'be', name: 'Belarusian', native: 'Беларуская' },
  { code: 'bg', name: 'Bulgarian', native: 'Български' },
  { code: 'bm', name: 'Bambara', native: 'Bamanankan' },
  { code: 'bs', name: 'Bosnian', native: 'Bosanski' },
  { code: 'ca', name: 'Catalan', native: 'Català' },
  { code: 'ceb', name: 'Cebuano', native: 'Cebuano' },
  { code: 'ckb', name: 'Kurdish (Sorani)', native: 'کوردی سۆرانی' },
  { code: 'co', name: 'Corsican', native: 'Corsu' },
  { code: 'cy', name: 'Welsh', native: 'Cymraeg' },
  { code: 'dv', name: 'Dhivehi', native: 'ދިވެހި' },
  { code: 'ee', name: 'Ewe', native: 'Eʋegbe' },
  { code: 'eo', name: 'Esperanto', native: 'Esperanto' },
  { code: 'et', name: 'Estonian', native: 'Eesti' },
  { code: 'eu', name: 'Basque', native: 'Euskara' },
  { code: 'fy', name: 'Frisian', native: 'Frysk' },
  { code: 'ga', name: 'Irish', native: 'Gaeilge' },
  { code: 'gd', name: 'Scots Gaelic', native: 'Gàidhlig' },
  { code: 'gl', name: 'Galician', native: 'Galego' },
  { code: 'gn', name: 'Guarani', native: 'Avañe\'ẽ' },
  { code: 'ha', name: 'Hausa', native: 'Hausa' },
  { code: 'haw', name: 'Hawaiian', native: 'ʻŌlelo Hawaiʻi' },
  { code: 'hmn', name: 'Hmong', native: 'Hmoob' },
  { code: 'hr', name: 'Croatian', native: 'Hrvatski' },
  { code: 'ht', name: 'Haitian Creole', native: 'Kreyòl ayisyen' },
  { code: 'hy', name: 'Armenian', native: 'Հայերեն' },
  { code: 'ig', name: 'Igbo', native: 'Igbo' },
  { code: 'ilo', name: 'Ilocano', native: 'Ilokano' },
  { code: 'is', name: 'Icelandic', native: 'Íslenska' },
  { code: 'jw', name: 'Javanese', native: 'Basa Jawa' },
  { code: 'ka', name: 'Georgian', native: 'ქართული' },
  { code: 'kk', name: 'Kazakh', native: 'Қазақ тілі' },
  { code: 'km', name: 'Khmer', native: 'ភាសាខ្មែរ' },
  { code: 'kri', name: 'Krio', native: 'Krio' },
  { code: 'ku', name: 'Kurdish (Kurmanji)', native: 'Kurdî' },
  { code: 'ky', name: 'Kyrgyz', native: 'Кыргызча' },
  { code: 'la', name: 'Latin', native: 'Latina' },
  { code: 'lb', name: 'Luxembourgish', native: 'Lëtzebuergesch' },
  { code: 'lg', name: 'Luganda', native: 'Luganda' },
  { code: 'ln', name: 'Lingala', native: 'Lingála' },
  { code: 'lo', name: 'Lao', native: 'ລາວ' },
  { code: 'lt', name: 'Lithuanian', native: 'Lietuvių' },
  { code: 'lv', name: 'Latvian', native: 'Latviešu' },
  { code: 'mg', name: 'Malagasy', native: 'Malagasy' },
  { code: 'mi', name: 'Maori', native: 'Māori' },
  { code: 'mk', name: 'Macedonian', native: 'Македонски' },
  { code: 'mn', name: 'Mongolian', native: 'Монгол' },
  { code: 'mt', name: 'Maltese', native: 'Malti' },
  { code: 'my', name: 'Burmese', native: 'မြန်မာ' },
  { code: 'nso', name: 'Northern Sotho (Sepedi)', native: 'Sepedi' },
  { code: 'ny', name: 'Chichewa', native: 'Chichewa' },
  { code: 'om', name: 'Oromo', native: 'Afaan Oromoo' },
  { code: 'ps', name: 'Pashto', native: 'پښتو' },
  { code: 'qu', name: 'Quechua', native: 'Runa Simi' },
  { code: 'rw', name: 'Kinyarwanda', native: 'Ikinyarwanda' },
  { code: 'sd', name: 'Sindhi', native: 'سنڌي' },
  { code: 'sk', name: 'Slovak', native: 'Slovenčina' },
  { code: 'sl', name: 'Slovenian', native: 'Slovenščina' },
  { code: 'sm', name: 'Samoan', native: 'Gagana fa\'a Sāmoa' },
  { code: 'sn', name: 'Shona', native: 'chiShona' },
  { code: 'so', name: 'Somali', native: 'Soomaaliga' },
  { code: 'sq', name: 'Albanian', native: 'Shqip' },
  { code: 'sr', name: 'Serbian', native: 'Српски' },
  { code: 'st', name: 'Sesotho', native: 'Sesotho' },
  { code: 'su', name: 'Sundanese', native: 'Basa Sunda' },
  { code: 'sw', name: 'Swahili', native: 'Kiswahili' },
  { code: 'tg', name: 'Tajik', native: 'Тоҷикӣ' },
  { code: 'ti', name: 'Tigrinya', native: 'ትግርኛ' },
  { code: 'tk', name: 'Turkmen', native: 'Türkmençe' },
  { code: 'ts', name: 'Tsonga', native: 'Xitsonga' },
  { code: 'tt', name: 'Tatar', native: 'Татар теле' },
  { code: 'ug', name: 'Uyghur', native: 'ئۇيغۇرچە' },
  { code: 'uz', name: 'Uzbek', native: 'Oʻzbekcha' },
  { code: 'xh', name: 'Xhosa', native: 'isiXhosa' },
  { code: 'yi', name: 'Yiddish', native: 'ייִדיש' },
  { code: 'yo', name: 'Yoruba', native: 'Èdè Yorùbá' },
  { code: 'zu', name: 'Zulu', native: 'isiZulu' }
];

// --- 2. State Management ---
const state = {
  isExecuting: false,
  safeMode: false,
  provider: 'gemini',
  activeLanguage: 'en',
  ws: null,
  speechRecognition: null,
  isListening: false,
  executionLogs: [],
  currentGoalText: '',
  lastResultData: null,
  stepCount: 1,
  maxSteps: 50
};

// --- 3. DOM Elements Cache ---
const elements = {};

function initElements() {
  elements.goalInput = document.getElementById('goal-input');
  elements.btnExecute = document.getElementById('btn-execute-goal');
  elements.btnStop = document.getElementById('btn-stop-agent');
  elements.btnVoice = document.getElementById('btn-voice-input');
  elements.voiceLabel = document.getElementById('voice-btn-label');
  elements.micIcon = document.getElementById('mic-icon');
  
  elements.executionDrawer = document.getElementById('execution-drawer');
  elements.executionStatus = document.getElementById('execution-status-label');
  elements.stepCounter = document.getElementById('step-counter-label');
  elements.terminalStream = document.getElementById('terminal-stream');
  elements.btnCopyTerminal = document.getElementById('btn-copy-terminal');
  
  elements.resultContainer = document.getElementById('result-container');
  elements.resultHeading = document.getElementById('result-heading');
  elements.resultBodyText = document.getElementById('result-body-text');
  elements.btnSpeakResult = document.getElementById('btn-speak-result');
  elements.btnExportMd = document.getElementById('btn-export-markdown');
  elements.btnExportJson = document.getElementById('btn-export-json');
  
  elements.btnToggleSafeMode = document.getElementById('btn-toggle-safemode');
  elements.safeModeStateText = document.getElementById('safe-mode-state-text');
  elements.providerStateText = document.getElementById('provider-state-text');
  elements.btnQuickProvider = document.getElementById('btn-quick-provider');
  
  elements.memoryBadge = document.getElementById('memory-size-badge');
  elements.systemStatusText = document.getElementById('system-status-text');
  elements.btnProjectBrowser = document.getElementById('btn-project-browser');
  elements.btnMemoryPill = document.getElementById('btn-memory-pill');
  elements.btnMetricsPill = document.getElementById('btn-metrics-pill');
  elements.btnSettingsPill = document.getElementById('btn-settings-pill');
  
  // Modals
  elements.modalSettings = document.getElementById('modal-settings');
  elements.btnCloseSettings = document.getElementById('btn-close-settings-modal');
  elements.btnCancelSettings = document.getElementById('btn-cancel-settings-modal');
  elements.btnSaveSettings = document.getElementById('btn-save-settings-modal');
  elements.selectProvider = document.getElementById('modal-select-provider');
  elements.inputGeminiKey = document.getElementById('input-gemini-key');
  elements.inputDeepseekKey = document.getElementById('input-deepseek-key');
  elements.inputOpenaiKey = document.getElementById('input-openai-key');
  elements.inputGroqKey = document.getElementById('input-groq-key');
  elements.inputCustomName = document.getElementById('input-custom-name');
  elements.inputCustomUrl = document.getElementById('input-custom-url');
  elements.inputCustomKey = document.getElementById('input-custom-key');
  elements.inputCustomModel = document.getElementById('input-custom-model');
  elements.inputOllamaModel = document.getElementById('input-ollama-model');
  elements.checkboxSafeMode = document.getElementById('modal-checkbox-safemode');
  
  elements.modalMemory = document.getElementById('modal-memory');
  elements.btnCloseMemory = document.getElementById('btn-close-memory-modal');
  elements.btnCloseMemoryBtn = document.getElementById('btn-close-memory-btn');
  elements.btnResetMemory = document.getElementById('btn-reset-memory-modal');
  elements.memoryPrompts = document.getElementById('modal-memory-prompts');
  elements.memorySize = document.getElementById('modal-memory-size');
  elements.memoryProgress = document.getElementById('modal-memory-progress');
  
  elements.modalMetrics = document.getElementById('modal-metrics');
  elements.btnCloseMetrics = document.getElementById('btn-close-metrics-modal');
  elements.metricsJsonDisplay = document.getElementById('metrics-json-display');
  
  elements.modalPermission = document.getElementById('modal-permission');
  elements.permissionDesc = document.getElementById('permission-modal-desc');
  elements.permissionDetails = document.getElementById('permission-modal-details');
  elements.btnApprovePermission = document.getElementById('btn-approve-permission');
  elements.btnDenyPermission = document.getElementById('btn-deny-permission');

  // Connection Diagnostics
  elements.btnConnectionsPill = document.getElementById('btn-connections-pill');
  elements.connectionsBadge = document.getElementById('connections-badge');
  elements.modalConnections = document.getElementById('modal-connections');
  elements.btnCloseConnections = document.getElementById('btn-close-connections-modal');
  elements.btnRerunConnCheck = document.getElementById('btn-rerun-conn-check');
  elements.connStabilityScore = document.getElementById('conn-stability-score');
  elements.connDurationText = document.getElementById('conn-duration-text');
  elements.connectionsReportDisplay = document.getElementById('connections-report-display');
  
  // Language Selector
  elements.btnLangDropdown = document.getElementById('btn-lang-dropdown');
  elements.langDropdownMenu = document.getElementById('lang-dropdown-menu');
  elements.langSearchBox = document.getElementById('lang-search-box');
  elements.langItemsContainer = document.getElementById('lang-items-container');
  elements.activeLangLabel = document.getElementById('active-lang-label');
  
  // Stepper Elements
  elements.stepNodes = [
    document.getElementById('step-node-1'),
    document.getElementById('step-node-2'),
    document.getElementById('step-node-3'),
    document.getElementById('step-node-4')
  ];
  elements.stepLines = [
    document.getElementById('step-line-1'),
    document.getElementById('step-line-2'),
    document.getElementById('step-line-3')
  ];
}

// --- 4. Initialization & Setup ---
document.addEventListener('DOMContentLoaded', () => {
  initElements();
  if (window.lucide) {
    lucide.createIcons();
  }
  
  setupTextarea();
  setupQuickIdeas();
  setupVoiceRecognition();
  setupLanguageSelector();
  setupModals();
  setupWebSocket();
  setupActions();
  fetchSystemStatus();
  fetchMemoryStats();
  
  // Periodic telemetry refresh & execution watchdog (recovers from socket drops)
  setInterval(() => {
    fetchSystemStatus();
    fetchMemoryStats();
    checkGoalWatchdog();
  }, 2500);
});

// --- 5. Textarea Auto-expand & Shortcut ---
function setupTextarea() {
  if (!elements.goalInput) return;
  
  const resize = () => {
    elements.goalInput.style.height = 'auto';
    elements.goalInput.style.height = Math.max(90, elements.goalInput.scrollHeight) + 'px';
  };
  
  elements.goalInput.addEventListener('input', resize);
  
  elements.goalInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      executeGoal();
    }
  });
}

// --- 6. Quick Ideas Chips ---
function setupQuickIdeas() {
  const chips = document.querySelectorAll('.idea-chip');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      const prompt = chip.getAttribute('data-prompt');
      if (prompt && elements.goalInput) {
        elements.goalInput.value = prompt;
        elements.goalInput.dispatchEvent(new Event('input'));
        elements.goalInput.focus();
        // Visual feedback animation
        chip.classList.add('scale-95');
        setTimeout(() => chip.classList.remove('scale-95'), 150);
      }
    });
  });
}

// --- 7. Web Speech API (Voice Input) ---
function setupVoiceRecognition() {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    if (elements.btnVoice) {
      elements.btnVoice.title = 'Voice input not supported in this browser';
      elements.btnVoice.classList.add('opacity-50', 'cursor-not-allowed');
    }
    return;
  }
  
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  state.speechRecognition = new SpeechRecognition();
  state.speechRecognition.continuous = false;
  state.speechRecognition.interimResults = true;
  state.speechRecognition.lang = 'en-US';

  state.speechRecognition.onstart = () => {
    state.isListening = true;
    if (elements.btnVoice) {
      elements.btnVoice.classList.add('border-red-500', 'bg-red-500/10', 'text-red-400');
      elements.voiceLabel.textContent = 'Listening...';
    }
  };

  state.speechRecognition.onresult = (event) => {
    let transcript = '';
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      transcript += event.results[i][0].transcript;
    }
    if (transcript && elements.goalInput) {
      elements.goalInput.value = transcript;
      elements.goalInput.dispatchEvent(new Event('input'));
    }
  };

  state.speechRecognition.onerror = (e) => {
    console.warn('Speech recognition error:', e.error);
    stopListening();
  };

  state.speechRecognition.onend = () => {
    stopListening();
  };

  if (elements.btnVoice) {
    elements.btnVoice.addEventListener('click', () => {
      if (state.isListening) {
        state.speechRecognition.stop();
      } else {
        try {
          state.speechRecognition.start();
        } catch (err) {
          console.error(err);
        }
      }
    });
  }
}

function stopListening() {
  state.isListening = false;
  if (elements.btnVoice) {
    elements.btnVoice.classList.remove('border-red-500', 'bg-red-500/10', 'text-red-400');
    elements.voiceLabel.textContent = 'Voice Input';
  }
}

// --- 8. Google Translate Multi-Language Selector ---
function setupLanguageSelector() {
  const countBadge = document.getElementById('lang-count-badge');
  if (countBadge) {
    countBadge.textContent = `${GOOGLE_LANGUAGES.length}+ Languages`;
  }
  
  renderLanguageList(GOOGLE_LANGUAGES);

  // Dynamically fetch and merge backend language list
  fetch('/api/translate/languages')
    .then(res => res.json())
    .then(data => {
      if (data && Array.isArray(data.languages) && data.languages.length > 0) {
        const existingCodes = new Set(GOOGLE_LANGUAGES.map(l => l.code));
        let added = false;
        data.languages.forEach(l => {
          if (!existingCodes.has(l.code)) {
            GOOGLE_LANGUAGES.push(l);
            existingCodes.add(l.code);
            added = true;
          }
        });
        if (countBadge) {
          countBadge.textContent = `${GOOGLE_LANGUAGES.length}+ Languages`;
        }
        if (added) {
          renderLanguageList(GOOGLE_LANGUAGES);
        }
      }
    })
    .catch(err => console.debug('Languages fetch fallback:', err));

  // Toggle Dropdown
  elements.btnLangDropdown?.addEventListener('click', (e) => {
    e.stopPropagation();
    elements.langDropdownMenu?.classList.toggle('hidden');
    elements.langDropdownMenu?.classList.toggle('flex');
    if (!elements.langDropdownMenu?.classList.contains('hidden')) {
      elements.langSearchBox?.focus();
    }
  });

  // Search filter
  elements.langSearchBox?.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    const filtered = GOOGLE_LANGUAGES.filter(l => 
      l.name.toLowerCase().includes(query) || 
      l.native.toLowerCase().includes(query) ||
      l.code.toLowerCase().includes(query)
    );
    renderLanguageList(filtered);
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!elements.langDropdownMenu?.contains(e.target) && e.target !== elements.btnLangDropdown) {
      elements.langDropdownMenu?.classList.add('hidden');
      elements.langDropdownMenu?.classList.remove('flex');
    }
  });

  // Restore saved language
  const savedLang = localStorage.getItem('helper_ai_lang');
  if (savedLang) {
    applyLanguage(savedLang, false);
  }
}

function renderLanguageList(list) {
  if (!elements.langItemsContainer) return;
  elements.langItemsContainer.innerHTML = '';
  
  list.forEach(item => {
    const btn = document.createElement('button');
    btn.className = 'w-full text-left px-3 py-2 text-xs flex items-center justify-between text-slate-300 hover:bg-white/10 hover:text-white transition';
    btn.innerHTML = `
      <div class="flex items-center gap-2">
        <span class="font-medium text-white">${item.name}</span>
        <span class="text-[11px] text-slate-400 font-sans">(${item.native})</span>
      </div>
      <span class="text-[10px] text-slate-400 font-mono uppercase bg-slate-900 px-1.5 py-0.5 rounded border border-white/5">${item.code}</span>
    `;
    btn.addEventListener('click', () => {
      applyLanguage(item.code, true);
      elements.langDropdownMenu?.classList.add('hidden');
      elements.langDropdownMenu?.classList.remove('flex');
    });
    elements.langItemsContainer.appendChild(btn);
  });
}

function applyLanguage(code, triggerReload) {
  state.activeLanguage = code;
  localStorage.setItem('helper_ai_lang', code);
  
  const found = GOOGLE_LANGUAGES.find(l => l.code === code);
  if (found && elements.activeLangLabel) {
    elements.activeLangLabel.textContent = found.name;
  }
  
  // Google Translate cookie configuration
  const hostname = window.location.hostname;
  document.cookie = `googtrans=/en/${code}; path=/; domain=${hostname}`;
  document.cookie = `googtrans=/en/${code}; path=/;`;
  
  // Trigger standard google translate combo box if active
  const select = document.querySelector('.goog-te-combo');
  if (select) {
    select.value = code;
    select.dispatchEvent(new Event('change'));
  } else if (triggerReload) {
    window.location.reload();
  }
}

// --- 9. Stepper Pipeline Controller ---
function updateStepper(stepIndex) {
  // stepIndex: 1 = Researching, 2 = Planning, 3 = Executing, 4 = Verifying
  elements.stepNodes.forEach((node, idx) => {
    if (!node) return;
    const current = idx + 1;
    node.classList.remove('active', 'completed');
    if (current < stepIndex) {
      node.classList.add('completed');
    } else if (current === stepIndex) {
      node.classList.add('active');
    }
  });

  elements.stepLines.forEach((line, idx) => {
    if (!line) return;
    if (idx + 1 < stepIndex) {
      line.classList.add('completed');
    } else {
      line.classList.remove('completed');
    }
  });
}

// --- 10. Terminal Stream Logger ---
function appendTerminalLog(message, type = 'info') {
  if (!elements.terminalStream) return;
  
  const time = new Date().toLocaleTimeString();
  const line = document.createElement('div');
  line.className = 'terminal-line';
  
  let badgeColor = 'text-slate-400';
  if (type === 'action') badgeColor = 'text-cyan-400 font-bold';
  else if (type === 'thought') badgeColor = 'text-purple-400';
  else if (type === 'success') badgeColor = 'text-emerald-400 font-bold';
  else if (type === 'error') badgeColor = 'text-red-400 font-bold';
  else if (type === 'warn') badgeColor = 'text-amber-400 font-semibold';
  
  line.innerHTML = `
    <span class="terminal-time">[${time}]</span>
    <span class="${badgeColor}">${message}</span>
  `;
  
  elements.terminalStream.appendChild(line);
  elements.terminalStream.scrollTop = elements.terminalStream.scrollHeight;
  state.executionLogs.push(`[${time}] ${message}`);
}

// --- 11. WebSocket Integration ---
function setupWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;
  
  try {
    state.ws = new WebSocket(wsUrl);
    
    state.ws.onopen = () => {
      console.log('⚡ Connected to Helper-AI real-time telemetry stream');
      if (state.wsPingInterval) clearInterval(state.wsPingInterval);
      state.wsPingInterval = setInterval(() => {
        if (state.ws && state.ws.readyState === WebSocket.OPEN) {
          state.ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 15000);
    };
    
    state.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'pong') return; // Heartbeat ack
        handleStreamEvent(data);
      } catch (e) {
        console.error('Error parsing WS message:', e);
      }
    };
    
    state.ws.onclose = () => {
      if (state.wsPingInterval) clearInterval(state.wsPingInterval);
      console.warn('Telemetry stream disconnected. Reconnecting in 3s...');
      setTimeout(setupWebSocket, 3000);
    };
    
    state.ws.onerror = (err) => {
      console.error('WebSocket error:', err);
    };
  } catch (err) {
    console.error('WebSocket connection failed:', err);
  }
}

function handleStreamEvent(data) {
  const payload = (data && data.data && typeof data.data === 'object') ? { ...data, ...data.data } : (data || {});
  const type = payload.type || payload.event;
  
  if (type === 'init') {
    const isRunning = Boolean(payload.is_running);
    const history = payload.history || [];
    if (!isRunning && (state.isExecuting || (elements.btnStop && !elements.btnStop.classList.contains('hidden')))) {
      if (history.length > 0 && state.executionLogs.length <= 4) {
        history.forEach(item => {
          if (item.thought) appendTerminalLog(`💡 Plan: ${item.thought}`, 'thought');
          if (item.action && item.action !== 'none') appendTerminalLog(`⚡ Action: ${item.action}`, 'action');
          if (item.output) {
            const outText = typeof item.output === 'string' ? item.output : JSON.stringify(item.output);
            appendTerminalLog(`↳ Result: ${outText.slice(0, 450)}${outText.length > 450 ? '...' : ''}`, 'info');
          }
        });
      }
      const lastMsg = history.length > 0 ? (history[history.length - 1].output || history[history.length - 1].result) : 'Goal execution finished.';
      handleExecutionComplete({ success: true, message: lastMsg });
    }
  }
  else if (type === 'started') {
    state.isExecuting = true;
    elements.btnExecute?.classList.add('opacity-50', 'pointer-events-none');
    elements.btnStop?.classList.remove('hidden');
    elements.executionDrawer?.classList.remove('hidden');
    elements.resultContainer?.classList.add('hidden');
    updateStepper(1);
    appendTerminalLog(`🚀 Goal initiated: "${payload.goal || state.currentGoalText}"`, 'info');
  } 
  else if (type === 'step_start') {
    state.stepCount = payload.step || 1;
    if (elements.stepCounter) {
      elements.stepCounter.textContent = `Step ${state.stepCount} of ${state.maxSteps}`;
    }
    // Update stepper phase intelligently based on step
    if (state.stepCount === 1) updateStepper(1); // Researching
    else if (state.stepCount === 2) updateStepper(2); // Planning
    else updateStepper(3); // Executing
  } 
  else if (type === 'thought') {
    const planText = payload.thought || payload.message || payload.plan || 'Analyzing next action...';
    appendTerminalLog(`💡 Plan: ${planText}`, 'thought');
  } 
  else if (type === 'action') {
    updateStepper(3);
    const actionName = payload.action || payload.tool;
    const actionInput = JSON.stringify(payload.args || payload.input || payload.action_args || '');
    appendTerminalLog(`⚡ Action [${actionName}]: ${actionInput.slice(0, 180)}`, 'action');
  } 
  else if (type === 'action_result') {
    const rawOut = payload.output !== undefined ? payload.output : (payload.result !== undefined ? payload.result : '');
    const resText = typeof rawOut === 'string' ? rawOut : JSON.stringify(rawOut || '');
    if (resText.trim()) {
      const lineCount = resText.split('\n').filter(l => l.trim()).length;
      const countNote = lineCount > 3 ? ` (${lineCount} items/lines)` : '';
      appendTerminalLog(`↳ Result${countNote}: ${resText.slice(0, 450)}${resText.length > 450 ? '...' : ''}`, 'info');
    }
  } 
  else if (type === 'permission_requested') {
    showPermissionModal(payload);
  } 
  else if (type === 'completed' || type === 'finished') {
    handleExecutionComplete(payload);
  } 
  else if (type === 'error') {
    appendTerminalLog(`❌ Error: ${payload.message || payload.error}`, 'error');
    handleExecutionComplete({ success: false, final_result: payload.message || payload.error });
  }
}

function handleExecutionComplete(data) {
  state.isExecuting = false;
  state.lastResultData = data;
  updateStepper(4);
  
  elements.btnExecute?.classList.remove('opacity-50', 'pointer-events-none');
  elements.btnStop?.classList.add('hidden');
  
  if (elements.executionStatus) {
    elements.executionStatus.textContent = data.success !== false ? 'Goal Completed Successfully' : 'Goal Execution Finished';
  }
  
  appendTerminalLog(`🎉 Mission complete! Final status: ${data.success !== false ? 'SUCCESS' : 'FINISHED'}`, 'success');
  
  // Show comprehensive final result card
  if (elements.resultContainer && elements.resultBodyText) {
    elements.resultContainer.classList.remove('hidden');
    elements.resultBodyText.textContent = data.final_result || data.message || 'Execution completed without output text.';
  }
  
  fetchMemoryStats();
}

// --- 12. Goal Execution Dispatcher ---
async function executeGoal() {
  const goal = elements.goalInput?.value?.trim();
  if (!goal) {
    elements.goalInput?.focus();
    return;
  }
  
  state.currentGoalText = goal;
  state.executionLogs = [];
  
  // Show drawer and clear terminal
  elements.executionDrawer?.classList.remove('hidden');
  elements.resultContainer?.classList.add('hidden');
  if (elements.terminalStream) {
    elements.terminalStream.innerHTML = '';
  }
  
  appendTerminalLog(`Preparing autonomous execution for goal...`, 'info');
  updateStepper(1);
  
  elements.btnExecute?.classList.add('opacity-50', 'pointer-events-none');
  elements.btnStop?.classList.remove('hidden');
  
  try {
    const response = await fetch('/api/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        goal: goal,
        provider: state.provider,
        safe_mode: state.safeMode,
        language: state.activeLanguage
      })
    });
    
    if (!response.ok) {
      throw new Error(`Execution error: ${response.statusText}`);
    }
    
    const result = await response.json();
    if (result && result.status === 'completed') {
      handleExecutionComplete(result);
    }
  } catch (err) {
    console.error('Goal execution error:', err);
    appendTerminalLog(`Execution failed: ${err.message}`, 'error');
    handleExecutionComplete({ success: false, final_result: err.message });
  }
}

async function stopAgent() {
  try {
    appendTerminalLog(`Requesting agent halt...`, 'warn');
    const res = await fetch('/api/cancel', { method: 'POST' });
    const data = await res.json();
    appendTerminalLog(`Agent cancelled: ${data.message || 'Stopped.'}`, 'warn');
  } catch (err) {
    console.error(err);
  }
}

// --- 13. Telemetry & Memory API ---
async function checkGoalWatchdog() {
  const isExecutingUI = state.isExecuting || (elements.btnStop && !elements.btnStop.classList.contains('hidden'));
  if (!isExecutingUI) return;

  try {
    const res = await fetch('/api/status');
    if (!res.ok) return;
    const statusData = await res.json();
    if (!statusData.is_running) {
      try {
        const expRes = await fetch('/api/export');
        if (expRes.ok) {
          const expData = await expRes.json();
          const history = expData.history || [];
          if (history.length > 0 && state.executionLogs.length <= 4) {
            history.forEach(item => {
              if (item.thought) appendTerminalLog(`💡 Plan: ${item.thought}`, 'thought');
              if (item.action && item.action !== 'none') appendTerminalLog(`⚡ Action: ${item.action}`, 'action');
              if (item.output) {
                const outText = typeof item.output === 'string' ? item.output : JSON.stringify(item.output);
                appendTerminalLog(`↳ Result: ${outText.slice(0, 450)}${outText.length > 450 ? '...' : ''}`, 'info');
              }
            });
          }
          const lastMsg = history.length > 0 ? (history[history.length - 1].output || history[history.length - 1].result) : 'Goal execution finished.';
          handleExecutionComplete({ success: true, message: lastMsg });
          return;
        }
      } catch (e) {}
      handleExecutionComplete({ success: true, message: 'Goal execution completed.' });
    }
  } catch (err) {
    // Network silent retry
  }
}

async function fetchSystemStatus() {
  try {
    const res = await fetch('/api/system-status');
    if (!res.ok) return;
    const data = await res.json();
    
    if (elements.systemStatusText) {
      elements.systemStatusText.textContent = `PC Control Online (${data.cpu_percent || 0}% CPU)`;
    }
  } catch (err) {
    // Keep status fallback
  }
}

async function loadAppMemories() {
  const container = document.getElementById('app-memory-cards-container');
  if (!container) return;
  try {
    const res = await fetch('/api/apps/memory');
    const data = await res.json();
    const profiles = data.profiles || [];
    if (profiles.length === 0) {
      container.innerHTML = '<div class="text-slate-500 text-center py-2">No applications in memory yet.</div>';
      return;
    }
    container.innerHTML = '';
    profiles.forEach(p => {
      const card = document.createElement('div');
      card.className = 'p-2.5 rounded-lg bg-slate-900/90 border border-white/5 flex items-center justify-between hover:border-cyan-500/30 transition';
      card.innerHTML = `
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 rounded bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 font-bold text-xs">
            ${p.app_name.substring(0, 2).toUpperCase()}
          </div>
          <div>
            <div class="font-semibold text-white text-xs flex items-center gap-1.5">
              ${p.app_name}
              <span class="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 font-mono">${p.app_type}</span>
            </div>
            <div class="text-[10px] text-slate-400">
              ⚡ ${p.shortcuts_count} Hotkeys • ${p.controls_count} UI Controls
            </div>
          </div>
        </div>
        <button class="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 font-mono text-[10px]" onclick="useAppPrompt('${p.app_name}')">
          Use App
        </button>
      `;
      container.appendChild(card);
    });
  } catch (e) {
    container.innerHTML = '<div class="text-red-400 text-center py-2">Failed to load app profiles</div>';
  }
}

window.useAppPrompt = function(appName) {
  if (elements.goalInput) {
    elements.goalInput.value = `Open ${appName} and use its direct fast-path shortcuts`;
    elements.goalInput.dispatchEvent(new Event('input'));
    elements.goalInput.focus();
    elements.modalMemory?.classList.add('hidden');
  }
};

async function fetchMemoryStats() {
  try {
    const res = await fetch('/api/memory/stats');
    if (!res.ok) return;
    const data = await res.json();
    
    const sizeStr = data.size_mb !== undefined ? `${data.size_mb.toFixed(2)} MB` : '0.02 MB';
    if (elements.memoryBadge) {
      elements.memoryBadge.textContent = sizeStr;
    }
    if (elements.memorySize) {
      elements.memorySize.textContent = `${sizeStr} / 20.0 MB`;
    }
    if (elements.memoryPrompts) {
      elements.memoryPrompts.textContent = `${data.prompt_count || 0} goals recorded`;
    }
    if (elements.memoryProgress) {
      const pct = Math.min(100, Math.max(2, (data.size_mb / 20.0) * 100));
      elements.memoryProgress.style.width = `${pct}%`;
    }
  } catch (err) {
    // Ignore silent telemetry errors
  }
}

// --- 14. Modals and Settings Management ---
function setupModals() {
  // Settings Modal
  elements.btnSettingsPill?.addEventListener('click', () => {
    elements.modalSettings?.classList.remove('hidden');
    loadSettingsIntoModal();
  });
  
  elements.btnCloseSettings?.addEventListener('click', () => elements.modalSettings?.classList.add('hidden'));
  elements.btnCancelSettings?.addEventListener('click', () => elements.modalSettings?.classList.add('hidden'));
  elements.btnSaveSettings?.addEventListener('click', saveSettingsFromModal);
  
  elements.selectProvider?.addEventListener('change', updateProviderKeyVisibility);
  
  // Memory Modal
  elements.btnMemoryPill?.addEventListener('click', () => {
    fetchMemoryStats();
    loadAppMemories();
    elements.modalMemory?.classList.remove('hidden');
  });
  elements.btnCloseMemory?.addEventListener('click', () => elements.modalMemory?.classList.add('hidden'));
  elements.btnCloseMemoryBtn?.addEventListener('click', () => elements.modalMemory?.classList.add('hidden'));
  elements.btnResetMemory?.addEventListener('click', resetMemoryLog);

  // Reverse Engineering Trigger Button
  document.getElementById('btn-trigger-re')?.addEventListener('click', async () => {
    const input = document.getElementById('input-re-target');
    const target = input ? input.value.trim() : '';
    if (!target) return;
    const btn = document.getElementById('btn-trigger-re');
    if (btn) btn.innerHTML = '<span>Scanning...</span>';
    try {
      const res = await fetch('/api/apps/reverse-engineer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: target, depth: 'deep' })
      });
      const data = await res.json();
      appendTerminalLog(`Reverse engineered '${target}': ${data.output || 'Saved to memory'}`, 'action');
      await loadAppMemories();
      if (input) input.value = '';
    } catch (e) {
      alert('Analysis failed: ' + e.message);
    } finally {
      if (btn) btn.innerHTML = '<i data-lucide="scan" class="w-3.5 h-3.5"></i> Analyze';
      if (window.lucide) lucide.createIcons();
    }
  });
  
  // Metrics Modal
  elements.btnMetricsPill?.addEventListener('click', async () => {
    elements.modalMetrics?.classList.remove('hidden');
    if (elements.metricsJsonDisplay) {
      elements.metricsJsonDisplay.textContent = 'Loading system metrics...';
      try {
        const res = await fetch('/api/system-status');
        const data = await res.json();
        elements.metricsJsonDisplay.textContent = JSON.stringify(data, null, 2);
      } catch (e) {
        elements.metricsJsonDisplay.textContent = 'Failed to fetch metrics.';
      }
    }
  });
  elements.btnCloseMetrics?.addEventListener('click', () => elements.modalMetrics?.classList.add('hidden'));
  
  // Safe Mode Quick Toggle
  elements.btnToggleSafeMode?.addEventListener('click', () => {
    state.safeMode = !state.safeMode;
    updateSafeModeDisplay();
  });
  
  // Provider Quick Badge Click
  elements.btnQuickProvider?.addEventListener('click', () => {
    elements.modalSettings?.classList.remove('hidden');
    loadSettingsIntoModal();
  });
  
  // Project Browser Launcher
  elements.btnProjectBrowser?.addEventListener('click', async () => {
    try {
      appendTerminalLog('Launching dedicated project browser session...', 'info');
      await fetch('/api/browser/launch', { method: 'POST' });
    } catch (err) {
      console.error(err);
    }
  });
  
  // Permission Modal Buttons
  elements.btnApprovePermission?.addEventListener('click', () => submitPermission(true));
  elements.btnDenyPermission?.addEventListener('click', () => submitPermission(false));

  // Connection Diagnostics Modal
  elements.btnConnectionsPill?.addEventListener('click', runConnectionsCheck);
  elements.btnRerunConnCheck?.addEventListener('click', runConnectionsCheck);
  elements.btnCloseConnections?.addEventListener('click', () => elements.modalConnections?.classList.add('hidden'));

  // Universal Custom AI 1-Click Preset Chips
  document.querySelectorAll('.btn-preset-chip').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const target = e.currentTarget;
      if (elements.inputCustomName) elements.inputCustomName.value = target.dataset.name || '';
      if (elements.inputCustomUrl) elements.inputCustomUrl.value = target.dataset.url || '';
      if (elements.inputCustomModel) elements.inputCustomModel.value = target.dataset.model || '';
    });
  });
}

async function runConnectionsCheck() {
  elements.modalConnections?.classList.remove('hidden');
  if (elements.connectionsReportDisplay) {
    elements.connectionsReportDisplay.innerHTML = '<div class="text-cyan-400 py-3 flex items-center gap-2"><span>⚡ Running double-pass connection diagnostic across all subsystems...</span></div>';
  }
  try {
    const res = await fetch('/api/connections/check?pass_count=2');
    const data = await res.json();
    if (elements.connStabilityScore) {
      elements.connStabilityScore.textContent = `${data.stability_score_pct || 100}%`;
    }
    if (elements.connDurationText) {
      elements.connDurationText.textContent = `Pass 1: ${data.pass_1?.duration_ms || 0}ms | Pass 2: ${data.pass_2?.duration_ms || 0}ms | Total: ${data.total_duration_ms || 0}ms`;
    }
    if (elements.connectionsBadge) {
      elements.connectionsBadge.textContent = `${data.stability_score_pct || 100}% OK`;
    }
    if (elements.connectionsReportDisplay) {
      let html = `<div class="font-semibold text-emerald-400 mb-3 text-xs flex items-center justify-between">
        <span>Diagnostic Complete (Double Pass)</span>
        <span class="text-slate-400 font-normal">Socket reuse speedup active</span>
      </div>`;
      html += '<table class="w-full text-left border-collapse text-xs">';
      html += '<tr class="border-b border-white/10 text-slate-400 pb-2"><th class="pb-1.5">Target</th><th class="pb-1.5">Pass 1</th><th class="pb-1.5">Pass 2</th><th class="pb-1.5">Speedup</th><th class="pb-1.5">Status</th></tr>';
      for (const [target, comp] of Object.entries(data.comparison || {})) {
        const isOk = comp.status_pass_2 === 'connected' || comp.status_pass_2 === 'standby_ready';
        const badgeColor = isOk ? 'text-emerald-400 bg-emerald-500/10' : (comp.status_pass_2 === 'offline' ? 'text-amber-400 bg-amber-500/10' : 'text-slate-400 bg-white/5');
        const speedup = comp.speedup_pct > 0 ? `<span class="text-cyan-400 font-bold">+${comp.speedup_pct}%</span>` : '<span class="text-slate-400">steady</span>';
        html += `<tr class="border-b border-white/5 py-1.5">
          <td class="py-1.5 text-slate-200 font-mono">${target}</td>
          <td class="py-1.5 text-slate-300 font-mono">${comp.latency_pass_1_ms}ms</td>
          <td class="py-1.5 text-slate-300 font-mono">${comp.latency_pass_2_ms}ms</td>
          <td class="py-1.5">${speedup}</td>
          <td class="py-1.5"><span class="px-2 py-0.5 rounded text-[10px] font-semibold ${badgeColor}">${comp.status_pass_2}</span></td>
        </tr>`;
      }
      html += '</table>';
      elements.connectionsReportDisplay.innerHTML = html;
    }
  } catch (err) {
    if (elements.connectionsReportDisplay) {
      elements.connectionsReportDisplay.innerHTML = `<span class="text-red-400">Failed to run connection diagnostics: ${err.message}</span>`;
    }
  }
}

function updateProviderKeyVisibility() {
  const p = elements.selectProvider?.value;
  document.getElementById('group-gemini-key')?.classList.toggle('hidden', p !== 'gemini');
  document.getElementById('group-deepseek-key')?.classList.toggle('hidden', p !== 'deepseek');
  document.getElementById('group-custom-ai')?.classList.toggle('hidden', p !== 'custom');
  document.getElementById('group-openai-key')?.classList.toggle('hidden', p !== 'openai');
  document.getElementById('group-groq-key')?.classList.toggle('hidden', p !== 'groq');
  document.getElementById('group-ollama-config')?.classList.toggle('hidden', p !== 'ollama');
}

function loadSettingsIntoModal() {
  if (elements.selectProvider) elements.selectProvider.value = state.provider;
  if (elements.checkboxSafeMode) elements.checkboxSafeMode.checked = state.safeMode;
  if (elements.inputGeminiKey) elements.inputGeminiKey.value = localStorage.getItem('helper_gemini_key') || '';
  if (elements.inputDeepseekKey) elements.inputDeepseekKey.value = localStorage.getItem('helper_deepseek_key') || '';
  if (elements.inputCustomName) elements.inputCustomName.value = localStorage.getItem('helper_custom_name') || 'OpenRouter';
  if (elements.inputCustomUrl) elements.inputCustomUrl.value = localStorage.getItem('helper_custom_url') || 'https://openrouter.ai/api/v1';
  if (elements.inputCustomKey) elements.inputCustomKey.value = localStorage.getItem('helper_custom_key') || '';
  if (elements.inputCustomModel) elements.inputCustomModel.value = localStorage.getItem('helper_custom_model') || 'anthropic/claude-3.5-sonnet';
  if (elements.inputOpenaiKey) elements.inputOpenaiKey.value = localStorage.getItem('helper_openai_key') || '';
  if (elements.inputGroqKey) elements.inputGroqKey.value = localStorage.getItem('helper_groq_key') || '';
  if (elements.inputOllamaModel) elements.inputOllamaModel.value = localStorage.getItem('helper_ollama_model') || 'qwen2.5:1.5b';
  updateProviderKeyVisibility();
}

function saveSettingsFromModal() {
  state.provider = elements.selectProvider?.value || 'gemini';
  state.safeMode = elements.checkboxSafeMode?.checked || false;
  
  if (elements.inputGeminiKey) localStorage.setItem('helper_gemini_key', elements.inputGeminiKey.value);
  if (elements.inputDeepseekKey) localStorage.setItem('helper_deepseek_key', elements.inputDeepseekKey.value);
  if (elements.inputCustomName) localStorage.setItem('helper_custom_name', elements.inputCustomName.value);
  if (elements.inputCustomUrl) localStorage.setItem('helper_custom_url', elements.inputCustomUrl.value);
  if (elements.inputCustomKey) localStorage.setItem('helper_custom_key', elements.inputCustomKey.value);
  if (elements.inputCustomModel) localStorage.setItem('helper_custom_model', elements.inputCustomModel.value);
  if (elements.inputOpenaiKey) localStorage.setItem('helper_openai_key', elements.inputOpenaiKey.value);
  if (elements.inputGroqKey) localStorage.setItem('helper_groq_key', elements.inputGroqKey.value);
  if (elements.inputOllamaModel) localStorage.setItem('helper_ollama_model', elements.inputOllamaModel.value);

  // Sync to server .env
  fetch('/api/settings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      provider: state.provider,
      gemini_key: elements.inputGeminiKey?.value || null,
      deepseek_key: elements.inputDeepseekKey?.value || null,
      custom_name: elements.inputCustomName?.value || null,
      custom_url: elements.inputCustomUrl?.value || null,
      custom_key: elements.inputCustomKey?.value || null,
      custom_model: elements.inputCustomModel?.value || null,
      openai_key: elements.inputOpenaiKey?.value || null,
      groq_key: elements.inputGroqKey?.value || null,
      ollama_model: elements.inputOllamaModel?.value || null,
      safe_mode: state.safeMode
    })
  }).catch(err => console.warn('Could not persist settings to server:', err));
  
  updateSafeModeDisplay();
  if (elements.providerStateText) {
    elements.providerStateText.textContent = state.provider.toUpperCase();
  }
  
  elements.modalSettings?.classList.add('hidden');
}

function updateSafeModeDisplay() {
  if (elements.safeModeStateText) {
    elements.safeModeStateText.textContent = state.safeMode ? 'On (Safe Mode)' : 'Off (Full Autonomous)';
    elements.safeModeStateText.className = state.safeMode ? 'text-amber-400 font-bold' : 'text-slate-200';
  }
}

async function resetMemoryLog() {
  if (!confirm('Are you sure you want to clear agent_memory.md?')) return;
  try {
    await fetch('/api/memory/reset', { method: 'POST' });
    fetchMemoryStats();
    elements.modalMemory?.classList.add('hidden');
  } catch (e) {
    alert('Failed to reset memory');
  }
}

function showPermissionModal(data) {
  if (!elements.modalPermission) return;
  elements.modalPermission.classList.remove('hidden');
  if (elements.permissionDetails) {
    elements.permissionDetails.textContent = JSON.stringify(data, null, 2);
  }
}

async function submitPermission(approved) {
  elements.modalPermission?.classList.add('hidden');
  try {
    await fetch('/api/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved })
    });
  } catch (e) {
    console.error(e);
  }
}

// --- 15. Action Handlers (Speak, Export, Copy) ---
function setupActions() {
  elements.btnExecute?.addEventListener('click', executeGoal);
  elements.btnStop?.addEventListener('click', stopAgent);
  
  // Copy Terminal Output
  elements.btnCopyTerminal?.addEventListener('click', () => {
    const text = state.executionLogs.join('\n');
    navigator.clipboard.writeText(text).then(() => {
      elements.btnCopyTerminal.innerHTML = '<i data-lucide="check" class="w-3 h-3 text-emerald-400"></i> Copied!';
      if (window.lucide) lucide.createIcons();
      setTimeout(() => {
        elements.btnCopyTerminal.innerHTML = '<i data-lucide="copy" class="w-3 h-3"></i> Copy Output';
        if (window.lucide) lucide.createIcons();
      }, 2000);
    });
  });
  
  // Read Aloud / Speak
  elements.btnSpeakResult?.addEventListener('click', () => {
    const text = elements.resultBodyText?.textContent;
    if (!text) return;
    
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  });
  
  // Export Markdown Report
  elements.btnExportMd?.addEventListener('click', () => {
    const text = elements.resultBodyText?.textContent || '';
    const content = `# Helper-AI Execution Report\n\n**Goal:** ${state.currentGoalText}\n**Date:** ${new Date().toISOString()}\n\n---\n\n${text}\n\n---\n### Execution Logs\n\`\`\`\n${state.executionLogs.join('\n')}\n\`\`\``;
    downloadBlob(content, 'helper_ai_report.md', 'text/markdown');
  });
  
  // Export JSON History
  elements.btnExportJson?.addEventListener('click', () => {
    const data = {
      goal: state.currentGoalText,
      timestamp: new Date().toISOString(),
      result: state.lastResultData,
      logs: state.executionLogs
    };
    downloadBlob(JSON.stringify(data, null, 2), 'helper_ai_history.json', 'application/json');
  });
}

function downloadBlob(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
