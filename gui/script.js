
async function pyCall(method, ...args) {
  try {
    return await window.pywebview.api[method](...args);
  } catch (e) {
    console.error(`pyCall(${method}) failed:`, e);
  }
}

/** Format a timestamp as HH:MM:SS */
function ts() {
  return new Date().toLocaleTimeString('en-GB', { hour12: false });
}

/* ── Theme management (early load) ──────────────────────────────────────── */
const THEME_STORAGE_KEY = 'gag2-theme-preference';
const DEFAULT_THEME = 'default';

/** Change the theme and save preference */
async function changeTheme(themeName) {
  document.documentElement.setAttribute('data-theme', themeName);
  localStorage.setItem(THEME_STORAGE_KEY, themeName);
  await pyCall('set_theme', themeName);  // Save to config.json
  const selector = document.getElementById('themeSelector');
  if (selector) {
    selector.value = themeName;
  }
}

/** Load and apply saved theme from config.json */
async function loadTheme() {
  let themeToApply = DEFAULT_THEME;
  try {
    const configStr = await pyCall('get_config');
    if (configStr) {
      const config = JSON.parse(configStr);
      themeToApply = config.theme || DEFAULT_THEME;
    }
  } catch (e) {
    console.warn('Could not load theme from config:', e);
    themeToApply = localStorage.getItem(THEME_STORAGE_KEY) || DEFAULT_THEME;
  }
  
  document.documentElement.setAttribute('data-theme', themeToApply);
  localStorage.setItem(THEME_STORAGE_KEY, themeToApply);
  const selector = document.getElementById('themeSelector');
  if (selector) {
    selector.value = themeToApply;
  }
}

// Wait for pywebview to be ready before loading theme
window.addEventListener('pywebviewready', function() {
  loadTheme();
}, { once: true });

/* ── Activity log ────────────────────────────────────────────────────────── */
const logBox = document.getElementById('logBox');

window.appendLog = function(msg, tag = 'info') {
  const entry = document.createElement('div');
  entry.className = 'log-entry';

  const time = document.createElement('span');
  time.className = 'log-time';
  time.textContent = `[${ts()}]`;

  const text = document.createElement('span');
  text.className = `log-msg ${tag}`;
  text.textContent = msg;

  entry.appendChild(time);
  entry.appendChild(text);
  logBox.appendChild(entry);
  logBox.scrollTop = logBox.scrollHeight;
};

window.clearLog = function() {
  logBox.innerHTML = '';
  window.appendLog('Log cleared.', 'info');
};

/* ── Roblox status indicator ─────────────────────────────────────────────── */
const statusDot    = document.getElementById('statusDot');
const statusText   = document.getElementById('statusText');
const placeholder  = document.getElementById('robloxPlaceholder');

window.onRobloxStatus = function(found) {
  if (found) {
    statusDot.classList.add('active');
    statusText.textContent = 'Roblox connected';
    placeholder.classList.add('hidden');
    window.appendLog('Roblox window detected and positioned.', 'success');
  } else {
    statusDot.classList.remove('active');
    statusText.textContent = 'Searching…';
    placeholder.classList.remove('hidden');
  }
};

/* ── Tab switching ───────────────────────────────────────────────────────── */
function switchTab(id) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(`tab-${id}`).classList.add('active');
  document.querySelector(`[onclick="switchTab('${id}')"]`).classList.add('active');
}

