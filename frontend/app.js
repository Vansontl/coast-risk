const API_BASE = 'http://127.0.0.1:8010/api';

const state = {
  datasets: [],
  activeDatasetId: null,
  activeDatasetMeta: null,
  datasetRows: [],
  editingRowId: null,
  expertResults: [],
  models: [],
  activeModelId: null,
  lastModelRegionFilter: '',
  histories: [],
  activeHistoryId: null,
  workflow: {
    expertUploaded: false,
    expertAnalyzed: false,
    datasetUploaded: false,
    datasetChecked: false,
    trainSplit: false,
    sugenoReady: false,
    trainRan: false,
    trainEvaluated: false,
  },
};

const SUGENO_RULES = [
  { rule: 'R1', condition: 'X1 cao, X2 cao, X5 cao', output: 'f1 = p1·X1 + q1·X2 + r1·X5 + c1', params: 'p1, q1, r1, c1', weight: 'w1', status: 'Khởi tạo' },
  { rule: 'R2', condition: 'X3 cao, X4 cao, X6 cao', output: 'f2 = p2·X3 + q2·X4 + r2·X6 + c2', params: 'p2, q2, r2, c2', weight: 'w2', status: 'Khởi tạo' },
  { rule: 'R3', condition: 'X1 trung bình, X3 cao, X6 cao', output: 'f3 = p3·X1 + q3·X3 + r3·X6 + c3', params: 'p3, q3, r3, c3', weight: 'w3', status: 'Khởi tạo' },
  { rule: 'R4', condition: 'X2 cao, X4 trung bình, X5 cao', output: 'f4 = p4·X2 + q4·X4 + r4·X5 + c4', params: 'p4, q4, r4, c4', weight: 'w4', status: 'Khởi tạo' },
];

const DATASET_FIELDS = [
  'projectId','region','projectName','waveHeight','tideMode','windSpeed','stormLevel','soilType','weakLayer','slideRisk','surveyQuality','techComplex','constructionDiff','equipmentDepend','techError','materialSupply','equipmentMobilize','transportRisk','resourceShortage','siteManage','coordinationRisk','scheduleRisk','issueHandling','laborSafety','marineSafety','environmentRisk','emergencyResponse','riskScore','riskLevel'
];

function switchSection(targetId) {
  document.querySelectorAll('.page-section').forEach(section => section.classList.toggle('active', section.id === targetId));
  document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.toggle('active', btn.dataset.target === targetId));
  const mobileSelect = document.getElementById('mobileSectionSelect');
  if (mobileSelect && mobileSelect.value !== targetId) mobileSelect.value = targetId;
}

document.querySelectorAll('.nav-btn').forEach(btn => btn.addEventListener('click', () => switchSection(btn.dataset.target)));
document.getElementById('mobileSectionSelect')?.addEventListener('change', event => switchSection(event.target.value));
document.getElementById('mobileSectionSelect')?.addEventListener('change', event => switchSection(event.target.value));

function setChip(id, mode, text) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.remove('done', 'active');
  if (mode === 'done') el.classList.add('done');
  if (mode === 'active') el.classList.add('active');
  if (text) el.textContent = text;
}

function setWorkflowBtnState(elementId, stateName) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.classList.remove('workflow-btn-pending', 'workflow-btn-active', 'workflow-btn-done');
  if (stateName === 'pending') el.classList.add('workflow-btn-pending');
  if (stateName === 'active') el.classList.add('workflow-btn-active');
  if (stateName === 'done') el.classList.add('workflow-btn-done');
}

function refreshWorkflowButtonHints() {
  setWorkflowBtnState('uploadExpertBtn', state.workflow.expertUploaded ? 'done' : 'active');
  setWorkflowBtnState('exportExpertTemplateBtn', state.workflow.expertUploaded ? 'pending' : 'active');

  setWorkflowBtnState('uploadDatasetBtn', state.workflow.datasetUploaded ? 'done' : 'active');
  setWorkflowBtnState('checkDatasetBtn', state.workflow.datasetUploaded && !state.workflow.datasetChecked ? 'active' : (state.workflow.datasetChecked ? 'done' : 'pending'));
  setWorkflowBtnState('exportDatasetTemplateBtn', state.workflow.datasetUploaded ? 'pending' : 'active');

  setWorkflowBtnState('splitDatasetBtn', state.workflow.trainSplit ? 'done' : 'active');
  setWorkflowBtnState('initSugenoBtn', state.workflow.trainSplit && !state.workflow.sugenoReady ? 'active' : (state.workflow.sugenoReady ? 'done' : 'pending'));
  setWorkflowBtnState('runTrainingBtn', state.workflow.sugenoReady && !state.workflow.trainRan ? 'active' : (state.workflow.trainRan ? 'done' : 'pending'));
  setWorkflowBtnState('evaluateTrainingBtn', state.workflow.trainRan && !state.workflow.trainEvaluated ? 'active' : (state.workflow.trainEvaluated ? 'done' : 'pending'));

  setWorkflowBtnState('importB1ExcelBtn', 'active');
  setWorkflowBtnState('normalizeXBtn', 'active');
  setWorkflowBtnState('createDatasetRowBtn', 'pending');

  setWorkflowBtnState('runPredictionBtn', 'active');
  setWorkflowBtnState('refreshHistoryBtn', 'active');
  setWorkflowBtnState('compareSelectedBtn', 'pending');
  setWorkflowBtnState('downloadReportBtn', state.activeHistoryId ? 'active' : 'pending');
  setWorkflowBtnState('downloadTrainingReportBtn', state.activeModelId ? 'active' : 'pending');
}

function refreshWorkflowChips() {
  setChip('expertUploadChip', state.workflow.expertUploaded ? 'done' : 'active', state.workflow.expertUploaded ? '1. Đã nạp file' : '1. Chưa nạp file');
  setChip('expertAnalyzeChip', state.workflow.expertAnalyzed ? 'done' : '', state.workflow.expertAnalyzed ? '2. Đã phân tích' : '2. Chưa phân tích');
  setChip('datasetUploadChip', state.workflow.datasetUploaded ? 'done' : 'active', state.workflow.datasetUploaded ? '1. Đã tải dữ liệu' : '1. Chưa tải dữ liệu');
  setChip('datasetCheckChip', state.workflow.datasetChecked ? 'done' : '', state.workflow.datasetChecked ? '2. Đã kiểm tra cấu trúc' : '2. Chưa kiểm tra cấu trúc');
  setChip('trainSplitChip', state.workflow.trainSplit ? 'done' : 'active', state.workflow.trainSplit ? '1. Đã chia train/test' : '1. Chưa chia train/test');
  setChip('trainSugenoChip', state.workflow.sugenoReady ? 'done' : '', state.workflow.sugenoReady ? '2. Đã khởi tạo Sugeno' : '2. Chưa khởi tạo Sugeno');
  setChip('trainRunChip', state.workflow.trainRan ? 'done' : '', state.workflow.trainRan ? '3. Đã huấn luyện' : '3. Chưa huấn luyện');
  setChip('trainEvalChip', state.workflow.trainEvaluated ? 'done' : '', state.workflow.trainEvaluated ? '4. Đã kiểm định' : '4. Chưa kiểm định');
  refreshWorkflowButtonHints();
}

function setProgress(prefix, percent, text, etaSeconds = null) {
  const bar = document.getElementById(`${prefix}ProgressBar`);
  const label = document.getElementById(`${prefix}ProgressText`);
  const etaLabel = document.getElementById(`${prefix}EtaText`);
  if (bar) bar.style.width = `${percent}%`;
  if (label) label.textContent = `${percent}%${text ? ` - ${text}` : ''}`;
  if (etaLabel) etaLabel.textContent = etaSeconds != null ? `ETA: ~${etaSeconds}s` : 'ETA: --';
}

async function pollJob(prefix, jobId) {
  while (true) {
    const response = await fetch(`${API_BASE}/jobs/${jobId}`);
    const job = await response.json();
    if (!response.ok) throw new Error(job.detail || 'Không đọc được tiến độ xử lý từ backend.');
    setProgress(prefix, job.percent || 0, job.message || 'Đang xử lý', job.etaSeconds ?? null);
    if (job.status === 'done') return job.result;
    if (job.status === 'failed') throw new Error(job.error || job.message || 'Job thất bại');
    await new Promise(resolve => setTimeout(resolve, 300));
  }
}

function isBlankValue(value) {
  return value === null || value === undefined || String(value).trim() === '';
}

function toRiskScale(value) {
  if (isBlankValue(value)) return null;
  const n = Number(value);
  if (!Number.isFinite(n)) return null;
  return Math.max(1, Math.min(5, Number(n.toFixed(2))));
}

function mapWaveHeight(value) {
  if (isBlankValue(value)) return null;
  const n = Number(value);
  if (!Number.isFinite(n)) return null;
  if (n < 1) return 1;
  if (n < 2) return 2;
  if (n < 3) return 3;
  if (n < 4) return 4;
  return 5;
}

function mapWindSpeed(value) {
  if (isBlankValue(value)) return null;
  const n = Number(value);
  if (!Number.isFinite(n)) return null;
  if (n < 6) return 1;
  if (n < 10) return 2;
  if (n < 14) return 3;
  if (n < 18) return 4;
  return 5;
}

function mapWeakLayer(value) {
  if (isBlankValue(value)) return null;
  const n = Number(value);
  if (!Number.isFinite(n)) return null;
  if (n < 2) return 1;
  if (n < 5) return 2;
  if (n < 10) return 3;
  if (n < 20) return 4;
  return 5;
}

function normalizeGroupAverage(values) {
  const nums = values.filter(v => v !== null && v !== undefined && v !== '').map(v => Number(v)).filter(v => Number.isFinite(v) && v > 0);
  if (!nums.length) return null;
  return (nums.reduce((sum, v) => sum + v, 0) / nums.length).toFixed(2);
}

function getNormalizedVector() {
  return {
    X1: normalizeGroupAverage([
      mapWaveHeight(document.getElementById('rowWaveHeight')?.value),
      toRiskScale(document.getElementById('rowTideMode')?.value),
      mapWindSpeed(document.getElementById('rowWindSpeed')?.value),
      toRiskScale(document.getElementById('rowStormLevel')?.value),
    ]),
    X2: normalizeGroupAverage([
      toRiskScale(document.getElementById('rowSoilType')?.value),
      mapWeakLayer(document.getElementById('rowWeakLayer')?.value),
      toRiskScale(document.getElementById('rowSlideRisk')?.value),
      toRiskScale(document.getElementById('rowSurveyQuality')?.value),
    ]),
    X3: normalizeGroupAverage(['rowTechComplex','rowConstructionDiff','rowEquipmentDepend','rowTechError'].map(id => toRiskScale(document.getElementById(id)?.value))),
    X4: normalizeGroupAverage(['rowMaterialSupply','rowEquipmentMobilize','rowTransportRisk','rowResourceShortage'].map(id => toRiskScale(document.getElementById(id)?.value))),
    X5: normalizeGroupAverage(['rowSiteManage','rowCoordinationRisk','rowScheduleRisk','rowIssueHandling'].map(id => toRiskScale(document.getElementById(id)?.value))),
    X6: normalizeGroupAverage(['rowLaborSafety','rowMarineSafety','rowEnvironmentRisk','rowEmergencyResponse'].map(id => toRiskScale(document.getElementById(id)?.value))),
  };
}

