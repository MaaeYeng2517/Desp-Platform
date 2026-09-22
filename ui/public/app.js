const API_BASE = '/api/knowledge-base';
const STORAGE_KEY = 'knowledge-base-studio-workspace-v1';
const FALLBACK_CATALOG = [
  { type: 'source_pdf', label: 'PDF', category: 'Sources', description: 'Load text from PDF files', defaultConfig: { extractLayout: true } },
  { type: 'source_docx', label: 'DOCX', category: 'Sources', description: 'Load text from Word documents', defaultConfig: { includeTables: true } },
  { type: 'source_csv', label: 'CSV', category: 'Sources', description: 'Load rows from a CSV file', defaultConfig: { delimiter: ',' } },
  { type: 'source_website', label: 'Website', category: 'Sources', description: 'Crawl and load web content', defaultConfig: { maxPages: 10 } },
  { type: 'source_database', label: 'Database', category: 'Sources', description: 'Read rows from a database query', defaultConfig: { batchSize: 500 } },
  { type: 'source_api', label: 'API', category: 'Sources', description: 'Ingest JSON from an API endpoint', defaultConfig: { method: 'GET' } },
  { type: 'extract_text', label: 'Extract Text', category: 'Processing', description: 'Extract readable text', defaultConfig: { preserveParagraphs: true } },
  { type: 'clean_text', label: 'Clean Text', category: 'Processing', description: 'Remove noise and normalize text', defaultConfig: { removeExtraWhitespace: true } },
  { type: 'chunk', label: 'Chunk', category: 'Processing', description: 'Split content into chunks', defaultConfig: { chunkSize: 500, overlap: 50 } },
  { type: 'metadata', label: 'Metadata', category: 'Metadata', description: 'Attach structured metadata', defaultConfig: { requiredFields: ['source', 'language'] } },
  { type: 'embedding', label: 'Embedding', category: 'Processing', description: 'Create vector embeddings', defaultConfig: { dimension: 32, model: 'local-hash-v1' } },
  { type: 'reranking', label: 'Reranking', category: 'AI', description: 'Reorder search results', defaultConfig: { topK: 5 } },
  { type: 'vector_database', label: 'Vector DB', category: 'Storage', description: 'Store and index embeddings', defaultConfig: { index: 'cosine' } },
  { type: 'knowledge_base', label: 'Knowledge Base', category: 'Storage', description: 'Publish an indexed collection', defaultConfig: { publish: true } },
  { type: 'rag', label: 'RAG', category: 'AI', description: 'Retrieve context for an answer', defaultConfig: { topK: 4 } },
  { type: 'agent', label: 'AI Agent', category: 'AI', description: 'Expose the knowledge base', defaultConfig: { temperature: 0.2 } },
];
const CATEGORY_ORDER = ['Sources', 'Processing', 'Metadata', 'Storage', 'AI'];
const NODE_ORDER = {
  source_pdf: 0, source_docx: 0, source_csv: 0, source_website: 0, source_database: 0, source_api: 0,
  extract_text: 10, clean_text: 15, chunk: 20, metadata: 30, embedding: 40, reranking: 45,
  vector_database: 50, knowledge_base: 60, rag: 70, agent: 80,
};
const DEFAULT_TYPES = ['source_pdf', 'extract_text', 'clean_text', 'chunk', 'metadata', 'embedding', 'vector_database', 'knowledge_base', 'rag', 'agent'];
const DEFAULT_DOCUMENTS = [
  { id: 'demo-refunds', content: 'Customers can request a refund within 30 days of purchase. Refunds return to the original payment method within five business days.', metadata: { source: 'refund-policy', language: 'en' } },
  { id: 'demo-password', content: 'To reset a password, open the sign in screen, choose forgot password, and follow the email verification link. Contact support if the email does not arrive.', metadata: { source: 'account-help', language: 'en' } },
  { id: 'demo-export', content: 'Export reports from the analytics page. Choose CSV for spreadsheets or JSON for API integrations, then confirm the date range before exporting.', metadata: { source: 'analytics-guide', language: 'en' } },
];

const elements = {};
let catalog = FALLBACK_CATALOG;
let state = {
  kb: null,
  nodes: [],
  edges: [],
  selectedNodeId: null,
  connectMode: false,
  connectFrom: null,
  dragNode: null,
  dragOffset: { x: 0, y: 0 },
  validation: null,
  results: [],
  loading: false,
};