/* ── Sub-tab switching (for nested tabs like Shop's Seeds/Gears) ──────────── */
function switchSubTab(id) {
  document.querySelectorAll('.sub-tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(`subtab-${id}`).classList.add('active');
  document.querySelector(`[onclick="switchSubTab('${id}')"]`).classList.add('active');
}

/* ── Rebind modal ────────────────────────────────────────────────────────── */
let rebindAction  = null;
let rebindCaptured = null;

const modal        = document.getElementById('rebindModal');
const modalTitle   = document.getElementById('modalTitle');
const modalHint    = document.getElementById('modalHint');
const modalKey     = document.getElementById('modalKey');
const modalConfirm = document.getElementById('modalConfirm');

/** Format a key for display (uppercase for single chars, title case for named keys) */
function formatKeyDisplay(key) {
  if (!key) return '—';
  return key.length === 1 ? key.toUpperCase() : key;
}

/** Update hotkey displays in both action cards and settings */
function updateHotkeyDisplay(action, key) {
  const display = formatKeyDisplay(key);
  const cardEl = document.getElementById(`hk-${action}`);
  const settingEl = document.getElementById(`set-hk-${action}`);
  if (cardEl) cardEl.textContent = display;
  if (settingEl) settingEl.textContent = display;
}

function openRebind(action) {
  rebindAction   = action;
  rebindCaptured = null;
  modalTitle.textContent  = `Rebind · ${action}`;
  modalHint.textContent   = 'Press any key…';
  modalHint.className     = 'modal-hint';
  modalKey.textContent    = '—';
  modalConfirm.disabled   = true;
  modal.classList.add('active');

  // Listen for a keydown (once: true auto-removes listener)
  window.addEventListener('keydown', onRebindKey, { once: true });
}

function onRebindKey(e) {
  e.preventDefault();
  rebindCaptured = e.key.toLowerCase();

  const display = formatKeyDisplay(e.key);
  modalKey.textContent  = display;
  modalHint.textContent = 'Key captured — confirm?';
  modalHint.classList.add('captured');
  modalConfirm.disabled = false;
}

async function confirmRebind() {
  if (!rebindCaptured || !rebindAction) return;

  await pyCall('rebind', rebindAction, rebindCaptured);
  updateHotkeyDisplay(rebindAction, rebindCaptured);
  closeRebind();
}

function closeRebind() {
  modal.classList.remove('active');
  rebindAction   = null;
  rebindCaptured = null;
}

modal.addEventListener('click', e => {
  if (e.target === modal) closeRebind();
});

/* ── Seeds and Gears Toggle Management ────────────────────────────────────── */
const SEEDS = [
  'Carrot', 'Strawberry', 'Blueberry', 'Tulip', 'Tomato', 'Apple', 'Bamboo', 
  'Corn', 'Cactus', 'Pineapple', 'Mushroom', 'Green Bean', 'Banana', 'Grape', 
  'Coconut', 'Mango', 'Dragon Fruit', 'Acorn', 'Cherry', 'Sunflower', 
  'Venus Fly Trap', 'Pomegranate', 'Poison Apple', 'Moon Bloom', "Dragon's Breath"
];

const GEARS = [
  'Common Watering Can', 'Common Sprinkler', 'Sign', 'Uncommon Sprinkler', 
  'Trowel', 'Rare Sprinkler', 'Jump Mushroom', 'Speed Mushroom', 'Lantern', 
  'Shrink Mushroom', 'Supersize Mushroom', 'Gnome', 'Flashbang', 'Basic Pot', 
  'Legendary Sprinkler', 'Invisibility Mushroom', 'Teleporter', 'Wheelbarrow', 
  'Super Watering Can', 'Super Sprinkler'
];

/* ── Mode management ──────────────────────────────────────── */
let currentMode = 'seeds';

async function loadCurrentMode() {
  const configStr = await pyCall('get_config');
  if (configStr) {
    const config = JSON.parse(configStr);
    currentMode = config.mode || 'seeds';
    updateModeDisplay();
  }
}

function updateModeDisplay() {
  const seedsBtn = document.getElementById('btn-mode-seeds');
  const gearsBtn = document.getElementById('btn-mode-gears');
  
  if (seedsBtn) {
    if (currentMode === 'seeds') {
      seedsBtn.textContent = 'ACTIVE MODE';
      seedsBtn.classList.remove('inactive');
    } else {
      seedsBtn.textContent = 'Click to activate';
      seedsBtn.classList.add('inactive');
    }
  }
  
  if (gearsBtn) {
    if (currentMode === 'gears') {
      gearsBtn.textContent = 'ACTIVE MODE';
      gearsBtn.classList.remove('inactive');
    } else {
      gearsBtn.textContent = 'Click to activate';
      gearsBtn.classList.add('inactive');
    }
  }
}

async function setMode(mode) {
  if (mode !== 'seeds' && mode !== 'gears') {
    return;
  }
  
  if (currentMode === mode) {
    return;
  }
  
  const result = await pyCall('set_mode', mode);
  if (result === 'ok') {
    currentMode = mode;
    updateModeDisplay();
  }
}

function initializeToggles(itemList, gridId, storageKey) {
  const grid = document.getElementById(gridId);
  if (!grid) return;

  grid.innerHTML = '';

  itemList.forEach(item => {
    const toggle = document.createElement('div');
    toggle.className = 'toggle-item';

    const label = document.createElement('label');
    label.className = 'toggle-label';
    label.textContent = item;

    const switchEl = document.createElement('div');
    switchEl.className = 'toggle-switch';
    switchEl.dataset.item = item;
    switchEl.dataset.storageKey = storageKey;

    // Load state from config
    pyCall('get_toggle_state', storageKey, item).then(isActive => {
      if (isActive === 'true' || isActive === true) {
        switchEl.classList.add('active');
      }
    });

    switchEl.addEventListener('click', () => {
      const isActive = switchEl.classList.toggle('active');
      pyCall('set_toggle_state', storageKey, item, isActive);
      
      const logMsg = isActive ? `${item} Selected` : `${item} Deselected`;
      window.appendLog(logMsg, isActive ? 'success' : 'info');
    });

    toggle.appendChild(label);
    toggle.appendChild(switchEl);
    grid.appendChild(toggle);
  });
}

/** Toggle all items in a category */
async function toggleAllItems(gridId, storageKey) {
  const grid = document.getElementById(gridId);
  if (!grid) return;

  const switches = grid.querySelectorAll('.toggle-switch');
  if (switches.length === 0) return;

  // Check if all are currently active
  const allActive = Array.from(switches).every(s => s.classList.contains('active'));

  // Toggle all to opposite state
  const newState = !allActive;
  
  for (const switchEl of switches) {
    const item = switchEl.dataset.item;
    if (newState) {
      switchEl.classList.add('active');
    } else {
      switchEl.classList.remove('active');
    }
    await pyCall('set_toggle_state', storageKey, item, newState);
    
    const logMsg = newState ? `${item} Selected` : `${item} Deselected`;
    window.appendLog(logMsg, newState ? 'success' : 'info');
  }
}

window.toggleAllSeeds = function() {
  toggleAllItems('seedsGrid', 'seeds');
};

window.toggleAllGears = function() {
  toggleAllItems('gearsGrid', 'gears');
};

/* ── Interval slider management ──────────────────────────────────────────── */
const INTERVAL_MIN = 1;  // minutes
const INTERVAL_MAX = 5;  // minutes
const INTERVAL_MIN_SECS = INTERVAL_MIN * 60;
const INTERVAL_MAX_SECS = INTERVAL_MAX * 60;

function updateIntervalDisplay(minutes) {
  const display = document.getElementById('intervalDisplay');
  if (display) {
    display.textContent = minutes === 1 ? '1 min' : `${minutes} min`;
  }
}

function initializeIntervalSlider() {
  const slider = document.getElementById('intervalSlider');
  if (!slider) return;

  // Load current interval from config and set slider
  pyCall('get_interval').then(intervalSecs => {
    const minutes = Math.max(INTERVAL_MIN, Math.min(INTERVAL_MAX, Math.round(intervalSecs / 60)));
    slider.value = minutes;
    updateIntervalDisplay(minutes);
  });

  // Handle slider change
  slider.addEventListener('change', async () => {
    const minutes = parseInt(slider.value);
    const seconds = minutes * 60;
    updateIntervalDisplay(minutes);
    
    // Save to config.json
    await pyCall('set_interval', seconds);
    window.appendLog(`Autobuy interval set to ${minutes} min`, 'info');
  });

  // Update display while dragging
  slider.addEventListener('input', () => {
    const minutes = parseInt(slider.value);
    updateIntervalDisplay(minutes);
  });
}

/* ── Init ────────────────────────────────────────────────────────────────── */
window.addEventListener('pywebviewready', async () => {
  const status = JSON.parse(await pyCall('get_status'));
  const hkeys  = status.config.hotkeys;

  // Apply saved hotkeys to all displays
  ['Start', 'Stop', 'Exit'].forEach(action => {
    updateHotkeyDisplay(action, hkeys[action]);
  });

  // Load and display current mode
  await loadCurrentMode();

  // Initialize toggles for seeds and gears
  initializeToggles(SEEDS, 'seedsGrid', 'seeds');
  initializeToggles(GEARS, 'gearsGrid', 'gears');

  // Initialize interval slider
  initializeIntervalSlider();

  if (!status.win32) {
    window.appendLog('pywin32 not installed — pip install pywin32', 'error');
  }
  if (!status.hotkeys) {
    window.appendLog('Global hotkeys unavailable — run as admin', 'error');
  }

  window.appendLog('Macro ready.', 'info');
  const keyStr = `Start → ${hkeys.Start.toUpperCase()}  |  Stop → ${hkeys.Stop.toUpperCase()}  |  Exit → ${hkeys.Exit.toUpperCase()}`;
  window.appendLog(keyStr, 'info');

  const titleBar = document.getElementById('titleBar');
  let isDragging = false;

  titleBar.addEventListener('mousedown', () => {
    isDragging = true;
  });

  document.addEventListener('mousemove', () => {
    if (isDragging) {
      pyCall('sync_roblox');
    }
  });

  document.addEventListener('mouseup', () => {
    isDragging = false;
  });
});