function updateB1Summary() {
  const summaryBox = document.getElementById('b1SummaryBox');
  const values = ['rowWaveHeight','rowTideMode','rowWindSpeed','rowStormLevel','rowSoilType','rowWeakLayer','rowSlideRisk','rowSurveyQuality','rowTechComplex','rowConstructionDiff','rowEquipmentDepend','rowTechError','rowMaterialSupply','rowEquipmentMobilize','rowTransportRisk','rowResourceShortage','rowSiteManage','rowCoordinationRisk','rowScheduleRisk','rowIssueHandling','rowLaborSafety','rowMarineSafety','rowEnvironmentRisk','rowEmergencyResponse'].map(id => document.getElementById(id)?.value ?? '');
  const filled = values.filter(v => String(v).trim() !== '').length;
  const percent = Math.round((filled / values.length) * 100);
  const vector = getNormalizedVector();
  if (summaryBox) summaryBox.innerHTML = `Đã nhập <strong>${filled}/${values.length}</strong> biến thành phần (${percent}%).<br>Chỉ tiêu tổng hợp nội bộ hiện tại: <strong>X1=${vector.X1 ?? '--'}</strong> · <strong>X2=${vector.X2 ?? '--'}</strong> · <strong>X3=${vector.X3 ?? '--'}</strong> · <strong>X4=${vector.X4 ?? '--'}</strong> · <strong>X5=${vector.X5 ?? '--'}</strong> · <strong>X6=${vector.X6 ?? '--'}</strong>`;
}

function bindB1FieldListeners() {
  const ids = ['rowWaveHeight','rowTideMode','rowWindSpeed','rowStormLevel','rowSoilType','rowWeakLayer','rowSlideRisk','rowSurveyQuality','rowTechComplex','rowConstructionDiff','rowEquipmentDepend','rowTechError','rowMaterialSupply','rowEquipmentMobilize','rowTransportRisk','rowResourceShortage','rowSiteManage','rowCoordinationRisk','rowScheduleRisk','rowIssueHandling','rowLaborSafety','rowMarineSafety','rowEnvironmentRisk','rowEmergencyResponse'];
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.addEventListener('input', updateB1Summary); el.addEventListener('change', updateB1Summary); }
  });
}

function inferRiskLevel(score) {
  const value = Number(score);
  if (!Number.isFinite(value)) return '';
  if (value < 2) return 'Thấp';
  if (value < 3) return 'Trung bình';
  if (value < 4) return 'Cao';
  return 'Rất cao';
}

function fillPredictionInputsFromB1() {
  const vector = getNormalizedVector();
  const box = document.getElementById('predictionInternalVectorBox');
  if (box) box.innerHTML = `Hệ thống đã xử lý hồ sơ đầu vào và sinh chỉ tiêu tổng hợp nội bộ: <strong>X1=${vector.X1 ?? '--'}</strong> · <strong>X2=${vector.X2 ?? '--'}</strong> · <strong>X3=${vector.X3 ?? '--'}</strong> · <strong>X4=${vector.X4 ?? '--'}</strong> · <strong>X5=${vector.X5 ?? '--'}</strong> · <strong>X6=${vector.X6 ?? '--'}</strong>`;
  return vector;
}

function clearB1Form() {
  fillRowForm({});
  
  document.getElementById('predictionAdvice').textContent = 'Khuyến cáo quản lý sẽ hiển thị sau khi có kết quả.';
  document.getElementById('predictionDominantBox').textContent = 'Nhóm rủi ro nổi trội nhất sẽ hiển thị sau khi tính toán.';
  document.getElementById('predictionRiskMatrixBox').textContent = 'Ma trận rủi ro nội bộ (Likelihood × Impact) sẽ hiển thị sau khi dự báo.';
  document.getElementById('predictionRecommendationBox').textContent = 'Khuyến nghị quản lý rủi ro chi tiết sẽ hiển thị sau khi dự báo.';
  const internalBox = document.getElementById('predictionInternalVectorBox');
  if (internalBox) internalBox.textContent = 'Các chỉ tiêu tổng hợp nội bộ sẽ hiển thị sau khi hệ thống xử lý hồ sơ đầu vào.';
  updateB1Summary();
}

async function uploadExpertSurvey() {
  const input = document.getElementById('expertSurveyFile');
  const file = input.files?.[0];
  if (!file) return document.getElementById('expertStatus').textContent = 'Anh hãy chọn file khảo sát chuyên gia trước.';
  const formData = new FormData();
  formData.append('file', file);
  setProgress('expert', 10, 'Đang chuẩn bị file');
  document.getElementById('expertStatus').textContent = 'Đang upload và phân tích khảo sát chuyên gia...';
  try {
    const response = await fetch(`${API_BASE}/expert-surveys/upload`, { method: 'POST', body: formData });
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || 'Upload khảo sát thất bại.');
    const finalResult = result.jobId ? await pollJob('expert', result.jobId) : result;
    state.expertResults = finalResult?.results || [];
    state.workflow.expertUploaded = true;
    state.workflow.expertAnalyzed = state.expertResults.length > 0;
    renderExpertResults();
    refreshWorkflowChips();
    setProgress('expert', 100, 'Hoàn tất');
    document.getElementById('expertStatus').textContent = `Đã xử lý file ${finalResult.file_name}. Số phiếu: ${finalResult.response_count}. Số yếu tố: ${state.expertResults.length}.`;
  } catch (error) {
    setProgress('expert', 0, 'Lỗi');
    document.getElementById('expertStatus').textContent = error.message || 'Không thể kết nối backend để upload khảo sát.';
  }
}

function renderExpertResults() {
  const body = document.getElementById('expertResultsBody');
  body.innerHTML = '';
  if (!state.expertResults.length) return body.innerHTML = '<tr><td colspan="7" class="muted">Chưa có kết quả khảo sát chuyên gia.</td></tr>';
  state.expertResults.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${item.factor}</td><td>${item.group}</td><td>${item.P}</td><td>${item.I}</td><td>${item.C}</td><td>${item.R}</td><td>${item.rank}</td>`;
    body.appendChild(tr);
  });
}

function syncRegionInputs(region = '', force = false) {
  const trainingRegion = document.getElementById('trainingRegion');
  const predictionRegion = document.getElementById('predictionRegion');
  if (trainingRegion && (force || !trainingRegion.value)) trainingRegion.value = region;
  if (predictionRegion && (force || !predictionRegion.value)) predictionRegion.value = region;
}

function updateTrainingDatasetSummary() {
  const select = document.getElementById('trainingDatasetSelect');
  const summary = document.getElementById('trainingDatasetSummary');
  if (!select || !summary) return;
  if (!state.datasets.length) {
    select.innerHTML = '<option value="">Chưa có dataset</option>';
    summary.textContent = 'Chưa có dataset nào từ A2 để dùng cho huấn luyện.';
    return;
  }
  select.innerHTML = '<option value="">Chọn dataset huấn luyện</option>';
  state.datasets.forEach(dataset => {
    const option = document.createElement('option');
    option.value = dataset.id;
    option.textContent = `#${dataset.id} - ${dataset.name}${dataset.is_active ? ' (đang dùng)' : ''}`;
    if (state.activeDatasetId === dataset.id) option.selected = true;
    select.appendChild(option);
  });
  const active = state.datasets.find(item => item.id === Number(select.value || state.activeDatasetId || 0)) || state.datasets[0];
  if (!active) return;
  state.activeDatasetId = active.id;
  state.activeDatasetMeta = active;
  const region = active.region_name || active.region || active.region_id || 'Chưa rõ vùng';
  summary.innerHTML = `Dataset huấn luyện hiện tại: <strong>#${active.id}</strong> - <strong>${active.name}</strong> | Vùng: <strong>${region}</strong> | Số dòng: <strong>${active.row_count ?? '--'}</strong>`;
  syncRegionInputs(String(region), true);
}

async function uploadDataset() {
  const input = document.getElementById('datasetFile');
  const file = input.files?.[0];
  if (!file) return document.getElementById('datasetStatus').textContent = 'Anh hãy chọn file dataset trước.';
  const datasetName = document.getElementById('datasetNameInput')?.value.trim() || file.name.replace(/\.(xlsx|xls)$/i, '');
  const formData = new FormData();
  formData.append('dataset_name', datasetName);
  formData.append('file', file);
  document.getElementById('datasetStatus').textContent = 'Đang upload và nạp dataset vào hệ thống...';
  setProgress('dataset', 20, 'Đang upload dataset');
  try {
    const response = await fetch(`${API_BASE}/datasets/upload`, { method: 'POST', body: formData });
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || 'Upload dataset thất bại.');
    const finalResult = result.jobId ? await pollJob('dataset', result.jobId) : result;
    state.workflow.datasetUploaded = true;
    refreshWorkflowChips();
    await loadDatasets();
    if (finalResult.dataset_id) {
      state.activeDatasetId = finalResult.dataset_id;
      await loadDatasetRows(state.activeDatasetId);
    }
    updateTrainingDatasetSummary();
    document.getElementById('datasetQualityBox').innerHTML = `Đã nạp dữ liệu thành công. Bộ dữ liệu hiện có <strong>${finalResult.validation.rowCount}</strong> mẫu và <strong>29</strong> cột. Nhãn điểm rủi ro và mức rủi ro được hệ thống tự động gán theo ma trận rủi ro nội bộ.`;
    document.getElementById('datasetStatus').textContent = `Đã nạp dataset ${datasetName}. Số mẫu: ${finalResult.validation.rowCount}.`;
    setProgress('dataset', 100, 'Hoàn tất');
  } catch (error) {
    setProgress('dataset', 0, 'Lỗi');
    document.getElementById('datasetStatus').textContent = error.message || 'Không thể kết nối backend để upload dataset.';
  }
}

async function loadDatasets() {
  const response = await fetch(`${API_BASE}/datasets`);
  state.datasets = await response.json();
  renderDatasetList();
  updateTrainingDatasetSummary();
}

function getSelectedDatasetIds() {
  return Array.from(document.querySelectorAll('[data-dataset-check]:checked')).map(el => Number(el.value));
}

function renderDatasetList() {
  const body = document.getElementById('datasetListBody');
  body.innerHTML = '';
  if (!state.datasets.length) return body.innerHTML = '<tr><td colspan="5" class="muted">Chưa có dataset nào.</td></tr>';
  state.datasets.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td><input type="checkbox" data-dataset-check value="${item.id}"></td><td>${item.id}</td><td>${item.name}<br><span class="muted">Gắn nhãn: ma trận rủi ro nội bộ</span></td><td>${item.row_count ?? 0}</td><td><button class="ghost-btn" data-open-dataset="${item.id}">Chọn</button></td>`;
    body.appendChild(tr);
  });
  body.querySelectorAll('[data-open-dataset]').forEach(btn => btn.addEventListener('click', async e => {
    const id = Number(e.currentTarget.dataset.openDataset);
    state.activeDatasetId = id;
    await loadDatasetRows(id);
    updateTrainingDatasetSummary();
    document.getElementById('datasetStatus').textContent = `Đã chọn dataset #${id} và hiển thị dữ liệu phía dưới.`;
  }));
}

async function loadDatasetRows(datasetId) {
  const response = await fetch(`${API_BASE}/datasets/${datasetId}/rows`);
  state.datasetRows = await response.json();
  renderDatasetRows();
}