function byId(id) { return document.getElementById(id); }

function cacheElements() {
  [
    'palette', 'palette-count', 'node-layer', 'edge-layer', 'canvas', 'canvas-hint', 'workspace-title',
    'kb-name', 'kb-description', 'metadata-owner', 'metadata-version', 'metadata-visibility', 'metadata-language', 'metadata-tags',
    'metadata-state', 'selected-type', 'node-config-empty', 'node-config-form', 'node-label', 'node-config', 'config-error',
    'documents', 'validate-workflow', 'run-pipeline', 'demo-docs', 'search-query', 'search-button', 'rag-mode',
    'run-state', 'status-nodes', 'status-chunks', 'status-dimension', 'validation-output', 'result-output',
    'connection-status', 'new-workflow', 'save-workflow', 'connect-mode', 'auto-layout', 'delete-node', 'toast-region',
  ].forEach((id) => { elements[id] = byId(id); });
}

function definitionFor(type) {
  return catalog.find((item) => item.type === type) || FALLBACK_CATALOG.find((item) => item.type === type) || { label: type, category: 'Processing', description: type, defaultConfig: {} };
}

function categoryColor(category) {
  if (category === 'Sources') return 'var(--accent)';
  if (category === 'Metadata') return 'var(--blue)';
  if (category === 'Storage') return 'var(--violet)';
  if (category === 'AI') return 'var(--amber)';
  return 'var(--blue)';
}

function categoryCode(category) {
  if (category === 'Sources') return 'S';
  if (category === 'Metadata') return 'M';
  if (category === 'Storage') return 'D';
  if (category === 'AI') return 'A';
  return 'P';
}

function defaultWorkflow() {
  const nodes = DEFAULT_TYPES.map((type, index) => {
    const definition = definitionFor(type);
    return {
      id: `node-${index + 1}`,
      type,
      label: definition.label,
      config: { ...definition.defaultConfig },
      position: { x: 55 + index * 175, y: 145 },
    };
  });
  const edges = nodes.slice(0, -1).map((node, index) => ({ id: `edge-${index + 1}`, from: node.id, to: nodes[index + 1].id }));
  return { nodes, edges };
}

function initialDocuments() {
  return JSON.stringify(DEFAULT_DOCUMENTS, null, 2);
}

function readStoredState() {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
    if (stored && Array.isArray(stored.nodes) && Array.isArray(stored.edges)) {
      state.nodes = stored.nodes;
      state.edges = stored.edges;
      state.kb = stored.kb || null;
      state.validation = stored.validation || null;
      if (stored.metadata) applyMetadataToForm(stored.metadata);
      if (typeof stored.name === 'string') elements['kb-name'].value = stored.name;
      if (typeof stored.documents === 'string') elements.documents.value = stored.documents;
      return true;
    }
  } catch (error) {
    toast(`Could not restore workspace: ${error.message}`, true);
  }
  return false;
}