function fillRowForm(data = {}) {
  document.getElementById('rowProjectId').value = data.projectId ?? '';
  document.getElementById('rowProjectName').value = data.projectName ?? '';
  document.getElementById('rowRegion').value = data.region ?? '';
  document.getElementById('rowWaveHeight').value = data.waveHeight ?? '';
  document.getElementById('rowTideMode').value = data.tideMode ?? '';
  document.getElementById('rowWindSpeed').value = data.windSpeed ?? '';
  document.getElementById('rowStormLevel').value = data.stormLevel ?? '';
  document.getElementById('rowSoilType').value = data.soilType ?? '';
  document.getElementById('rowWeakLayer').value = data.weakLayer ?? '';
  document.getElementById('rowSlideRisk').value = data.slideRisk ?? '';
  document.getElementById('rowSurveyQuality').value = data.surveyQuality ?? '';
  document.getElementById('rowTechComplex').value = data.techComplex ?? '';
  document.getElementById('rowConstructionDiff').value = data.constructionDiff ?? '';
  document.getElementById('rowEquipmentDepend').value = data.equipmentDepend ?? '';
  document.getElementById('rowTechError').value = data.techError ?? '';
  document.getElementById('rowMaterialSupply').value = data.materialSupply ?? '';
  document.getElementById('rowEquipmentMobilize').value = data.equipmentMobilize ?? '';
  document.getElementById('rowTransportRisk').value = data.transportRisk ?? '';
  document.getElementById('rowResourceShortage').value = data.resourceShortage ?? '';
  document.getElementById('rowSiteManage').value = data.siteManage ?? '';
  document.getElementById('rowCoordinationRisk').value = data.coordinationRisk ?? '';
  document.getElementById('rowScheduleRisk').value = data.scheduleRisk ?? '';
  document.getElementById('rowIssueHandling').value = data.issueHandling ?? '';
  document.getElementById('rowLaborSafety').value = data.laborSafety ?? '';
  document.getElementById('rowMarineSafety').value = data.marineSafety ?? '';
  document.getElementById('rowEnvironmentRisk').value = data.environmentRisk ?? '';
  document.getElementById('rowEmergencyResponse').value = data.emergencyResponse ?? '';
  
  document.getElementById('rowProjectLocation').value = data.projectLocation ?? '';
  document.getElementById('rowProjectType').value = data.projectType ?? '';
  document.getElementById('rowProjectStage').value = data.projectStage ?? '';
  updateB1Summary();
}

async function importB1FromExcel() {
  const input = document.getElementById('b1ImportFile');
  const file = input.files?.[0];
  if (!file) {
    document.getElementById('b1SummaryBox').textContent = 'Anh hãy chọn file Excel mẫu để import vào B1.';
    return;
  }
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${API_BASE}/datasets/import-single-row`, { method: 'POST', body: formData });
  const result = await response.json();
  if (!response.ok) {
    document.getElementById('b1SummaryBox').textContent = result.detail || 'Không import được dữ liệu từ Excel.';
    return;
  }
  fillRowForm(result.row || {});
  fillPredictionInputsFromB1();
  document.getElementById('b1SummaryBox').innerHTML = 'Đã import dữ liệu từ Excel mẫu vào form B1. Anh có thể rà lại, chỉnh tay thêm nếu cần rồi yêu cầu hệ thống xử lý dữ liệu đầu vào.';
  setWorkflowBtnState('importB1ExcelBtn', 'done');
  setWorkflowBtnState('normalizeXBtn', 'active');
}

function getDatasetRowFormPayload() {
  const projectId = document.getElementById('rowProjectId').value.trim();
  const projectName = document.getElementById('rowProjectName').value.trim();
  const region = document.getElementById('rowRegion').value.trim();
  const riskScore = Number(document.getElementById('rowRiskScore').value || 0);
  const riskLevel = document.getElementById('rowRiskLevel').value.trim() || inferRiskLevel(riskScore);
  return { projectId, projectName, riskScore, riskLevel, data: { projectId, region, projectName, waveHeight: Number(document.getElementById('rowWaveHeight').value || 0), tideMode: Number(document.getElementById('rowTideMode').value || 0), windSpeed: Number(document.getElementById('rowWindSpeed').value || 0), stormLevel: Number(document.getElementById('rowStormLevel').value || 0), soilType: Number(document.getElementById('rowSoilType').value || 0), weakLayer: Number(document.getElementById('rowWeakLayer').value || 0), slideRisk: Number(document.getElementById('rowSlideRisk').value || 0), surveyQuality: Number(document.getElementById('rowSurveyQuality').value || 0), techComplex: Number(document.getElementById('rowTechComplex').value || 0), constructionDiff: Number(document.getElementById('rowConstructionDiff').value || 0), equipmentDepend: Number(document.getElementById('rowEquipmentDepend').value || 0), techError: Number(document.getElementById('rowTechError').value || 0), materialSupply: Number(document.getElementById('rowMaterialSupply').value || 0), equipmentMobilize: Number(document.getElementById('rowEquipmentMobilize').value || 0), transportRisk: Number(document.getElementById('rowTransportRisk').value || 0), resourceShortage: Number(document.getElementById('rowResourceShortage').value || 0), siteManage: Number(document.getElementById('rowSiteManage').value || 0), coordinationRisk: Number(document.getElementById('rowCoordinationRisk').value || 0), scheduleRisk: Number(document.getElementById('rowScheduleRisk').value || 0), issueHandling: Number(document.getElementById('rowIssueHandling').value || 0), laborSafety: Number(document.getElementById('rowLaborSafety').value || 0), marineSafety: Number(document.getElementById('rowMarineSafety').value || 0), environmentRisk: Number(document.getElementById('rowEnvironmentRisk').value || 0), emergencyResponse: Number(document.getElementById('rowEmergencyResponse').value || 0), riskScore, riskLevel } };
}

async function saveDatasetRow() {
  if (!state.activeDatasetId) return document.getElementById('datasetStatus').textContent = 'Anh cần chọn một dataset ở A2 trước khi lưu.';
  const payload = getDatasetRowFormPayload();
  if (!payload.projectId || !payload.projectName || !payload.data.region) return document.getElementById('datasetStatus').textContent = 'Cần nhập tối thiểu mã công trình, tên công trình và vùng trước khi lưu.';
  const url = state.editingRowId != null ? `${API_BASE}/datasets/rows/${state.editingRowId}` : `${API_BASE}/datasets/${state.activeDatasetId}/rows`;
  const method = state.editingRowId != null ? 'PUT' : 'POST';
  const response = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  const result = await response.json();
  if (!response.ok) return document.getElementById('datasetStatus').textContent = result.detail || 'Không lưu được dòng dataset.';
  document.getElementById('datasetStatus').textContent = 'Đã lưu dữ liệu công trình vào dataset.';
  await loadDatasetRows(state.activeDatasetId);
  setWorkflowBtnState('createDatasetRowBtn', 'done');
}

async function deleteDatasetRow(rowId) {
  const response = await fetch(`${API_BASE}/datasets/rows/${rowId}`, { method: 'DELETE' });
  const result = await response.json();
  if (!response.ok) return document.getElementById('datasetStatus').textContent = result.detail || 'Không xóa được dòng dataset.';
  document.getElementById('datasetStatus').textContent = `Đã xóa dòng ${rowId}.`;
  await loadDatasetRows(state.activeDatasetId);
  closeDatasetModal();
}

function fillDatasetModal(row) {
  const d = row.data || {};
  DATASET_FIELDS.forEach(field => {
    const el = document.getElementById(`modal${field.charAt(0).toUpperCase()}${field.slice(1)}`);
    if (el) el.value = d[field] ?? '';
  });
}

function openDatasetModal(row) {
  state.editingRowId = row.id;
  fillDatasetModal(row);
  document.getElementById('datasetDetailModal').classList.remove('hidden');
}

function closeDatasetModal() {
  document.getElementById('datasetDetailModal').classList.add('hidden');
}

async function saveDatasetModal() {
  if (state.editingRowId == null) return;
  const payload = {
    projectId: document.getElementById('modalProjectId').value.trim(),
    projectName: document.getElementById('modalProjectName').value.trim(),
    riskScore: Number(document.getElementById('modalRiskScore').value || 0),
    riskLevel: document.getElementById('modalRiskLevel').value.trim() || inferRiskLevel(Number(document.getElementById('modalRiskScore').value || 0)),
    data: {
      projectId: document.getElementById('modalProjectId').value.trim(), region: document.getElementById('modalRegion').value.trim(), projectName: document.getElementById('modalProjectName').value.trim(), waveHeight: document.getElementById('modalWaveHeight').value, tideMode: document.getElementById('modalTideMode').value, windSpeed: document.getElementById('modalWindSpeed').value, stormLevel: document.getElementById('modalStormLevel').value, soilType: document.getElementById('modalSoilType').value, weakLayer: document.getElementById('modalWeakLayer').value, slideRisk: document.getElementById('modalSlideRisk').value, surveyQuality: document.getElementById('modalSurveyQuality').value, techComplex: document.getElementById('modalTechComplex').value, constructionDiff: document.getElementById('modalConstructionDiff').value, equipmentDepend: document.getElementById('modalEquipmentDepend').value, techError: document.getElementById('modalTechError').value, materialSupply: document.getElementById('modalMaterialSupply').value, equipmentMobilize: document.getElementById('modalEquipmentMobilize').value, transportRisk: document.getElementById('modalTransportRisk').value, resourceShortage: document.getElementById('modalResourceShortage').value, siteManage: document.getElementById('modalSiteManage').value, coordinationRisk: document.getElementById('modalCoordinationRisk').value, scheduleRisk: document.getElementById('modalScheduleRisk').value, issueHandling: document.getElementById('modalIssueHandling').value, laborSafety: document.getElementById('modalLaborSafety').value, marineSafety: document.getElementById('modalMarineSafety').value, environmentRisk: document.getElementById('modalEnvironmentRisk').value, emergencyResponse: document.getElementById('modalEmergencyResponse').value, riskScore: Number(document.getElementById('modalRiskScore').value || 0), riskLevel: document.getElementById('modalRiskLevel').value.trim() || inferRiskLevel(Number(document.getElementById('modalRiskScore').value || 0))
    }
  };
  const response = await fetch(`${API_BASE}/datasets/rows/${state.editingRowId}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  const result = await response.json();
  if (!response.ok) return document.getElementById('datasetStatus').textContent = result.detail || 'Không lưu được cập nhật chi tiết.';
  await loadDatasetRows(state.activeDatasetId);
  closeDatasetModal();
}

async function checkDatasetStructure() {
  const box = document.getElementById('datasetQualityBox');
  if (!state.datasetRows.length) return box.textContent = 'Chưa có dữ liệu để kiểm tra. Hệ thống cần có dữ liệu đã nạp ở bảng bên dưới.';
  const required = DATASET_FIELDS;
  const missing = [];
  state.datasetRows.forEach(row => {
    const data = row.data || {};
    required.forEach(field => {
      const value = data[field];
      if (value === null || value === undefined || String(value).trim() === '') missing.push(`Dòng ${row.id}: thiếu ${field}`);
    });
  });
  state.workflow.datasetChecked = true;
  refreshWorkflowChips();
  box.innerHTML = missing.length ? `Phát hiện thiếu dữ liệu hoặc thiếu cột:<br>${missing.slice(0, 20).join('<br>')}` : `Bảng dữ liệu đạt yêu cầu với <strong>${state.datasetRows.length}</strong> mẫu.`;
}

function renderDatasetRows() {
  const body = document.getElementById('datasetRowsBody');
  body.innerHTML = '';
  if (!state.datasetRows.length) return body.innerHTML = '<tr><td colspan="7" class="muted">Chưa có dòng dataset nào.</td></tr>';
  state.datasetRows.forEach(row => {
    const d = row.data || {};
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${row.id}</td><td>${d.projectId ?? ''}</td><td>${d.region ?? ''}</td><td>${d.projectName ?? ''}</td><td>${d.riskScore ?? ''}</td><td>${d.riskLevel ?? ''}</td><td><button class="ghost-btn" data-edit-row="${row.id}">Mở chi tiết</button> <button class="ghost-btn" data-delete-row="${row.id}">Xóa</button></td>`;
    body.appendChild(tr);
  });
  body.querySelectorAll('[data-delete-row]').forEach(btn => btn.addEventListener('click', () => deleteDatasetRow(Number(btn.dataset.deleteRow))));
  body.querySelectorAll('[data-edit-row]').forEach(btn => btn.addEventListener('click', () => {
    const row = state.datasetRows.find(item => item.id === Number(btn.dataset.editRow));
    if (row) openDatasetModal(row);
  }));
}

function initializeSplitStep() { if (!state.activeDatasetId) return document.getElementById('trainingStatus').textContent = 'Anh cần chọn dataset từ A2 trước khi chia train/test.'; state.workflow.trainSplit = true; refreshWorkflowChips(); const splitRatio = Number(document.getElementById('trainingSplitRatio').value || 0.8); document.getElementById('trainingStatus').textContent = `Đã chia dữ liệu theo tỷ lệ ${Math.round(splitRatio * 100)}/${Math.round((1 - splitRatio) * 100)}.`; }
function renderSugenoRuleTable(ruleSource, titleText = 'Bảng luật Sugeno khởi tạo') {
  const rows = (ruleSource || []).map((item, idx) => {
    const learnedParams = item.learnedParams || item.params || '-';
    const learnedOutput = item.learnedOutput || item.output || '-';
    return `
      <tr>
        <td>${item.rule || item.name || `R${idx + 1}`}</td>
        <td>${item.condition || '-'}</td>
        <td>${learnedOutput}</td>
        <td>${learnedParams}</td>
        <td>${item.weight || `w${idx + 1}`}</td>
        <td>w̄${idx + 1} = w${idx + 1} / Σw</td>
        <td>${item.status || 'Khởi tạo'}</td>
      </tr>
    `;
  }).join('');
  document.getElementById('trainingRulesBox').innerHTML = `
    <strong>${titleText}</strong>
    <table style="width:100%; margin-top:12px; border-collapse:collapse; min-width:unset;">
      <thead>
        <tr>
          <th>Luật</th>
          <th>Điều kiện</th>
          <th>Hàm kết quả</th>
          <th>Tham số</th>
          <th>Trọng số kích hoạt</th>
          <th>Trọng số chuẩn hóa</th>
          <th>Trạng thái</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
    <div style="margin-top:10px; color:#475569;">Các luật trên là bộ luật Sugeno theo tư duy ANFIS. Sau khi huấn luyện, các hệ số consequent sẽ được cập nhật từ dữ liệu train.</div>
    <div style="margin-top:12px; padding:10px 12px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:12px; color:#1e3a8a;">
      <strong>Công thức tổng hợp đầu ra:</strong><br>
      w̄i = wi / Σwi<br>
      y = Σ(w̄i · fi)
    </div>
  `;
}

function initializeSugenoRules() {
  if (!state.workflow.trainSplit) return document.getElementById('trainingStatus').textContent = 'Anh hãy chia train/test trước khi khởi tạo luật Sugeno.';
  state.workflow.sugenoReady = true;
  refreshWorkflowChips();
  renderSugenoRuleTable(SUGENO_RULES, 'Bảng luật Sugeno khởi tạo');
  document.getElementById('trainingRuleOriginBox').innerHTML = '<strong>Nguồn gốc luật:</strong> Bộ luật khởi tạo minh họa theo chuyên gia/seed rules. Sau khi huấn luyện, nếu backend sinh luật từ dữ liệu thì khu vực này sẽ hiển thị lại nguồn gốc data-driven.';
  document.getElementById('trainingStatus').textContent = 'Đã khởi tạo bảng luật Sugeno theo 6 biến đầu vào, sẵn sàng cho bước huấn luyện.';
}

async function runTraining() {
  const selectedDatasetId = Number(document.getElementById('trainingDatasetSelect')?.value || state.activeDatasetId || 0);
  if (selectedDatasetId) state.activeDatasetId = selectedDatasetId;
  updateTrainingDatasetSummary();
  const region = document.getElementById('trainingRegion').value.trim();
  const splitRatio = Number(document.getElementById('trainingSplitRatio').value || 0.8);
  const membership = document.getElementById('trainingMembership').value || 'gaussian';
  const ruleInitMode = document.getElementById('trainingRuleInitMode').value || 'data-driven';
  const epochs = Number(document.getElementById('trainingEpochs').value || 5);
  const patience = Number(document.getElementById('trainingPatience').value || 2);
  const premiseLr = Number(document.getElementById('trainingPremiseLr').value || 0.05);
  if (!state.workflow.trainSplit) return document.getElementById('trainingStatus').textContent = 'Anh cần thực hiện bước chia train/test trước.';
  if (!state.workflow.sugenoReady) return document.getElementById('trainingStatus').textContent = 'Anh cần khởi tạo luật Sugeno trước khi huấn luyện.';

  const memberships = membership === 'all' ? ['gaussian', 'gbell', 'triangular'] : [membership];
  let result = null;
  for (const membershipItem of memberships) {
    document.getElementById('trainingStatus').textContent = `Đang huấn luyện membership: ${membershipItem}...`;
    const response = await fetch(`${API_BASE}/training/run`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ region, split_ratio: splitRatio, membership: membershipItem, epochs, patience, premise_lr: premiseLr, rule_init_mode: ruleInitMode }) });
    result = await response.json();
    if (!response.ok) return document.getElementById('trainingStatus').textContent = result.detail || `Huấn luyện thất bại với membership ${membershipItem}.`;
  }

  state.workflow.trainRan = true;
  refreshWorkflowChips();
  document.getElementById('trainingStatus').textContent = membership === 'all'
    ? `Đã huấn luyện xong ${memberships.length} membership cho vùng ${region}.`
    : `Đã huấn luyện xong model ${result.modelName}. Train: ${result.trainCount}, Test: ${result.testCount}.`;
  document.getElementById('trainingMetrics').innerHTML = `Membership: <strong>${membership}</strong><br>Khởi tạo luật: <strong>${ruleInitMode}</strong><br>Số luật ứng viên: <strong>${result.artifact?.candidate_rule_count ?? '--'}</strong><br>Số luật sau pruning: <strong>${result.artifact?.pruned_rule_count ?? '--'}</strong><br>Premise learning rate: <strong>${premiseLr}</strong><br>MAE: <strong>${result.metrics.mae}</strong> | RMSE: <strong>${result.metrics.rmse}</strong> | R²: <strong>${result.metrics.r2}</strong><br>Số epoch thực tế: <strong>${result.metrics.epochs || 0}</strong><br>Best epoch: <strong>${result.metrics.best_epoch ?? '--'}</strong><br>Best test loss: <strong>${result.metrics.best_test_loss ?? '--'}</strong><br>Early stopping: <strong>${result.metrics.early_stopped ? 'Có' : 'Không'}</strong><br>Lịch sử loss: <strong>${(result.metrics.history || []).map(item => `E${item.epoch}(train:${item.train_loss}, test:${item.test_loss})`).join(' | ')}</strong>`;
  const artifactRules = result.artifact?.rules || [];
  const ruleInit = result.metrics?.rule_init_mode || result.artifact?.rule_init || 'seed/expert';
  document.getElementById('trainingRuleOriginBox').innerHTML = `<strong>Nguồn gốc luật:</strong> <strong>${ruleInit}</strong><br>${artifactRules.map((rule, idx) => `${rule.name || `R${idx + 1}`}: ${rule.origin || ruleInit} | Biến: ${Object.keys(rule.inputs || {}).join(', ') || '--'}`).join('<br>')}`;
  const candidateCount = result.artifact?.candidate_rule_count;
  const prunedCount = result.artifact?.pruned_rule_count;
  document.getElementById('trainingRulePruningNarrativeBox').innerHTML = ruleInit === 'pruned-grid'
    ? `<strong>Diễn giải học thuật về không gian luật:</strong><br>Hệ thống đã sinh đầy đủ <strong>${candidateCount ?? '--'}</strong> luật ứng viên từ không gian tổ hợp mờ của 6 chỉ tiêu tổng hợp nội bộ (3 mức mờ cho mỗi biến, tương ứng 3^6 tổ hợp). Sau đó, hệ thống thực hiện sàng lọc theo mức kích hoạt trên dữ liệu huấn luyện và giữ lại <strong>${prunedCount ?? '--'}</strong> luật có ý nghĩa nhất để huấn luyện mô hình ANFIS. Cách tiếp cận này giúp vừa bao phủ không gian luật đầy đủ, vừa tránh dư thừa và giảm độ phức tạp tính toán.`
    : `<strong>Diễn giải học thuật về không gian luật:</strong><br>Chế độ hiện tại sử dụng cơ chế khởi tạo luật <strong>${ruleInit}</strong>. Khi cần mở rộng không gian luật theo hướng đầy đủ và có sàng lọc, có thể sử dụng chế độ <strong>pruned-grid</strong> để sinh toàn bộ luật ứng viên rồi pruning trước khi huấn luyện.`;
  renderTrainingLossChart(result.metrics.history || [], result.metrics.best_epoch);
  renderTrainingConvergenceCharts(result.metrics.history || [], result.metrics.best_epoch);
  renderTrainingConvergenceNarrative(result.metrics.history || [], result.metrics.best_epoch);
  renderEpochComparisonTable(result.artifact?.epoch_snapshots || []);
  renderBestEpochSnapshot(result.metrics.best_epoch, result.metrics.best_test_loss, result.artifact?.epoch_snapshots || []);
  renderRuleEvolutionTimeline(result.artifact?.epoch_snapshots || []);
  renderMembershipCurves(result.artifact?.rules || []);
  renderPremiseDrift(result.artifact?.epoch_snapshots || []);
  const baseline = result.metrics.baseline_compare || {};
  document.getElementById('baselineCompareBox').innerHTML = `ANFIS → MAE: <strong>${baseline.anfis?.mae ?? '--'}</strong>, RMSE: <strong>${baseline.anfis?.rmse ?? '--'}</strong>, R²: <strong>${baseline.anfis?.r2 ?? '--'}</strong><br>ANN baseline → MAE: <strong>${baseline.ann?.mae ?? '--'}</strong>, RMSE: <strong>${baseline.ann?.rmse ?? '--'}</strong>, R²: <strong>${baseline.ann?.r2 ?? '--'}</strong><br>Fuzzy baseline → MAE: <strong>${baseline.fuzzy?.mae ?? '--'}</strong>, RMSE: <strong>${baseline.fuzzy?.rmse ?? '--'}</strong>, R²: <strong>${baseline.fuzzy?.r2 ?? '--'}</strong>`;
  const anfisR2 = Number(baseline.anfis?.r2 ?? 0);
  const annR2 = Number(baseline.ann?.r2 ?? 0);
  const better = anfisR2 > annR2 ? 'ANFIS đang cho kết quả nhỉnh hơn ANN trên thước đo R².' : (anfisR2 < annR2 ? 'ANN đang cho kết quả nhỉnh hơn ANFIS trên thước đo R².' : 'ANFIS và ANN đang cho kết quả tương đương trên thước đo R².');
  const diff = Math.abs(anfisR2 - annR2).toFixed(6);
  document.getElementById('anfisAnnCompareBox').innerHTML = `<strong>Đối chiếu trọng tâm:</strong> ANFIS (R² = <strong>${baseline.anfis?.r2 ?? '--'}</strong>) so với ANN (R² = <strong>${baseline.ann?.r2 ?? '--'}</strong>).<br>${better}<br>Độ chênh lệch |ΔR²| = <strong>${diff}</strong>.`;
  renderRuleInitCompare(result);
  if (result.artifact?.rules?.length) {
    const learnedRules = result.artifact.rules.map((rule, idx) => ({
      rule: rule.name || `R${idx + 1}`,
      condition: Object.entries(rule.inputs || {}).map(([k, v]) => {
        const label = Array.isArray(v) ? v[0] : '';
        const kind = Array.isArray(v) ? v[1] : '';
        return `${k} ${label} [${kind}]`;
      }).join(', '),
      learnedOutput: `${Object.entries(rule.coeffs || {}).map(([k, v]) => `${Number(v).toFixed(4)}·${k}`).join(' + ')} + ${Number(rule.bias || 0).toFixed(4)}`,
      learnedParams: `${Object.entries(rule.coeffs || {}).map(([k, v]) => `${k}:${Number(v).toFixed(4)}`).join(' | ')} | c:${Number(rule.bias || 0).toFixed(4)}`,
      weight: `w${idx + 1}`,
      status: `${rule.status || 'Learned'}${rule.origin ? ` | ${rule.origin}` : ''}`
    }));
    renderSugenoRuleTable(learnedRules, 'Bảng luật Sugeno sau huấn luyện');
  }
  syncRegionInputs(result.region || region, true);
  await loadModels(result.region || region);
}

function evaluateTraining() { const html = document.getElementById('trainingMetrics').innerText; if (!state.workflow.trainRan || !html.trim()) return document.getElementById('trainingConclusion').textContent = 'Cần huấn luyện mô hình trước khi kiểm định.'; state.workflow.trainEvaluated = true; refreshWorkflowChips(); let conclusion = 'Mô hình đạt độ tin cậy khá.'; const match = html.match(/R²[:\s]*([0-9.-]+)/); const r2 = match ? Number(match[1]) : null; if (r2 != null) conclusion = r2 >= 0.8 ? 'Mô hình có độ tin cậy tốt, có thể ưu tiên khai thác.' : (r2 >= 0.6 ? 'Mô hình có độ tin cậy khá, nên tiếp tục bổ sung dữ liệu để cải thiện.' : 'Mô hình chưa đạt độ tin cậy cao, cần rà soát dữ liệu và cấu hình huấn luyện.'); document.getElementById('trainingConclusion').textContent = conclusion; }

async function loadModels(region = '') { state.lastModelRegionFilter = region; const filterInput = document.getElementById('modelRegionFilter'); if (filterInput && region) filterInput.value = region; const url = region ? `${API_BASE}/models?region=${encodeURIComponent(region)}` : `${API_BASE}/models`; const response = await fetch(url); state.models = await response.json(); document.getElementById('modelStatus').textContent = state.models.length ? `Đã tải ${state.models.length} model.` : 'Chưa có model nào.'; renderModels(); renderModelSelectOptions(); }
function renderMembershipMetricChart(elementId, bestByGroup, metricKey, labelPrefix, inverse = false) {
  const chart = document.getElementById(elementId);
  if (!chart) return;
  if (!bestByGroup.length) {
    chart.textContent = `Chưa có dữ liệu biểu đồ ${metricKey}.`;
    return;
  }
  const values = bestByGroup.map(item => Number(item.best.metrics?.[metricKey] || 0));
  const maxValue = Math.max(...values, 0.001);
  chart.innerHTML = bestByGroup.map(item => {
    const val = Number(item.best.metrics?.[metricKey] || 0);
    const normalized = inverse ? (maxValue - val + 0.001) : val;
    const height = Math.max(12, (normalized / maxValue) * 180);
    return `<div class="chart-bar-col"><div class="chart-value">${labelPrefix}=${val.toFixed(4)}</div><div class="chart-bar" style="height:${height}px"></div><div class="chart-label">${item.membership}</div></div>`;
  }).join('');
}

function getComparableModels() {
  return state.models.filter(model => model.metrics?.membership && model.metrics?.rule_init_mode);
}

function renderRuleInitCompare(currentResult = null) {
  const a3Box = document.getElementById('ruleInitCompareBox');
  const a4Box = document.getElementById('ruleInitSummaryBox');
  const comparableModels = getComparableModels();
  if (!comparableModels.length && !currentResult) {
    if (a3Box) a3Box.textContent = 'Chưa có dữ liệu so sánh kiểu khởi tạo luật.';
    if (a4Box) a4Box.textContent = 'Chưa có dữ liệu so sánh kiểu khởi tạo luật.';
    return;
  }
  const grouped = {};
  comparableModels.forEach(model => {
    const key = model.metrics?.rule_init_mode || model.metrics?.rule_init || 'seed';
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(model);
  });
  const bestByRuleInit = Object.entries(grouped).map(([ruleInit, models]) => {
    const best = models.reduce((a, b) => Number(a.metrics?.r2 || -999) > Number(b.metrics?.r2 || -999) ? a : b);
    return { ruleInit, best, count: models.length };
  });
  const currentText = currentResult ? `<strong>Lượt train hiện tại:</strong><br>Model: <strong>${currentResult.modelName || '--'}</strong><br>Khởi tạo luật: <strong>${currentResult.metrics?.rule_init_mode || currentResult.artifact?.rule_init || '--'}</strong><br>MAE=${currentResult.metrics?.mae ?? '--'} | RMSE=${currentResult.metrics?.rmse ?? '--'} | R²=${currentResult.metrics?.r2 ?? '--'}<br><br>` : '';
  const historyTitle = bestByRuleInit.length ? '<strong>Model tốt nhất trong lịch sử theo từng kiểu khởi tạo:</strong><br>' : '';
  const summary = currentText + historyTitle + bestByRuleInit.map(item => `<strong>${item.ruleInit}</strong>: ${item.count} model | tốt nhất: <strong>${item.best.modelName}</strong> | MAE=${item.best.metrics?.mae ?? '--'} | RMSE=${item.best.metrics?.rmse ?? '--'} | R²=${item.best.metrics?.r2 ?? '--'}`).join('<br>');
  if (a3Box) a3Box.innerHTML = summary || 'Chưa có dữ liệu so sánh kiểu khởi tạo luật.';
  if (a4Box) a4Box.innerHTML = summary || 'Chưa có dữ liệu so sánh kiểu khởi tạo luật.';
}

function renderMembershipCompare() {
  const box = document.getElementById('membershipCompareBox');
  const comparableModels = getComparableModels();
  if (!state.models.length) {
    box.textContent = 'Chưa có dữ liệu so sánh membership.';
    renderMembershipMetricChart('membershipCompareChartR2', [], 'r2', 'R²');
    renderMembershipMetricChart('membershipCompareChartMae', [], 'mae', 'MAE');
    renderMembershipMetricChart('membershipCompareChartRmse', [], 'rmse', 'RMSE');
    renderRuleInitCompare();
    return;
  }
  const grouped = {};
  comparableModels.forEach(model => {
    const key = model.metrics?.membership || 'gaussian';
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(model);
  });
  const bestByGroup = Object.entries(grouped).map(([membership, models]) => {
    const best = models.reduce((a, b) => Number(a.metrics?.r2 || -999) > Number(b.metrics?.r2 || -999) ? a : b);
    return { membership, best, count: models.length };
  });
  box.innerHTML = bestByGroup.map(item => `<strong>${item.membership}</strong>: ${item.count} model | tốt nhất: <strong>${item.best.modelName}</strong> | R²=${item.best.metrics?.r2 ?? '--'} | MAE=${item.best.metrics?.mae ?? '--'} | RMSE=${item.best.metrics?.rmse ?? '--'}`).join('<br>');
  renderMembershipMetricChart('membershipCompareChartR2', bestByGroup, 'r2', 'R²');
  renderMembershipMetricChart('membershipCompareChartMae', bestByGroup, 'mae', 'MAE', true);
  renderMembershipMetricChart('membershipCompareChartRmse', bestByGroup, 'rmse', 'RMSE', true);
  renderRuleInitCompare();
}

function renderModels() { const body = document.getElementById('modelsBody'); const defaultBox = document.getElementById('defaultModelSummary'); body.innerHTML = ''; if (!state.models.length) { body.innerHTML = '<tr><td colspan="7" class="muted">Chưa có model nào.</td></tr>'; defaultBox.textContent = 'Chưa xác định model mặc định.'; renderMembershipCompare(); return; } const defaultModel = state.models.find(model => model.isDefault); const comparableCount = getComparableModels().length; defaultBox.innerHTML = defaultModel ? `Model mặc định hiện tại: <strong>${defaultModel.modelName}</strong><br><span class="muted">Model có đủ metadata ANFIS sâu để so sánh: ${comparableCount}/${state.models.length}</span>` : 'Chưa có model mặc định cho vùng hiện tại.'; state.models.forEach(model => { const legacyBadge = model.isLegacy ? ' <span style="color:#b45309; font-weight:700;">(Legacy)</span>' : ' <span style="color:#166534; font-weight:700;">(Artifact)</span>'; const membership = model.metrics?.membership || '--'; const ruleInitBadge = model.metrics?.rule_init_mode ? ` <span style="color:#1d4ed8; font-weight:700;">[${model.metrics.rule_init_mode}]</span>` : ' <span style="color:#94a3b8; font-weight:700;">[thiếu metadata]</span>'; const tr = document.createElement('tr'); tr.innerHTML = `<td>${model.id}</td><td>${model.modelName}${legacyBadge}${ruleInitBadge}</td><td>${model.modelType}</td><td>${membership}</td><td>${model.isDefault ? 'Mặc định' : 'Đã lưu'}</td><td>${model.metrics?.mae ?? '--'} / ${model.metrics?.rmse ?? '--'} / ${model.metrics?.r2 ?? '--'}</td><td><button class="ghost-btn" data-pick-model="${model.id}">Chọn</button> <button class="ghost-btn" data-set-default="${model.id}">Đặt mặc định</button></td>`; body.appendChild(tr); }); body.querySelectorAll('[data-set-default]').forEach(btn => btn.addEventListener('click', () => setDefaultModel(Number(btn.dataset.setDefault)))); body.querySelectorAll('[data-pick-model]').forEach(btn => btn.addEventListener('click', () => { state.activeModelId = Number(btn.dataset.pickModel); document.getElementById('modelStatus').textContent = `Đã chọn model #${state.activeModelId} để dùng cho báo cáo A3.`; refreshWorkflowButtonHints(); })); renderMembershipCompare(); }
function renderModelSelectOptions() { const select = document.getElementById('predictionModelSelect'); const hintBox = document.getElementById('predictionModelHint'); if (!select) return; select.innerHTML = '<option value="">Chọn model</option>'; let defaultModelName = ''; state.models.forEach(model => { const option = document.createElement('option'); option.value = model.modelName; option.textContent = `${model.modelName}${model.isDefault ? ' (mặc định)' : ''}`; if (model.isDefault) defaultModelName = model.modelName; select.appendChild(option); }); if (defaultModelName) { select.value = defaultModelName; hintBox.textContent = `Đang ưu tiên model mặc định: ${defaultModelName}`; } }
async function setDefaultModel(modelId) { const response = await fetch(`${API_BASE}/models/${modelId}/set-default`, { method: 'POST' }); const result = await response.json(); if (!response.ok) return document.getElementById('modelStatus').textContent = result.detail || 'Không đặt được model mặc định.'; document.getElementById('modelStatus').textContent = `Đã đặt ${result.modelName} làm model mặc định.`; await loadModels(state.lastModelRegionFilter || document.getElementById('trainingRegion').value.trim()); }
function predictionAdvice(score) { if (score < 2) return 'Rủi ro thấp: tiếp tục duy trì kiểm soát hiện trường và theo dõi định kỳ.'; if (score < 3) return 'Rủi ro trung bình: cần theo dõi chặt các nhóm yếu tố có biến động lớn.'; if (score < 4) return 'Rủi ro cao: cần bổ sung biện pháp kỹ thuật, tăng giám sát và điều phối thi công.'; return 'Rủi ro rất cao: cần rà soát tổng thể phương án thi công, an toàn, logistics và điều hành.'; }
function dominantFactorInfo(inputs) {
  const mapping = {
    X1: 'Nhóm 1 - Điều kiện tự nhiên',
    X2: 'Nhóm 2 - Địa chất - nền móng',
    X3: 'Nhóm 3 - Kỹ thuật - công nghệ',
    X4: 'Nhóm 4 - Vật liệu - logistics',
    X5: 'Nhóm 5 - Tổ chức - quản lý',
    X6: 'Nhóm 6 - An toàn - môi trường',
  };
  const entries = Object.entries(inputs || {});
  if (!entries.length) return null;
  const [key, value] = entries.reduce((best, current) => Number(current[1]) > Number(best[1]) ? current : best);
  return { key, value: Number(value), label: mapping[key] || key };
}
function renderPredictionBarChart(inputs) {
  const root = document.getElementById('predictionBarChart');
  const labels = {
    X1: 'Tự nhiên', X2: 'Địa chất', X3: 'Kỹ thuật', X4: 'Logistics', X5: 'Quản lý', X6: 'AT-MT'
  };
  const entries = Object.entries(inputs || {});
  if (!entries.length) return root.textContent = 'Chưa có dữ liệu biểu đồ.';
  const max = Math.max(...entries.map(([, value]) => Number(value) || 0), 5);
  root.innerHTML = entries.map(([key, value]) => {
    const num = Number(value) || 0;
    const height = Math.max(12, (num / max) * 180);
    return `<div class="chart-bar-col"><div class="chart-value">${num.toFixed(2)}</div><div class="chart-bar" style="height:${height}px"></div><div class="chart-label">${key}</div><div class="chart-label">${labels[key] || key}</div></div>`;
  }).join('');
}
function renderPredictionRadarChart(inputs) {
  const root = document.getElementById('predictionRadarChart');
  root.innerHTML = '';
  const entries = Object.entries(inputs || {});
  if (!entries.length) return root.textContent = 'Chưa có dữ liệu biểu đồ.';
  const center = 150;
  const radius = 105;
  const levels = [0.2, 0.4, 0.6, 0.8, 1];
  const points = entries.map(([key, value], index) => {
    const angle = (-Math.PI / 2) + (index * 2 * Math.PI / entries.length);
    const scaled = (Number(value) || 0) / 5;
    const x = center + Math.cos(angle) * radius * scaled;
    const y = center + Math.sin(angle) * radius * scaled;
    const labelX = center + Math.cos(angle) * (radius + 24);
    const labelY = center + Math.sin(angle) * (radius + 24);
    return { key, value: Number(value) || 0, x, y, angle, labelX, labelY };
  });
  const polygon = points.map(p => `${p.x},${p.y}`).join(' ');
  const grid = levels.map(level => {
    const g = entries.map((_, index) => {
      const angle = (-Math.PI / 2) + (index * 2 * Math.PI / entries.length);
      const x = center + Math.cos(angle) * radius * level;
      const y = center + Math.sin(angle) * radius * level;
      return `${x},${y}`;
    }).join(' ');
    return `<polygon points="${g}" fill="none" stroke="#cbd5e1" stroke-width="1" />`;
  }).join('');
  const spokes = entries.map((_, index) => {
    const angle = (-Math.PI / 2) + (index * 2 * Math.PI / entries.length);
    const x = center + Math.cos(angle) * radius;
    const y = center + Math.sin(angle) * radius;
    return `<line x1="${center}" y1="${center}" x2="${x}" y2="${y}" stroke="#cbd5e1" stroke-width="1" />`;
  }).join('');
  const labels = points.map(p => `<text x="${p.labelX}" y="${p.labelY}" text-anchor="middle" font-size="12" fill="#334155">${p.key}</text>`).join('');
  root.innerHTML = `<div class="radar-wrap"><svg class="radar-svg" viewBox="0 0 300 300">${grid}${spokes}<polygon points="${polygon}" fill="rgba(37,99,235,0.25)" stroke="#2563eb" stroke-width="2" />${points.map(p => `<circle cx="${p.x}" cy="${p.y}" r="4" fill="#2563eb" />`).join('')}${labels}</svg></div>`;
}

function renderPredictionRuleDetails(ruleDetails) {
  const body = document.getElementById('predictionRuleBody');
  body.innerHTML = '';
  if (!ruleDetails || !ruleDetails.length) {
    body.innerHTML = '<tr><td colspan="4" class="muted">Chưa có chi tiết suy diễn.</td></tr>';
    return;
  }
  ruleDetails.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${item.rule}</td><td>${Number(item.weight || 0).toFixed(6)}</td><td>${Number(item.normalized_weight || 0).toFixed(6)}</td><td>${Number(item.consequent || 0).toFixed(6)}</td>`;
    body.appendChild(tr);
  });
}

function renderTrainingLossChart(history, bestEpoch = null) {
  const root = document.getElementById('trainingLossChart');
  if (!history || !history.length) {
    root.textContent = 'Chưa có dữ liệu loss theo epoch.';
    return;
  }
  const max = Math.max(...history.flatMap(item => [Number(item.train_loss) || 0, Number(item.test_loss) || 0]), 0.001);
  root.innerHTML = history.map(item => {
    const trainLoss = Number(item.train_loss) || 0;
    const testLoss = Number(item.test_loss) || 0;
    const trainHeight = Math.max(12, (trainLoss / max) * 160);
    const testHeight = Math.max(12, (testLoss / max) * 160);
    const highlight = Number(bestEpoch) === Number(item.epoch) ? 'box-shadow:0 0 0 3px rgba(16,185,129,0.25); border-radius:12px; padding:6px;' : '';
    return `<div class="chart-bar-col" style="${highlight}"><div class="chart-value">T:${trainLoss.toFixed(4)} | V:${testLoss.toFixed(4)}</div><div style="display:flex; gap:8px; align-items:end;"><div class="chart-bar train-bar" style="height:${trainHeight}px;"></div><div class="chart-bar test-bar" style="height:${testHeight}px;"></div></div><div class="chart-label">E${item.epoch}${Number(bestEpoch) === Number(item.epoch) ? ' ★' : ''}</div></div>`;
  }).join('');
}

function renderTrainingConvergenceNarrative(history, bestEpoch = null) {
  const box = document.getElementById('trainingChartNarrativeBox');
  if (!box) return;
  if (!history || !history.length) {
    box.textContent = 'Chưa có diễn giải trực quan quá trình huấn luyện.';
    return;
  }
  const first = history[0] || {};
  const last = history[history.length - 1] || {};
  const firstTrain = Number(first.train_loss || 0);
  const lastTrain = Number(last.train_loss || 0);
  const firstTest = Number(first.test_loss || 0);
  const lastTest = Number(last.test_loss || 0);
  const firstGap = Math.abs(firstTest - firstTrain);
  const lastGap = Math.abs(lastTest - lastTrain);
  const gapTrend = lastGap < firstGap ? 'thu hẹp dần' : (lastGap > firstGap ? 'mở rộng hơn' : 'giữ gần như ổn định');
  const totalImprove = firstTest - lastTest;
  const improveText = totalImprove > 0 ? `Test loss giảm từ <strong>${firstTest.toFixed(4)}</strong> xuống <strong>${lastTest.toFixed(4)}</strong>, cho thấy mô hình đang hội tụ theo hướng tích cực.` : `Test loss không giảm rõ rệt (từ <strong>${firstTest.toFixed(4)}</strong> xuống <strong>${lastTest.toFixed(4)}</strong>), cần lưu ý khả năng hội tụ chậm hoặc bão hòa sớm.`;
  const bestText = bestEpoch ? `Epoch tốt nhất hiện tại là <strong>E${bestEpoch}</strong>, đây là mốc nên ưu tiên dùng để phân tích và báo cáo.` : 'Chưa xác định được epoch tốt nhất.';
  const lateSteps = history.slice(1).map((item, idx) => (Number(history[idx].test_loss || 0) - Number(item.test_loss || 0)));
  const avgLateImprove = lateSteps.length ? lateSteps.reduce((a, b) => a + b, 0) / lateSteps.length : 0;
  const stabilityText = avgLateImprove > 0.001 ? 'Tốc độ cải thiện vẫn còn rõ, mô hình còn khả năng học thêm nếu tăng epoch hợp lý.' : 'Tốc độ cải thiện đã nhỏ dần, mô hình đang tiến tới vùng ổn định/hội tụ.';
  box.innerHTML = `${improveText}<br>Khoảng cách giữa train loss và test loss đang <strong>${gapTrend}</strong> (từ ${firstGap.toFixed(4)} xuống ${lastGap.toFixed(4)}).<br>${stabilityText}<br>${bestText}`;
}

function renderTrainingConvergenceCharts(history, bestEpoch = null) {
  const convergenceRoot = document.getElementById('trainingConvergenceChart');
  const gapRoot = document.getElementById('trainingGapChart');
  const improvementRoot = document.getElementById('trainingImprovementChart');
  if (!history || !history.length) {
    if (convergenceRoot) convergenceRoot.textContent = 'Chưa có dữ liệu hội tụ.';
    if (gapRoot) gapRoot.textContent = 'Chưa có dữ liệu khoảng cách hội tụ.';
    if (improvementRoot) improvementRoot.textContent = 'Chưa có dữ liệu cải thiện loss.';
    return;
  }
  const maxLoss = Math.max(...history.flatMap(item => [Number(item.train_loss) || 0, Number(item.val_loss) || 0, Number(item.test_loss) || 0]), 0.001);
  if (convergenceRoot) {
    convergenceRoot.innerHTML = history.map(item => {
      const train = Number(item.train_loss) || 0;
      const val = Number(item.val_loss) || 0;
      const test = Number(item.test_loss) || 0;
      const isBest = bestEpoch && Number(item.epoch) === Number(bestEpoch);
      const trainH = Math.max(10, (train / maxLoss) * 180);
      const valH = Math.max(10, (val / maxLoss) * 180);
      const testH = Math.max(10, (test / maxLoss) * 180);
      return `<div class="chart-bar-col"><div class="chart-value">E${item.epoch}${isBest ? ' ★' : ''}</div><div style="display:flex; gap:5px; align-items:end;"><div class="chart-bar train-bar" style="height:${trainH}px"></div><div class="chart-bar val-bar" style="height:${valH}px"></div><div class="chart-bar test-bar" style="height:${testH}px"></div></div><div class="chart-label">Train / Val / Test</div></div>`;
    }).join('');
  }
  if (gapRoot) {
    gapRoot.innerHTML = history.map(item => {
      const train = Number(item.train_loss) || 0;
      const test = Number(item.test_loss) || 0;
      const gap = Math.abs(test - train);
      const gapH = Math.max(12, (gap / Math.max(maxLoss, 0.001)) * 200);
      return `<div class="chart-bar-col"><div class="chart-value">Gap=${gap.toFixed(4)}</div><div class="chart-bar gap-bar" style="height:${gapH}px"></div><div class="chart-label">E${item.epoch}</div></div>`;
    }).join('');
  }
  if (improvementRoot) {
    improvementRoot.innerHTML = history.map((item, index) => {
      const prev = index === 0 ? null : Number(history[index - 1].test_loss) || 0;
      const curr = Number(item.test_loss) || 0;
      const improvement = prev == null ? 0 : (prev - curr);
      const h = Math.max(12, (Math.abs(improvement) / Math.max(maxLoss, 0.001)) * 200);
      const colorClass = improvement >= 0 ? 'improve-bar' : 'worse-bar';
      const label = index === 0 ? 'Khởi tạo' : `${improvement >= 0 ? '↓' : '↑'} ${Math.abs(improvement).toFixed(4)}`;
      return `<div class="chart-bar-col"><div class="chart-value">${label}</div><div class="chart-bar ${colorClass}" style="height:${h}px"></div><div class="chart-label">E${item.epoch}</div></div>`;
    }).join('');
  }
}

function renderEpochComparisonTable(snapshots) {
  const body = document.getElementById('trainingEpochCompareBody');
  body.innerHTML = '';
  if (!snapshots || snapshots.length < 2) {
    body.innerHTML = '<tr><td colspan="3" class="muted">Chưa có dữ liệu so sánh epoch.</td></tr>';
    return;
  }
  const first = snapshots[0];
  const last = snapshots[snapshots.length - 1];
  const firstRules = first.rules || [];
  const lastRules = last.rules || [];
  lastRules.forEach((rule, idx) => {
    const before = firstRules[idx] || {};
    const after = rule || {};
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${after.name || `R${idx + 1}`}</td><td>${Object.entries(before.coeffs || {}).map(([k,v]) => `${k}:${Number(v).toFixed(3)}`).join(' | ')} | c:${Number(before.bias || 0).toFixed(3)}</td><td>${Object.entries(after.coeffs || {}).map(([k,v]) => `${k}:${Number(v).toFixed(3)}`).join(' | ')} | c:${Number(after.bias || 0).toFixed(3)}</td>`;
    body.appendChild(tr);
  });
}

function renderBestEpochSnapshot(bestEpoch, bestLoss, snapshots) {
  const box = document.getElementById('bestEpochSnapshotBox');
  if (!snapshots || !snapshots.length || !bestEpoch) {
    box.textContent = 'Chưa có snapshot tốt nhất.';
    return;
  }
  const snap = snapshots.find(item => Number(item.epoch) === Number(bestEpoch));
  if (!snap) {
    box.textContent = 'Không tìm thấy snapshot của best epoch.';
    return;
  }
  box.innerHTML = `<strong>Best epoch:</strong> ${bestEpoch}<br><strong>Best test loss:</strong> ${bestLoss ?? '--'}<br><strong>Số luật:</strong> ${(snap.rules || []).length}<br>${(snap.rules || []).map(rule => `${rule.name}: ${Object.entries(rule.coeffs || {}).map(([k,v]) => `${k}:${Number(v).toFixed(3)}`).join(', ')} | c:${Number(rule.bias || 0).toFixed(3)}`).join('<br>')}`;
}

function renderRuleEvolutionTimeline(snapshots) {
  const root = document.getElementById('trainingRuleTimeline');
  if (!snapshots || !snapshots.length) {
    root.textContent = 'Chưa có dữ liệu evolution.';
    return;
  }
  root.innerHTML = snapshots.map(snap => `<div class="timeline-card"><div class="timeline-title">Epoch ${snap.epoch}</div><div class="timeline-meta">${(snap.rules || []).map(rule => `${rule.name}: ${Object.entries(rule.coeffs || {}).map(([k,v]) => `${k}:${Number(v).toFixed(3)}`).join(' | ')} | c:${Number(rule.bias || 0).toFixed(3)}`).join('<br>')}</div></div>`).join('');
}

function membershipValue(kind, x, p1, p2, p3) {
  if (kind === 'triangular') {
    if (x <= p1 || x >= p3) return 0;
    if (x === p2) return 1;
    if (x < p2) return (x - p1) / Math.max(p2 - p1, 0.1);
    return (p3 - x) / Math.max(p3 - p2, 0.1);
  }
  if (kind === 'gbell') {
    return 1 / (1 + Math.abs((x - p3) / Math.max(p1, 0.1)) ** (2 * Math.max(p2, 0.1)));
  }
  return Math.exp(-((x - p1) ** 2) / (2 * Math.max(p2, 0.1) ** 2));
}

function renderMembershipCurves(rules) {
  const root = document.getElementById('membershipCurveBox');
  if (!rules || !rules.length) {
    root.textContent = 'Chưa có dữ liệu membership curves.';
    return;
  }
  const seen = new Map();
  rules.forEach(rule => {
    Object.entries(rule.inputs || {}).forEach(([key, v]) => {
      if (!seen.has(key)) seen.set(key, []);
      seen.get(key).push(v);
    });
  });
  root.innerHTML = Array.from(seen.entries()).map(([key, defs]) => {
    const uniqueDefs = defs.slice(0, 3);
    const width = 520, height = 220, pad = 30;
    const colors = ['#2563eb', '#16a34a', '#d97706'];
    const polylines = uniqueDefs.map((def, idx) => {
      const [label, kind, p1, p2, p3] = def;
      const pts = [];
      for (let i = 0; i <= 100; i++) {
        const xVal = 1 + (i / 100) * 4;
        const yVal = membershipValue(kind, xVal, Number(p1), Number(p2), p3 == null ? null : Number(p3));
        const x = pad + (i / 100) * (width - pad * 2);
        const y = height - pad - yVal * (height - pad * 2);
        pts.push(`${x},${y}`);
      }
      return `<polyline fill="none" stroke="${colors[idx % colors.length]}" stroke-width="2" points="${pts.join(' ')}" /><text x="${pad + 8}" y="${24 + idx * 16}" fill="${colors[idx % colors.length]}" font-size="12">${label} [${kind}]</text>`;
    }).join('');
    return `<div class="membership-curve-card"><div class="membership-curve-title">${key}</div><svg class="membership-curve-svg" viewBox="0 0 ${width} ${height}"><rect x="0" y="0" width="${width}" height="${height}" fill="#fff" /><line x1="${pad}" y1="${height - pad}" x2="${width - pad}" y2="${height - pad}" stroke="#94a3b8" /><line x1="${pad}" y1="${pad}" x2="${pad}" y2="${height - pad}" stroke="#94a3b8" />${polylines}</svg></div>`;
  }).join('');
}

function renderPremiseDrift(snapshots) {
  const body = document.getElementById('premiseDriftBody');
  body.innerHTML = '';
  if (!snapshots || !snapshots.length) {
    body.innerHTML = '<tr><td colspan="4" class="muted">Chưa có dữ liệu biến động premise.</td></tr>';
    return;
  }
  snapshots.forEach(snap => {
    const premise = snap.premise || {};
    Object.entries(premise).forEach(([ruleName, variables]) => {
      Object.entries(variables).forEach(([varName, info]) => {
        const tr = document.createElement('tr');
        const p3Text = info.p3 == null ? '-' : Number(info.p3).toFixed(4);
        tr.innerHTML = `<td>E${snap.epoch}</td><td>${ruleName}</td><td>${varName}</td><td>${info.kind} | p1=${Number(info.p1).toFixed(4)} | p2=${Number(info.p2).toFixed(4)} | p3=${p3Text}</td>`;
        body.appendChild(tr);
      });
    });
  });
}
async function runPrediction() { const internalVector = fillPredictionInputsFromB1(); const region = document.getElementById('predictionRegion').value.trim(); const modelName = document.getElementById('predictionModelSelect').value; const projectStage = document.getElementById('rowProjectStage')?.value || ''; const projectName = document.getElementById('rowProjectName')?.value?.trim() || 'prediction-session'; if (Object.values(internalVector).some(v => v == null || Number(v) <= 0)) return document.getElementById('predictionStatus').textContent = 'Anh hãy nhập và xử lý đầy đủ hồ sơ công trình trước khi dự báo.'; const payload = { region, model_name: modelName, project_stage: projectStage, project_name: projectName, inputs: { X1: Number(internalVector.X1 || 0), X2: Number(internalVector.X2 || 0), X3: Number(internalVector.X3 || 0), X4: Number(internalVector.X4 || 0), X5: Number(internalVector.X5 || 0), X6: Number(internalVector.X6 || 0) } }; if (!region || !modelName) return document.getElementById('predictionStatus').textContent = 'Anh cần nhập vùng và chọn model trước khi dự báo.'; const response = await fetch(`${API_BASE}/predictions/run`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }); const result = await response.json(); if (!response.ok) return document.getElementById('predictionStatus').textContent = result.detail || 'Dự báo thất bại.'; document.getElementById('predictionStatus').textContent = `Đã dự báo bằng model ${result.modelName}.`; document.getElementById('predictionResult').innerHTML = `Điểm rủi ro: <strong>${result.score}</strong> | Mức rủi ro: <strong>${result.riskLevel}</strong>`; document.getElementById('predictionAdvice').textContent = predictionAdvice(Number(result.score)); const dominant = dominantFactorInfo(payload.inputs); document.getElementById('predictionDominantBox').innerHTML = dominant ? `Nhóm rủi ro nổi trội nhất: <strong>${dominant.label}</strong> (${dominant.key} = ${dominant.value.toFixed(2)}). Giai đoạn thi công: <strong>${projectStage || 'Chưa chọn'}</strong>.` : 'Chưa xác định được nhóm rủi ro nổi trội nhất.'; const rec = result.recommendations || {}; const stakeholders = rec.stakeholderActions || {}; const riskMatrix = rec.riskMatrix || result.riskMatrix || {}; document.getElementById('predictionRiskMatrixBox').innerHTML = `<strong>Ma trận rủi ro nội bộ:</strong><br>Likelihood = <strong>${riskMatrix.likelihood ?? '--'}</strong> | Impact = <strong>${riskMatrix.impact ?? '--'}</strong> | Matrix Score = <strong>${riskMatrix.matrixScore ?? '--'}</strong>`; document.getElementById('predictionRecommendationBox').innerHTML = `<strong>Nhận định điều hành:</strong> ${rec.summary || 'Chưa có khuyến nghị.'}<br><br>${rec.managementMessage || ''}<br><br><strong>Giai đoạn thi công:</strong> ${rec.projectStage || projectStage || 'Chưa chọn'}<br><br><strong>Hành động cần ưu tiên ngay:</strong><br>${(rec.immediateActions || []).map(item => `- ${item}`).join('<br>') || 'Chưa có.'}<br><br><strong>Biện pháp kiểm soát trọng tâm:</strong><br>${(rec.priorityActions || []).map(item => `- ${item}`).join('<br>') || 'Chưa có.'}<br><br><strong>Nội dung cần theo dõi liên tục:</strong><br>${(rec.monitoringActions || []).map(item => `- ${item}`).join('<br>') || 'Chưa có.'}<br><br><strong>Kiến nghị cho Ban chỉ huy công trường:</strong><br>${(stakeholders.siteCommand || []).map(item => `- ${item}`).join('<br>') || 'Chưa có.'}<br><br><strong>Kiến nghị cho Tư vấn giám sát:</strong><br>${(stakeholders.supervisionConsultant || []).map(item => `- ${item}`).join('<br>') || 'Chưa có.'}<br><br><strong>Kiến nghị cho Chủ đầu tư / Ban QLDA:</strong><br>${(stakeholders.investorPMU || []).map(item => `- ${item}`).join('<br>') || 'Chưa có.'}`; renderPredictionBarChart(payload.inputs); renderPredictionRadarChart(payload.inputs); renderPredictionRuleDetails(result.ruleDetails || []); setWorkflowBtnState('runPredictionBtn', 'done'); setWorkflowBtnState('refreshHistoryBtn', 'active'); await loadHistories(); }
async function loadHistories() { const response = await fetch(`${API_BASE}/reports/history`); state.histories = await response.json(); document.getElementById('historyStatus').textContent = state.histories.length ? `Đã tải ${state.histories.length} hồ sơ lịch sử dự báo.` : 'Chưa có lịch sử dự báo nào.'; renderHistories(); }
function renderHistories() { const body = document.getElementById('historyBody'); const cardList = document.getElementById('historyCardList'); body.innerHTML = ''; if (cardList) cardList.innerHTML = ''; if (!state.histories.length) { body.innerHTML = '<tr><td colspan="8" class="muted">Chưa có lịch sử dự báo nào.</td></tr>'; if (cardList) cardList.innerHTML = '<div class="muted">Chưa có lịch sử dự báo nào.</div>'; return; } state.histories.forEach(item => { const tr = document.createElement('tr'); tr.innerHTML = `<td><input type="checkbox" data-history-check value="${item.id}"></td><td>${item.id}</td><td>${item.projectName}</td><td>${item.projectStage || '--'}</td><td>${item.result?.score ?? '--'}</td><td>${item.result?.level ?? '--'}</td><td>${item.createdAt}</td><td><button class="ghost-btn" data-view-history="${item.id}">Xem</button> <button class="ghost-btn" data-delete-history="${item.id}">Xóa</button></td>`; body.appendChild(tr); if (cardList) { const card = document.createElement('div'); card.className = 'history-mobile-card'; card.innerHTML = `<label class="history-mobile-check"><input type="checkbox" data-history-check value="${item.id}"> <strong>#${item.id}</strong> - ${item.projectName}</label><div class="history-mobile-meta"><strong>Giai đoạn:</strong> ${item.projectStage || '--'}</div><div class="history-mobile-meta"><strong>Điểm / Mức:</strong> ${item.result?.score ?? '--'} / ${item.result?.level ?? '--'}</div><div class="history-mobile-meta"><strong>Thời gian:</strong> ${item.createdAt}</div><div class="toolbar" style="margin-top:10px;"><button class="ghost-btn" data-view-history="${item.id}">Xem</button><button class="ghost-btn" data-delete-history="${item.id}">Xóa</button></div>`; cardList.appendChild(card); } }); document.querySelectorAll('[data-view-history]').forEach(btn => btn.addEventListener('click', () => viewHistory(Number(btn.dataset.viewHistory)))); document.querySelectorAll('[data-delete-history]').forEach(btn => btn.addEventListener('click', () => deleteHistory(Number(btn.dataset.deleteHistory)))); }