function persistLocalState() {
  const payload = {
    name: elements['kb-name'].value,
    metadata: readMetadataFromForm(),
    nodes: state.nodes,
    edges: state.edges,
    kb: state.kb,
    validation: state.validation,
    documents: elements.documents.value,
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
}

function applyMetadataToForm(metadata) {
  if (!metadata || typeof metadata !== 'object') return;
  elements['kb-description'].value = metadata.description || elements['kb-description'].value;
  elements['metadata-owner'].value = metadata.owner || '';
  elements['metadata-version'].value = metadata.version || '';
  elements['metadata-visibility'].value = ['private', 'team', 'public'].includes(metadata.visibility) ? metadata.visibility : 'private';
  elements['metadata-language'].value = metadata.language || '';
  elements['metadata-tags'].value = Array.isArray(metadata.tags) ? metadata.tags.join(', ') : '';
}

function readMetadataFromForm() {
  const tags = elements['metadata-tags'].value.split(',').map((tag) => tag.trim()).filter(Boolean);
  const metadata = {
    title: elements['kb-name'].value.trim(),
    description: elements['kb-description'].value.trim(),
    owner: elements['metadata-owner'].value.trim(),
    version: elements['metadata-version'].value.trim(),
    visibility: elements['metadata-visibility'].value,
    language: elements['metadata-language'].value.trim(),
    tags,
  };
  return metadata;
}

function renderPalette() {
  elements.palette.innerHTML = '';
  CATEGORY_ORDER.forEach((category) => {
    const items = catalog.filter((item) => item.category === category);
    if (!items.length) return;
    const group = document.createElement('div');
    group.className = 'palette-group';
    const title = document.createElement('div');
    title.className = 'palette-group-title';
    title.textContent = category;
    group.appendChild(title);
    items.forEach((item) => {
      const button = document.createElement('button');
      button.className = 'palette-item';
      button.type = 'button';
      button.draggable = true;
      button.dataset.type = item.type;
      const icon = document.createElement('span');
      icon.className = 'palette-icon';
      icon.style.background = `${categoryColor(category)}22`;
      icon.style.color = categoryColor(category);
      icon.textContent = categoryCode(category);
      const copy = document.createElement('span');
      copy.className = 'palette-item-copy';
      const label = document.createElement('span');
      label.className = 'palette-item-label';
      label.textContent = item.label;
      const description = document.createElement('span');
      description.className = 'palette-item-desc';
      description.textContent = item.description;
      copy.append(label, description);
      button.append(icon, copy);
      button.addEventListener('dragstart', (event) => {
        event.dataTransfer.setData('application/x-kb-component', item.type);
        event.dataTransfer.effectAllowed = 'copy';
      });
      group.appendChild(button);
    });
    elements.palette.appendChild(group);
  });
  elements['palette-count'].textContent = String(catalog.length);
}

function renderCanvas() {
  elements['node-layer'].innerHTML = '';
  state.nodes.forEach((node) => {
    const definition = definitionFor(node.type);
    const nodeElement = document.createElement('div');
    nodeElement.className = 'workflow-node';
    nodeElement.dataset.id = node.id;
    nodeElement.style.left = `${node.position?.x || 0}px`;
    nodeElement.style.top = `${node.position?.y || 0}px`;
    if (node.id === state.selectedNodeId) nodeElement.classList.add('selected');
    if (node.id === state.connectFrom) nodeElement.classList.add('connect-source');
    const glyph = document.createElement('span');
    glyph.className = 'node-glyph';
    glyph.style.background = `${categoryColor(definition.category)}22`;
    glyph.style.color = categoryColor(definition.category);
    glyph.textContent = categoryCode(definition.category);
    const copy = document.createElement('span');
    copy.className = 'node-copy';
    const label = document.createElement('span');
    label.className = 'node-label';
    label.textContent = node.label || definition.label;
    const type = document.createElement('span');
    type.className = 'node-type';
    type.textContent = definition.category;
    copy.append(label, type);
    nodeElement.append(glyph, copy);
    elements['node-layer'].appendChild(nodeElement);
  });
  elements.canvas.classList.toggle('is-populated', state.nodes.length > 0);
  renderEdges();
  renderToolbar();
}

function renderEdges() {
  const paths = state.edges.map((edge) => {
    const from = state.nodes.find((node) => node.id === edge.from);
    const to = state.nodes.find((node) => node.id === edge.to);
    if (!from || !to) return '';
    const x1 = (from.position?.x || 0) + 142;
    const y1 = (from.position?.y || 0) + 29;
    const x2 = (to.position?.x || 0);
    const y2 = (to.position?.y || 0) + 29;
    const curve = Math.max(55, Math.abs(x2 - x1) * 0.45);
    return `<path class="edge" d="M ${x1} ${y1} C ${x1 + curve} ${y1}, ${x2 - curve} ${y2}, ${x2} ${y2}"></path>`;
  }).join('');
  elements['edge-layer'].innerHTML = `<defs><marker id="arrowhead" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M 0 0 L 7 3 L 0 6" fill="none" stroke="rgba(110, 231, 216, 0.7)" stroke-width="1.4"></path></marker></defs>${paths}`;
}

function renderToolbar() {
  elements['workspace-title'].textContent = elements['kb-name'].value.trim() || 'Untitled knowledge base';
  elements['delete-node'].disabled = !state.selectedNodeId;
  elements['connect-mode'].classList.toggle('button-primary', state.connectMode);
  elements['connect-mode'].textContent = state.connectMode ? 'Cancel connect' : 'Connect mode';
}

function selectNode(id) {
  state.selectedNodeId = id;
  const node = state.nodes.find((item) => item.id === id);
  if (!node) {
    elements['node-config-empty'].hidden = false;
    elements['node-config-form'].hidden = true;
    elements['selected-type'].textContent = 'None';
    renderCanvas();
    return;
  }
  const definition = definitionFor(node.type);
  elements['node-config-empty'].hidden = true;
  elements['node-config-form'].hidden = false;
  elements['selected-type'].textContent = definition.category;
  elements['node-label'].value = node.label || definition.label;
  elements['node-config'].value = JSON.stringify(node.config || definition.defaultConfig || {}, null, 2);
  elements['config-error'].hidden = true;
  renderCanvas();
}

function addNode(type, x, y) {
  const definition = definitionFor(type);
  const id = `node-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
  state.nodes.push({
    id,
    type,
    label: definition.label,
    config: { ...definition.defaultConfig },
    position: { x: Math.max(12, x - 71), y: Math.max(12, y - 29) },
  });
  selectNode(id);
  persistLocalState();
  toast(`${definition.label} added to the canvas`);
}

function removeSelectedNode() {
  if (!state.selectedNodeId) return;
  const id = state.selectedNodeId;
  state.nodes = state.nodes.filter((node) => node.id !== id);
  state.edges = state.edges.filter((edge) => edge.from !== id && edge.to !== id);
  if (state.connectFrom === id) state.connectFrom = null;
  state.selectedNodeId = null;
  selectNode(null);
  persistLocalState();
  toast('Component removed');
}

function autoLayout() {
  const sorted = [...state.nodes].sort((a, b) => (NODE_ORDER[a.type] ?? 20) - (NODE_ORDER[b.type] ?? 20));
  sorted.forEach((node, index) => {
    node.position = { x: 55 + (index % 5) * 175, y: 120 + Math.floor(index / 5) * 145 };
  });
  renderCanvas();
  persistLocalState();
  toast('Canvas auto-layout applied');
}

function addEdge(from, to) {
  if (from === to) {
    toast('A component cannot connect to itself', true);
    return;
  }
  if (state.edges.some((edge) => edge.from === from && edge.to === to)) {
    toast('That connection already exists', true);
    return;
  }
  state.edges.push({ id: `edge-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`, from, to });
  state.connectFrom = null;
  renderCanvas();
  persistLocalState();
  toast('Components connected');
}

function handleCanvasPointerDown(event) {
  const nodeElement = event.target.closest('.workflow-node');
  if (!nodeElement) return;
  const id = nodeElement.dataset.id;
  if (state.connectMode) {
    if (!state.connectFrom) {
      state.connectFrom = id;
      renderCanvas();
      toast('Select the next component to connect');
    } else {
      addEdge(state.connectFrom, id);
    }
    return;
  }
  const node = state.nodes.find((item) => item.id === id);
  if (!node) return;
  selectNode(id);
  const bounds = elements.canvas.getBoundingClientRect();
  state.dragNode = node;
  state.dragOffset = { x: event.clientX - bounds.left - (node.position?.x || 0), y: event.clientY - bounds.top - (node.position?.y || 0) };
  event.preventDefault();
}

function handleWindowPointerMove(event) {
  if (!state.dragNode) return;
  const bounds = elements.canvas.getBoundingClientRect();
  state.dragNode.position = {
    x: Math.max(8, event.clientX - bounds.left - state.dragOffset.x),
    y: Math.max(8, event.clientY - bounds.top - state.dragOffset.y),
  };
  renderCanvas();
}

function handleWindowPointerUp() {
  if (!state.dragNode) return;
  state.dragNode = null;
  persistLocalState();
}

async function api(path, options = {}) {
  const headers = { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(options.headers || {}) };
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const contentType = response.headers.get('content-type') || '';
  const payload = contentType.includes('application/json') ? await response.json() : null;
  if (!response.ok) {
    const message = payload?.message || (typeof payload === 'string' ? payload : `Request failed with status ${response.status}`);
    const error = new Error(typeof message === 'string' ? message : JSON.stringify(message));
    error.payload = payload;
    throw error;
  }
  return payload;
}

function setBusy(loading) {
  state.loading = loading;
  [elements['save-workflow'], elements['validate-workflow'], elements['run-pipeline'], elements['search-button']].forEach((button) => { button.disabled = loading; });
  elements['connection-status'].innerHTML = loading
    ? '<span class="status-dot" style="background:var(--amber)"></span><span>Working...</span>'
    : '<span class="status-dot"></span><span>Local workspace</span>';
}

function toast(message, isError = false) {
  const item = document.createElement('div');
  item.className = `toast${isError ? ' error' : ''}`;
  item.textContent = message;
  elements['toast-region'].appendChild(item);
  window.setTimeout(() => item.remove(), 4200);
}

function statusLabel(status) {
  const labels = { draft: 'Draft', validating: 'Validating', validated: 'Validated', indexing: 'Indexing', ready: 'Ready', failed: 'Failed' };
  return labels[status] || 'Draft';
}

function updateMetadataState(status) {
  const label = statusLabel(status);
  elements['metadata-state'].textContent = label;
  elements['metadata-state'].className = `state-pill state-${String(status || 'draft').toLowerCase()}`;
}

function updateRunState(status) {
  const label = status || 'Idle';
  elements['run-state'].textContent = label;
  elements['run-state'].className = `state-pill ${['ready', 'validated'].includes(label.toLowerCase()) ? 'state-ready' : label.toLowerCase() === 'failed' ? 'state-failed' : label.toLowerCase() === 'idle' ? 'state-idle' : 'state-running'}`;
}

function updateStatusSummary(status) {
  elements['status-nodes'].textContent = `${state.nodes.length} node${state.nodes.length === 1 ? '' : 's'}`;
  const chunkCount = status?.index?.chunks ?? 0;
  const dimension = status?.index?.embeddingDimension ?? 0;
  elements['status-chunks'].textContent = `${chunkCount} chunk${chunkCount === 1 ? '' : 's'}`;
  elements['status-dimension'].textContent = dimension ? `${dimension} dim` : 'not indexed';
}

function renderValidation(validation) {
  state.validation = validation;
  if (!validation) {
    elements['validation-output'].hidden = true;
    elements['validation-output'].innerHTML = '';
    return;
  }
  elements['validation-output'].hidden = false;
  elements['validation-output'].innerHTML = '';
  const summary = document.createElement('div');
  summary.className = `validation-summary ${validation.valid ? 'valid' : 'invalid'}`;
  summary.textContent = validation.valid ? 'Workflow is valid' : 'Workflow needs attention';
  elements['validation-output'].appendChild(summary);
  if (validation.issues?.length) {
    const list = document.createElement('ul');
    list.className = 'validation-issues';
    validation.issues.forEach((issue) => {
      const item = document.createElement('li');
      item.textContent = `${issue.severity === 'warning' ? 'Warning' : 'Error'}: ${issue.message}`;
      list.appendChild(item);
    });
    elements['validation-output'].appendChild(list);
  }
  persistLocalState();
}

function renderResults(response, isRag) {
  state.results = response.results || [];
  elements['result-output'].innerHTML = '';
  if (isRag && typeof response.answer === 'string') {
    const answer = document.createElement('div');
    answer.className = 'result-answer';
    answer.textContent = response.answer;
    elements['result-output'].appendChild(answer);
  }
  if (!state.results.length) {
    const placeholder = document.createElement('div');
    placeholder.className = state.results.length || isRag ? 'result-empty' : 'result-placeholder';
    placeholder.textContent = isRag ? 'No matching knowledge chunks were found.' : 'No search results yet.';
    elements['result-output'].appendChild(placeholder);
    return;
  }
  state.results.forEach((result) => {
    const item = document.createElement('div');
    item.className = 'result-item';
    const meta = document.createElement('div');
    meta.className = 'result-meta';
    const source = document.createElement('span');
    source.textContent = result.chunk?.metadata?.documentId || result.chunk?.sourceDocumentId || 'chunk';
    const score = document.createElement('span');
    score.className = 'result-score';
    score.textContent = `${Math.round((result.score || 0) * 1000) / 10}%`;
    meta.append(source, score);
    const content = document.createElement('div');
    content.className = 'result-content';
    content.textContent = result.chunk?.content || '';
    item.append(meta, content);
    elements['result-output'].appendChild(item);
  });
}

function parseDocuments() {
  try {
    const documents = JSON.parse(elements.documents.value || '[]');
    if (!Array.isArray(documents) || documents.some((document) => !document || typeof document.content !== 'string' || !document.content.trim())) {
      throw new Error('Documents must be an array of objects with non-empty content');
    }
    return documents;
  } catch (error) {
    throw new Error(`Invalid document JSON: ${error.message}`);
  }
}

async function saveWorkspace() {
  setBusy(true);
  try {
    const workflow = { nodes: state.nodes, edges: state.edges };
    const metadata = readMetadataFromForm();
    const payload = {
      name: elements['kb-name'].value.trim() || 'Untitled knowledge base',
      description: metadata.description,
      metadata,
      workflow,
    };
    const path = state.kb?.id ? `/${state.kb.id}` : '';
    const method = state.kb?.id ? 'PATCH' : 'POST';
    const saved = await api(path, { method, body: JSON.stringify(payload) });
    state.kb = saved;
    updateMetadataState(saved.status);
    updateStatusSummary();
    persistLocalState();
    toast(state.kb.id ? 'Workspace saved' : 'Knowledge base created');
  } catch (error) {
    toast(error.message, true);
  } finally {
    setBusy(false);
  }
}

async function validateWorkspace() {
  if (!state.kb?.id) {
    toast('Save the workspace before validation', true);
    return;
  }
  setBusy(true);
  try {
    const response = await api(`/${state.kb.id}/validate`, { method: 'POST' });
    renderValidation(response.validation);
    updateMetadataState(response.status);
    updateRunState(response.status);
    toast(response.validation.valid ? 'Workflow validation passed' : 'Workflow validation found issues', !response.validation.valid);
  } catch (error) {
    renderValidation(error.payload?.validation || null);
    toast(error.message, true);
  } finally {
    setBusy(false);
  }
}

async function runPipeline() {
  if (!state.kb?.id) {
    toast('Save the workspace before running the pipeline', true);
    return;
  }
  let documents;
  try { documents = parseDocuments(); } catch (error) { toast(error.message, true); return; }
  setBusy(true);
  updateRunState('indexing');
  try {
    const response = await api(`/${state.kb.id}/run`, { method: 'POST', body: JSON.stringify({ documents }) });
    updateRunState(response.status);
    updateStatusSummary({ index: { chunks: response.chunkCount, embeddingDimension: response.embeddingDimension } });
    toast(`Pipeline completed with ${response.chunkCount} chunks`);
  } catch (error) {
    renderValidation(error.payload?.validation || null);
    updateRunState('failed');
    toast(error.message, true);
  } finally {
    setBusy(false);
  }
}

async function runSearch() {
  if (!state.kb?.id) {
    toast('Save and index a knowledge base first', true);
    return;
  }
  const query = elements['search-query'].value.trim();
  if (!query) {
    toast('Enter a search query', true);
    return;
  }
  setBusy(true);
  try {
    const response = await api(`/${state.kb.id}/${elements['rag-mode'].checked ? 'retrieve' : 'search'}`, {
      method: 'POST',
      body: JSON.stringify({ query, topK: 4 }),
    });
    renderResults(response, elements['rag-mode'].checked);
  } catch (error) {
    toast(error.message, true);
  } finally {
    setBusy(false);
  }
}

async function refreshStatus() {
  if (!state.kb?.id) {
    updateStatusSummary();
    return;
  }
  try {
    const status = await api(`/${state.kb.id}/status`);
    updateStatusSummary(status);
    updateMetadataState(status.status);
    updateRunState(status.status === 'ready' ? 'Ready' : status.status === 'failed' ? 'Failed' : 'Idle');
  } catch (error) {
    updateRunState('Idle');
  }
}

function loadWorkspaceFromResponse(response) {
  state.kb = response;
  const workflow = response.workflow || defaultWorkflow();
  state.nodes = Array.isArray(workflow.nodes) ? workflow.nodes : defaultWorkflow().nodes;
  state.edges = Array.isArray(workflow.edges) ? workflow.edges : defaultWorkflow().edges;
  applyMetadataToForm(response.metadata || {});
  if (response.name) elements['kb-name'].value = response.name;
  if (response.validation) renderValidation(response.validation);
  updateMetadataState(response.status);
  updateStatusSummary();
  renderCanvas();
  persistLocalState();
}

function resetWorkspace() {
  const workflow = defaultWorkflow();
  state.kb = null;
  state.nodes = workflow.nodes;
  state.edges = workflow.edges;
  state.selectedNodeId = null;
  state.connectFrom = null;
  state.connectMode = false;
  state.validation = null;
  state.results = [];
  elements['kb-name'].value = 'Product Support Knowledge';
  elements['kb-description'].value = 'Support policies, troubleshooting, and product guidance';
  elements['metadata-owner'].value = 'Knowledge Team';
  elements['metadata-version'].value = '1.0.0';
  elements['metadata-visibility'].value = 'team';
  elements['metadata-language'].value = 'en';
  elements['metadata-tags'].value = 'support, product, demo';
  elements.documents.value = initialDocuments();
  elements['validation-output'].hidden = true;
  elements['validation-output'].innerHTML = '';
  elements['result-output'].innerHTML = '<div class="result-placeholder">Run the pipeline, then search your indexed knowledge.</div>';
  updateMetadataState('draft');
  updateRunState('Idle');
  renderCanvas();
  persistLocalState();
  toast('New workflow ready');
}

function bindEvents() {
  elements.canvas.addEventListener('dragover', (event) => { event.preventDefault(); event.dataTransfer.dropEffect = 'copy'; });
  elements.canvas.addEventListener('drop', (event) => {
    event.preventDefault();
    const type = event.dataTransfer.getData('application/x-kb-component');
    if (!type) return;
    const bounds = elements.canvas.getBoundingClientRect();
    addNode(type, event.clientX - bounds.left, event.clientY - bounds.top);
  });
  elements['node-layer'].addEventListener('pointerdown', handleCanvasPointerDown);
  window.addEventListener('pointermove', handleWindowPointerMove);
  window.addEventListener('pointerup', handleWindowPointerUp);
  elements['connect-mode'].addEventListener('click', () => {
    state.connectMode = !state.connectMode;
    state.connectFrom = null;
    renderCanvas();
  });
  elements['auto-layout'].addEventListener('click', autoLayout);
  elements['delete-node'].addEventListener('click', removeSelectedNode);
  elements['new-workflow'].addEventListener('click', resetWorkspace);
  elements['save-workflow'].addEventListener('click', saveWorkspace);
  elements['validate-workflow'].addEventListener('click', validateWorkspace);
  elements['run-pipeline'].addEventListener('click', runPipeline);
  elements['search-button'].addEventListener('click', runSearch);
  elements['search-query'].addEventListener('keydown', (event) => { if (event.key === 'Enter') runSearch(); });
  elements['demo-docs'].addEventListener('click', () => { elements.documents.value = initialDocuments(); toast('Demo documents loaded'); });
  elements['kb-name'].addEventListener('input', () => { renderToolbar(); persistLocalState(); });
  ['kb-description', 'metadata-owner', 'metadata-version', 'metadata-visibility', 'metadata-language', 'metadata-tags'].forEach((id) => {
    elements[id].addEventListener('input', persistLocalState);
    elements[id].addEventListener('change', persistLocalState);
  });
  elements['node-label'].addEventListener('input', () => {
    const node = state.nodes.find((item) => item.id === state.selectedNodeId);
    if (node) node.label = elements['node-label'].value;
    renderCanvas();
    persistLocalState();
  });
  elements['node-config'].addEventListener('input', () => {
    try {
      JSON.parse(elements['node-config'].value || '{}');
      elements['config-error'].hidden = true;
    } catch (error) {
      elements['config-error'].hidden = false;
      elements['config-error'].textContent = `Invalid JSON: ${error.message}`;
    }
  });
  elements['node-config'].addEventListener('change', () => {
    const node = state.nodes.find((item) => item.id === state.selectedNodeId);
    if (!node) return;
    try {
      node.config = JSON.parse(elements['node-config'].value || '{}');
      elements['config-error'].hidden = true;
      persistLocalState();
    } catch (error) {
      elements['config-error'].hidden = false;
      elements['config-error'].textContent = `Invalid JSON: ${error.message}`;
    }
  });
}

async function initialize() {
  cacheElements();
  bindEvents();
  try {
    const remoteCatalog = await api('/catalog');
    if (Array.isArray(remoteCatalog) && remoteCatalog.length) catalog = remoteCatalog;
  } catch (error) {
    elements['connection-status'].innerHTML = '<span class="status-dot" style="background:var(--amber)"></span><span>Offline preview</span>';
  }
  renderPalette();
  if (!readStoredState()) resetWorkspace();
  else {
    renderCanvas();
    updateMetadataState(state.kb?.status || 'draft');
    updateStatusSummary();
  }
  elements.documents.value = elements.documents.value || initialDocuments();
  refreshStatus();
}

document.addEventListener('DOMContentLoaded', initialize);