function renderHistoryCompareCharts(selectedItems) {
  const xChart = document.getElementById('historyCompareChart');
  const scoreChart = document.getElementById('historyScoreCompareChart');
  if (!selectedItems.length) {
    xChart.textContent = 'Chưa có dữ liệu so sánh.';
    scoreChart.textContent = 'Chưa có dữ liệu so sánh.';
    return;
  }
  const labels = [
    { key: 'X1', name: 'Nhóm 1 - Điều kiện tự nhiên' },
    { key: 'X2', name: 'Nhóm 2 - Địa chất - nền móng' },
    { key: 'X3', name: 'Nhóm 3 - Kỹ thuật - công nghệ' },
    { key: 'X4', name: 'Nhóm 4 - Vật liệu - logistics' },
    { key: 'X5', name: 'Nhóm 5 - Tổ chức - quản lý' },
    { key: 'X6', name: 'Nhóm 6 - An toàn - môi trường' },
  ];
  const displayName = item => `${item.projectName} (#${item.id})`;
  xChart.innerHTML = labels.map(label => {
    const lines = selectedItems.map(item => `${displayName(item)}: ${Number(item.inputs?.[label.key] || 0).toFixed(2)}`).join('<br>');
    return `<div class="chart-bar-col"><div class="chart-label">${label.key}</div><div class="chart-label">${label.name}</div><div class="status-box" style="min-width:160px;">${lines}</div></div>`;
  }).join('');
  scoreChart.innerHTML = selectedItems.map(item => {
    const score = Number(item.result?.score || 0);
    const height = Math.max(12, (score / 5) * 180);
    return `<div class="chart-bar-col"><div class="chart-value">${score.toFixed(2)}</div><div class="chart-bar" style="height:${height}px"></div><div class="chart-label">${displayName(item)}</div></div>`;
  }).join('');
}
async function viewHistory(historyId) { const response = await fetch(`${API_BASE}/reports/history/${historyId}/report-payload`); const result = await response.json(); if (!response.ok) return document.getElementById('historyStatus').textContent = result.detail || 'Không xem được payload báo cáo.'; state.activeHistoryId = historyId; document.getElementById('historyStatus').innerHTML = `Báo cáo: <strong>${result.summary}</strong><br>Model: ${result.modelName || '--'} | Region: ${result.region || '--'}`; document.getElementById('historyPayloadBox').innerHTML = `Ngày báo cáo: <strong>${result.reportDate}</strong><br>Giai đoạn thi công: <strong>${result.projectStage || 'Chưa xác định'}</strong><br>Đầu vào: <strong>${Object.entries(result.inputs || {}).map(([k,v]) => `${k}=${v}`).join(', ')}</strong><br>Metrics: <strong>MAE ${result.metrics?.mae ?? '--'} | RMSE ${result.metrics?.rmse ?? '--'} | R² ${result.metrics?.r2 ?? '--'}</strong><br><br><strong>Khuyến nghị ưu tiên:</strong><br>${(result.recommendations?.priorityActions || []).map(item => `- ${item}`).join('<br>') || 'Chưa có.'}`; setWorkflowBtnState('downloadReportBtn', 'active'); }
async function deleteHistory(historyId) { const response = await fetch(`${API_BASE}/reports/history/${historyId}`, { method: 'DELETE' }); const result = await response.json(); if (!response.ok) return document.getElementById('historyStatus').textContent = result.detail || 'Không xóa được lịch sử.'; document.getElementById('historyStatus').textContent = `Đã xóa lịch sử ${historyId}.`; if (state.activeHistoryId === historyId) { state.activeHistoryId = null; document.getElementById('historyPayloadBox').textContent = 'Chưa xem payload báo cáo nào.'; } await loadHistories(); }
function downloadActiveReport() { if (!state.activeHistoryId) return document.getElementById('historyStatus').textContent = 'Anh cần bấm Xem một hồ sơ trước khi tải báo cáo Word.'; window.open(`${API_BASE}/reports/history/${state.activeHistoryId}/export-docx`, '_blank'); }
function exportTemplate(kind) { if (kind === 'dataset') { const datasetName = document.getElementById('datasetNameInput')?.value.trim() || 'du_lieu_mau'; window.open(`${API_BASE}/datasets/template/export?dataset_name=${encodeURIComponent(datasetName)}`, '_blank'); return; } window.open(`${API_BASE}/expert-surveys/template/export`, '_blank'); }

document.getElementById('uploadExpertBtn').addEventListener('click', uploadExpertSurvey);
document.getElementById('uploadDatasetBtn').addEventListener('click', uploadDataset);
document.getElementById('trainingDatasetSelect').addEventListener('change', event => { state.activeDatasetId = Number(event.target.value || 0) || state.activeDatasetId; updateTrainingDatasetSummary(); });
document.getElementById('checkDatasetBtn').addEventListener('click', checkDatasetStructure);
document.getElementById('createDatasetRowBtn').addEventListener('click', saveDatasetRow);
document.getElementById('normalizeXBtn').addEventListener('click', () => { updateB1Summary(); fillPredictionInputsFromB1(); setWorkflowBtnState('normalizeXBtn', 'done'); setWorkflowBtnState('runPredictionBtn', 'active'); });
document.getElementById('clearDatasetRowBtn').addEventListener('click', clearB1Form);
document.getElementById('importB1ExcelBtn').addEventListener('click', importB1FromExcel);
document.getElementById('splitDatasetBtn').addEventListener('click', initializeSplitStep);
document.getElementById('initSugenoBtn').addEventListener('click', initializeSugenoRules);
document.getElementById('runTrainingBtn').addEventListener('click', runTraining);
document.getElementById('evaluateTrainingBtn').addEventListener('click', evaluateTraining);
document.getElementById('loadModelsBtn').addEventListener('click', () => loadModels(document.getElementById('modelRegionFilter')?.value.trim() || document.getElementById('trainingRegion').value.trim()));
document.getElementById('downloadTrainingReportBtn').addEventListener('click', () => {
  if (!state.activeModelId) {
    document.getElementById('modelStatus').textContent = 'Anh cần huấn luyện hoặc chọn một model trước khi tải báo cáo A3.';
    return;
  }
  window.open(`${API_BASE}/reports/models/${state.activeModelId}/export-training-docx`, '_blank');
});
document.getElementById('downloadMembershipReportBtn').addEventListener('click', () => {
  window.open(`${API_BASE}/reports/memberships/export-compare-docx`, '_blank');
});
document.getElementById('runPredictionBtn').addEventListener('click', runPrediction);
document.getElementById('refreshHistoryBtn').addEventListener('click', loadHistories);
document.getElementById('downloadReportBtn').addEventListener('click', downloadActiveReport);
document.getElementById('compareSelectedBtn').addEventListener('click', () => {
  const ids = Array.from(document.querySelectorAll('[data-history-check]:checked')).map(el => Number(el.value));
  const selectedItems = state.histories.filter(item => ids.includes(item.id)).slice(0, 5);
  renderHistoryCompareCharts(selectedItems);
  document.getElementById('historyStatus').textContent = selectedItems.length ? `Đang so sánh ${selectedItems.length} công trình.` : 'Anh hãy chọn ít nhất một hồ sơ để so sánh.';
  if (selectedItems.length) setWorkflowBtnState('compareSelectedBtn', 'done');
});
document.getElementById('exportExpertTemplateBtn').addEventListener('click', () => exportTemplate('expert'));
document.getElementById('exportDatasetTemplateBtn').addEventListener('click', () => exportTemplate('dataset'));
document.getElementById('deleteSelectedDatasetsBtn').addEventListener('click', async () => {
  const ids = getSelectedDatasetIds();
  if (!ids.length) return document.getElementById('datasetStatus').textContent = 'Anh hãy tick ít nhất một bảng dữ liệu để xóa.';
  const response = await fetch(`${API_BASE}/datasets/delete-bulk`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ datasetIds: ids }) });
  const result = await response.json();
  if (!response.ok) return document.getElementById('datasetStatus').textContent = result.detail || 'Không xóa được các dataset đã chọn.';
  if (ids.includes(state.activeDatasetId)) { state.activeDatasetId = null; state.datasetRows = []; renderDatasetRows(); }
  await loadDatasets();
  document.getElementById('datasetStatus').textContent = `Đã xóa ${result.deletedDatasetIds.length} bảng dữ liệu.`;
});
document.getElementById('deleteAllDatasetsBtn').addEventListener('click', async () => {
  const ids = state.datasets.map(item => item.id);
  if (!ids.length) return document.getElementById('datasetStatus').textContent = 'Không có dataset nào để xóa.';
  const response = await fetch(`${API_BASE}/datasets/delete-bulk`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ datasetIds: ids }) });
  const result = await response.json();
  if (!response.ok) return document.getElementById('datasetStatus').textContent = result.detail || 'Không xóa được toàn bộ dataset.';
  state.activeDatasetId = null; state.datasetRows = []; renderDatasetRows();
  await loadDatasets();
  document.getElementById('datasetStatus').textContent = `Đã xóa toàn bộ ${result.deletedDatasetIds.length} bảng dữ liệu.`;
});
document.getElementById('closeDatasetModalBtn').addEventListener('click', closeDatasetModal);
document.getElementById('saveDatasetModalBtn').addEventListener('click', saveDatasetModal);
document.getElementById('deleteDatasetModalBtn').addEventListener('click', () => { if (state.editingRowId != null) deleteDatasetRow(state.editingRowId); });
document.querySelectorAll('[data-close-dataset-modal="true"]').forEach(el => el.addEventListener('click', closeDatasetModal));

refreshWorkflowChips();
loadDatasets();
loadModels();
loadHistories();
fillRowForm({});
bindB1FieldListeners();
updateB1Summary();
switchSection('section-overview');