// Global variables
let currentDetailedIssues = [];
let currentLanguage = 'en';
let filteredIssues = [];

// Language translations
const translations = {
    en: {
        noFileSelected: 'No file selected',
        filesSelected: 'files selected',
        fileSelected: 'file selected',
        processing: 'Processing...',
        analysisComplete: 'Analysis complete',
        analysisError: 'Analysis failed',
        noIssuesFound: 'No issues found in the log file',
        searchPlaceholder: 'Search issues...',
        allTypes: 'All Types'
    },
    zh: {
        noFileSelected: '未选择文件',
        filesSelected: '个文件已选择',
        fileSelected: '个文件已选择',
        processing: '处理中...',
        analysisComplete: '分析完成',
        analysisError: '分析失败',
        noIssuesFound: '日志文件中未发现问题',
        searchPlaceholder: '搜索问题...',
        allTypes: '所有类型'
    }
};

// Initialize application
window.onload = () => {
    initializeEventListeners();
    initializeLanguage();
    setupDragAndDrop();
};

function initializeEventListeners() {
    // File selection
    document.getElementById('selectFileBtn').addEventListener('click', () => {
        document.getElementById('actualFileInput').click();
    });

    document.getElementById('actualFileInput').addEventListener('change', handleFileSelect);

    // Modal controls
    window.onclick = function(event) {
        const modal = document.getElementById('issueDetailModal');
        if (event.target === modal) {
            closeModal();
        }
    };

    window.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeModal();
        }
    });

    // Search and filter
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', filterIssues);
    }

    const typeFilter = document.getElementById('typeFilter');
    if (typeFilter) {
        typeFilter.addEventListener('change', filterIssues);
    }

    // Export functionality
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportResults);
    }
}

function initializeLanguage() {
    const savedLanguage = localStorage.getItem('gui-language') || 'en';
    toggleLanguage(savedLanguage);
}

// Language toggle function
function toggleLanguage(lang) {
    currentLanguage = lang;
    const enElements = document.querySelectorAll('[id*="-en"]');
    const zhElements = document.querySelectorAll('[id*="-zh"]');
    const enBtn = document.getElementById('btn-en');
    const zhBtn = document.getElementById('btn-zh');

    if (lang === 'en') {
        enElements.forEach(el => el.style.display = 'block');
        zhElements.forEach(el => el.style.display = 'none');
        enBtn?.classList.add('active');
        zhBtn?.classList.remove('active');
    } else {
        enElements.forEach(el => el.style.display = 'none');
        zhElements.forEach(el => el.style.display = 'block');
        enBtn?.classList.remove('active');
        zhBtn?.classList.add('active');
    }

    localStorage.setItem('gui-language', lang);
    updateDynamicText();
}

function updateDynamicText() {
    const t = translations[currentLanguage];

    // Update search placeholder
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.placeholder = t.searchPlaceholder;
    }

    // Update filter options
    const typeFilter = document.getElementById('typeFilter');
    if (typeFilter && typeFilter.options.length > 0) {
        typeFilter.options[0].text = t.allTypes;
    }
}

// Drag and drop functionality
function setupDragAndDrop() {
    const dropZone = document.getElementById('fileDropZone');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    dropZone.addEventListener('drop', handleDrop, false);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    document.getElementById('fileDropZone').classList.add('drag-over');
}

function unhighlight(e) {
    document.getElementById('fileDropZone').classList.remove('drag-over');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    document.getElementById('actualFileInput').files = files;
    handleFileSelect({ target: { files: files } });
}

async function handleFileSelect(event) {
    const files = event.target.files;
    const statusElement = document.getElementById('analysisStatus');
    const selectedFileInfoElement = document.getElementById('selectedFileInfo');
    const resultsSection = document.getElementById('resultsSection');
    const progressSection = document.getElementById('progressSection');
    const selectFileBtn = document.getElementById('selectFileBtn');

    if (!files || files.length === 0) {
        updateFileInfo(null);
        resetUI();
        return;
    }

    updateFileInfo(files);
    showProgress();
    resetResults();

    selectFileBtn.disabled = true;

    // Process files (for now, just handle the first file)
    const file = files[0];
    await processFile(file);
}

function updateFileInfo(files) {
    const selectedFileInfoElement = document.getElementById('selectedFileInfo');
    const t = translations[currentLanguage];

    if (!files || files.length === 0) {
        selectedFileInfoElement.innerHTML = `<span class="lang-content">${t.noFileSelected}</span>`;
    } else if (files.length === 1) {
        selectedFileInfoElement.innerHTML = `
            <i class="fas fa-file-alt"></i>
            <strong>${files[0].name}</strong>
            <span class="file-size">(${formatFileSize(files[0].size)})</span>
        `;
    } else {
        selectedFileInfoElement.innerHTML = `
            <i class="fas fa-files"></i>
            <strong>${files.length} ${t.filesSelected}</strong>
        `;
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showProgress() {
    const progressSection = document.getElementById('progressSection');
    const progressText = document.getElementById('progressText');
    const t = translations[currentLanguage];

    progressSection.style.display = 'block';
    progressText.textContent = t.processing;
    animateProgress();
}

function animateProgress() {
    const progressFill = document.getElementById('progressFill');
    let width = 0;
    const interval = setInterval(() => {
        width += Math.random() * 10;
        if (width >= 90) {
            clearInterval(interval);
            width = 90;
        }
        progressFill.style.width = width + '%';
    }, 200);
}

function hideProgress() {
    const progressSection = document.getElementById('progressSection');
    const progressFill = document.getElementById('progressFill');

    progressFill.style.width = '100%';
    setTimeout(() => {
        progressSection.style.display = 'none';
        progressFill.style.width = '0%';
    }, 500);
}

function resetUI() {
    const statusElement = document.getElementById('analysisStatus');
    const resultsSection = document.getElementById('resultsSection');
    const progressSection = document.getElementById('progressSection');

    statusElement.textContent = '';
    statusElement.className = '';
    resultsSection.style.display = 'none';
    progressSection.style.display = 'none';
}

function resetResults() {
    const summaryStatsElement = document.getElementById('summaryStats');
    const detailedIssuesTableContainerElement = document.getElementById('detailedIssuesTableContainer');
    const resultsSection = document.getElementById('resultsSection');

    summaryStatsElement.innerHTML = '';
    detailedIssuesTableContainerElement.innerHTML = '';
    resultsSection.style.display = 'none';
    currentDetailedIssues = [];
    filteredIssues = [];
}

async function processFile(file) {
    const statusElement = document.getElementById('analysisStatus');
    const selectFileBtn = document.getElementById('selectFileBtn');
    const t = translations[currentLanguage];


    const reader = new FileReader();
    reader.onload = async (e) => {
        const fileContent = e.target.result;

        try {
            console.log(`Analyzing ${file.name}...`);
            const result = await eel.start_analysis_py(file.name, fileContent)();
            console.log("Analysis result:", result);

            hideProgress();

            if (result.status === "error") {
                showStatus(`${t.analysisError}: ${result.message}`, 'error');
                resetResults();
            } else if (result.status === "success" && result.analysis_data) {
                const issueCount = result.analysis_data.detailed_issues?.length || 0;
                showStatus(`${t.analysisComplete}. ${issueCount} issues found.`, 'success');
                displayResults(result.analysis_data);
            } else {
                showStatus('Unexpected response from analyzer', 'error');
                resetResults();
            }
        } catch (error) {
            console.error("Analysis error:", error);
            hideProgress();
            showStatus(`${t.analysisError}: ${error.message}`, 'error');
            resetResults();
        } finally {
            selectFileBtn.disabled = false;
        }
    };

    reader.onerror = () => {
        hideProgress();
        showStatus('Failed to read file', 'error');
        selectFileBtn.disabled = false;
    };

    reader.readAsText(file);
}

function showStatus(message, type) {
    const statusElement = document.getElementById('analysisStatus');
    statusElement.textContent = message;
    statusElement.className = `status-${type}`;
}

function displayResults(analysisData) {
    const resultsSection = document.getElementById('resultsSection');

    currentDetailedIssues = analysisData.detailed_issues || [];
    filteredIssues = [...currentDetailedIssues];

    // Check if this is an advanced analysis (SPRD package)
    const isAdvancedAnalysis = analysisData.package_info || analysisData.sprd_analysis;

    if (isAdvancedAnalysis) {
        displayAdvancedResults(analysisData);
    } else {
        displayBasicResults(analysisData);
    }

    resultsSection.style.display = 'block';
}

function displayAdvancedResults(analysisData) {
    // Display package overview
    displayPackageOverview(analysisData.package_info || {});

    // Display platform information
    if (analysisData.sprd_analysis && analysisData.sprd_analysis.platform_info) {
        displayPlatformInfo(analysisData.sprd_analysis.platform_info);
    }

    // Display summary
    displaySummary(analysisData.summary_counts || analysisData.summary || {});

    // Display subsystem analysis
    if (analysisData.subsystem_analysis) {
        displaySubsystemAnalysis(analysisData.subsystem_analysis);
    }

    // Display timeline
    if (analysisData.timeline && analysisData.timeline.length > 0) {
        displayTimeline(analysisData.timeline);
    }

    // Display detailed issues
    displayIssuesTable();

    // Setup filters
    setupAdvancedFilters(analysisData);
}

function displayBasicResults(analysisData) {
    // Hide advanced sections
    hideAdvancedSections();

    // Display summary
    displaySummary(analysisData.summary_counts || {});

    // Display detailed issues
    displayIssuesTable();

    // Setup filters
    setupFilters();
}

function hideAdvancedSections() {
    const sections = ['packageOverview', 'platformInfo', 'subsystemAnalysis', 'timelineSection'];
    sections.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.style.display = 'none';
    });
}

function displayPackageOverview(packageInfo) {
    const packageOverview = document.getElementById('packageOverview');

    if (!packageInfo || Object.keys(packageInfo).length === 0) {
        packageOverview.style.display = 'none';
        return;
    }

    document.getElementById('packageName').textContent = packageInfo.name || 'Unknown';
    document.getElementById('packageSize').textContent = formatFileSize(packageInfo.size || 0);
    document.getElementById('totalFiles').textContent = packageInfo.total_files || 0;
    document.getElementById('subsystemCount').textContent = packageInfo.subsystems ? packageInfo.subsystems.length : 0;

    packageOverview.style.display = 'block';
}

function displayPlatformInfo(platformInfo) {
    const platformInfoSection = document.getElementById('platformInfo');

    if (!platformInfo || Object.keys(platformInfo).length === 0) {
        platformInfoSection.style.display = 'none';
        return;
    }

    document.getElementById('chipsetInfo').textContent = platformInfo.chipset || 'Unknown';
    document.getElementById('androidVersion').textContent = platformInfo.android_version || 'Unknown';
    document.getElementById('buildVersion').textContent = platformInfo.build_version || 'Unknown';

    platformInfoSection.style.display = 'block';
}

function displaySubsystemAnalysis(subsystemAnalysis) {
    const subsystemSection = document.getElementById('subsystemAnalysis');
    const tabsContainer = document.getElementById('subsystemTabs');
    const contentContainer = document.getElementById('subsystemContent');

    if (!subsystemAnalysis || Object.keys(subsystemAnalysis).length === 0) {
        subsystemSection.style.display = 'none';
        return;
    }

    // Clear existing content
    tabsContainer.innerHTML = '';
    contentContainer.innerHTML = '';

    // Create tabs and content for each subsystem
    const subsystems = Object.keys(subsystemAnalysis);
    subsystems.forEach((subsystemName, index) => {
        const subsystemData = subsystemAnalysis[subsystemName];

        // Create tab
        const tab = document.createElement('button');
        tab.className = `subsystem-tab ${index === 0 ? 'active' : ''}`;
        tab.textContent = subsystemName.charAt(0).toUpperCase() + subsystemName.slice(1);
        tab.onclick = () => switchSubsystemTab(subsystemName);
        tabsContainer.appendChild(tab);

        // Create content panel
        const panel = document.createElement('div');
        panel.className = `subsystem-panel ${index === 0 ? 'active' : ''}`;
        panel.id = `panel-${subsystemName}`;
        panel.innerHTML = createSubsystemPanelContent(subsystemData);
        contentContainer.appendChild(panel);
    });

    subsystemSection.style.display = 'block';
}

function createSubsystemPanelContent(subsystemData) {
    const stats = subsystemData.statistics || {};
    const issues = subsystemData.issues || [];

    return `
        <div class="subsystem-stats">
            <div class="subsystem-stat">
                <div class="stat-value">${subsystemData.file_count || 0}</div>
                <div class="stat-label">Files</div>
            </div>
            <div class="subsystem-stat">
                <div class="stat-value">${formatFileSize(subsystemData.total_size || 0)}</div>
                <div class="stat-label">Total Size</div>
            </div>
            <div class="subsystem-stat">
                <div class="stat-value">${issues.length}</div>
                <div class="stat-label">Issues Found</div>
            </div>
            <div class="subsystem-stat">
                <div class="stat-value">${Object.keys(stats.issue_types || {}).length}</div>
                <div class="stat-label">Issue Types</div>
            </div>
        </div>
        <div class="subsystem-issues">
            <h4>Recent Issues</h4>
            ${issues.slice(0, 5).map(issue => `
                <div class="issue-preview">
                    <span class="issue-type ${issue.type}">${issue.type}</span>
                    <span class="issue-description">${issue.message || issue.trigger_line_str || 'No description'}</span>
                </div>
            `).join('')}
        </div>
    `;
}

function switchSubsystemTab(subsystemName) {
    // Update tab states
    document.querySelectorAll('.subsystem-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');

    // Update panel states
    document.querySelectorAll('.subsystem-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    document.getElementById(`panel-${subsystemName}`).classList.add('active');
}

function displayTimeline(timeline) {
    const timelineSection = document.getElementById('timelineSection');
    const timelineContainer = document.getElementById('timelineContainer');

    if (!timeline || timeline.length === 0) {
        timelineSection.style.display = 'none';
        return;
    }

    // Sort timeline by timestamp
    const sortedTimeline = timeline.sort((a, b) => {
        return new Date(a.timestamp || 0) - new Date(b.timestamp || 0);
    });

    // Create timeline items
    const timelineHTML = sortedTimeline.slice(0, 50).map(event => `
        <div class="timeline-item">
            <div class="timeline-time">${event.timestamp || 'Unknown'}</div>
            <div class="timeline-subsystem">${event.subsystem || 'System'}</div>
            <div class="timeline-description">${event.description || event.type || 'Event'}</div>
            <div class="timeline-severity ${event.severity || 'medium'}">${event.severity || 'medium'}</div>
        </div>
    `).join('');

    timelineContainer.innerHTML = timelineHTML;
    timelineSection.style.display = 'block';
}

function setupAdvancedFilters(analysisData) {
    setupFilters();

    // Add subsystem filter options
    const subsystemFilter = document.getElementById('subsystemFilter');
    if (subsystemFilter && analysisData.subsystem_analysis) {
        const subsystems = Object.keys(analysisData.subsystem_analysis);
        subsystems.forEach(subsystem => {
            const option = document.createElement('option');
            option.value = subsystem;
            option.textContent = subsystem.charAt(0).toUpperCase() + subsystem.slice(1);
            subsystemFilter.appendChild(option);
        });
    }
}

function displaySummary(summary) {
    const summaryStatsElement = document.getElementById('summaryStats');
    const t = translations[currentLanguage];

    let totalIssues = 0;
    for (const count of Object.values(summary)) {
        totalIssues += count;
    }

    if (totalIssues === 0) {
        summaryStatsElement.innerHTML = `<div class="empty-state-message">${t.noIssuesFound}</div>`;
        return;
    }

    let summaryHtml = '';
    const issueTypes = {
        'JavaCrash': { icon: 'fas fa-bug', color: '#dc2626' },
        'ANR': { icon: 'fas fa-clock', color: '#d97706' },
        'NativeCrashHint': { icon: 'fas fa-exclamation-triangle', color: '#7c3aed' },
        'SystemError': { icon: 'fas fa-times-circle', color: '#dc2626' },
        'MemoryIssue': { icon: 'fas fa-memory', color: '#2563eb' }
    };

    for (const [type, count] of Object.entries(summary)) {
        if (count > 0) {
            const typeInfo = issueTypes[type] || { icon: 'fas fa-question', color: '#6b7280' };
            const displayName = type.replace(/([A-Z])/g, ' $1').trim();

            summaryHtml += `
                <div class="summary-card" style="background: linear-gradient(135deg, ${typeInfo.color}, ${typeInfo.color}dd)">
                    <div class="card-title">
                        <i class="${typeInfo.icon}"></i> ${displayName}
                    </div>
                    <div class="card-value">${count}</div>
                </div>
            `;
        }
    }

    summaryStatsElement.innerHTML = summaryHtml;
}


function displayIssuesTable() {
    const detailedIssuesTableContainerElement = document.getElementById('detailedIssuesTableContainer');
    const t = translations[currentLanguage];

    if (filteredIssues.length === 0) {
        detailedIssuesTableContainerElement.innerHTML = `<div class="empty-state-message">${t.noIssuesFound}</div>`;
        return;
    }

    let tableHtml = `
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Type</th>
                    <th>Timestamp</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
    `;

    filteredIssues.forEach((issue, index) => {
        const originalIndex = currentDetailedIssues.indexOf(issue);
        const triggerLine = issue.trigger_line_str || "";
        const timestampMatch = triggerLine.match(/Timestamp:\s*(\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3})/);
        const timestamp = timestampMatch ? timestampMatch[1] : 'N/A';

        let briefDetails = 'N/A';
        if (issue.type === "ANR" && issue.process_name) {
            briefDetails = `Process: ${issue.process_name}`;
        } else if (issue.type === "NativeCrashHint" && issue.signal_info) {
            briefDetails = `Signal: ${issue.signal_info}`;
        } else if (issue.type === "SystemError" && issue.error_subtype) {
            briefDetails = `Subtype: ${issue.error_subtype}`;
        } else if (issue.type === "MemoryIssue" && issue.killed_process) {
            briefDetails = `Killed: ${issue.killed_process}`;
        } else if (triggerLine) {
            briefDetails = triggerLine.substring(triggerLine.indexOf('Message:') + 8, triggerLine.indexOf('Message:') + 80) + '...';
        }

        const typeClass = issue.type.toLowerCase().replace(/([A-Z])/g, '-$1').substring(1);

        tableHtml += `
            <tr onclick="showIssueDetails(${originalIndex})" data-type="${issue.type}">
                <td>${index + 1}</td>
                <td><span class="issue-type ${typeClass}">${issue.type}</span></td>
                <td>${timestamp}</td>
                <td>${briefDetails}</td>
            </tr>
        `;
    });

    tableHtml += '</tbody></table>';
    detailedIssuesTableContainerElement.innerHTML = tableHtml;
}

function setupFilters() {
    const typeFilter = document.getElementById('typeFilter');
    const t = translations[currentLanguage];

    // Clear existing options
    typeFilter.innerHTML = `<option value="">${t.allTypes}</option>`;

    // Get unique issue types
    const types = [...new Set(currentDetailedIssues.map(issue => issue.type))];
    types.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        typeFilter.appendChild(option);
    });
}

function filterIssues() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const typeFilter = document.getElementById('typeFilter').value;

    filteredIssues = currentDetailedIssues.filter(issue => {
        const matchesSearch = !searchTerm ||
            issue.type.toLowerCase().includes(searchTerm) ||
            (issue.process_name && issue.process_name.toLowerCase().includes(searchTerm)) ||
            (issue.signal_info && issue.signal_info.toLowerCase().includes(searchTerm)) ||
            (issue.error_subtype && issue.error_subtype.toLowerCase().includes(searchTerm)) ||
            (issue.trigger_line_str && issue.trigger_line_str.toLowerCase().includes(searchTerm));

        const matchesType = !typeFilter || issue.type === typeFilter;

        return matchesSearch && matchesType;
    });

    displayIssuesTable();
}

function exportResults() {
    if (currentDetailedIssues.length === 0) {
        alert('No results to export');
        return;
    }

    const data = {
        summary_counts: {},
        detailed_issues: currentDetailedIssues
    };

    // Calculate summary
    currentDetailedIssues.forEach(issue => {
        data.summary_counts[issue.type] = (data.summary_counts[issue.type] || 0) + 1;
    });

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `log_analysis_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function showIssueDetails(index) {
    if (index < 0 || index >= currentDetailedIssues.length) {
        console.error("Invalid index for showIssueDetails:", index);
        return;
    }

    const issue = currentDetailedIssues[index];
    const modal = document.getElementById('issueDetailModal');
    const detailContentElement = document.getElementById('issueDetailContent');

    // Format issue details in a more readable way
    let formattedDetails = '';

    // Add issue type and basic info
    formattedDetails += `Issue Type: ${issue.type}\n`;
    formattedDetails += `═══════════════════════════════════════\n\n`;

    // Add specific details based on issue type
    if (issue.type === 'ANR') {
        if (issue.process_name) formattedDetails += `Process Name: ${issue.process_name}\n`;
        if (issue.reason) formattedDetails += `Reason: ${issue.reason}\n`;
    } else if (issue.type === 'NativeCrashHint') {
        if (issue.signal_info) formattedDetails += `Signal Info: ${issue.signal_info}\n`;
        if (issue.process_info) formattedDetails += `Process Info: ${issue.process_info}\n`;
    } else if (issue.type === 'SystemError') {
        if (issue.error_subtype) formattedDetails += `Error Subtype: ${issue.error_subtype}\n`;
    } else if (issue.type === 'MemoryIssue') {
        if (issue.killed_process) formattedDetails += `Killed Process: ${issue.killed_process}\n`;
        if (issue.oom_reason) formattedDetails += `OOM Reason: ${issue.oom_reason}\n`;
    }

    formattedDetails += '\n';

    // Add trigger line details
    if (issue.trigger_line_str) {
        formattedDetails += 'Trigger Line Details:\n';
        formattedDetails += '─────────────────────\n';
        formattedDetails += issue.trigger_line_str + '\n\n';
    }

    // Add any additional fields
    const excludeFields = ['type', 'trigger_line_str', 'process_name', 'reason', 'signal_info', 'process_info', 'error_subtype', 'killed_process', 'oom_reason'];
    const additionalFields = Object.keys(issue).filter(key => !excludeFields.includes(key));

    if (additionalFields.length > 0) {
        formattedDetails += 'Additional Information:\n';
        formattedDetails += '─────────────────────\n';
        additionalFields.forEach(key => {
            if (issue[key] !== null && issue[key] !== undefined) {
                const readableKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                formattedDetails += `${readableKey}: ${issue[key]}\n`;
            }
        });
    }

    detailContentElement.textContent = formattedDetails.trim();
    modal.style.display = 'block';

    // Add animation class
    setTimeout(() => {
        modal.querySelector('.modal-content').style.transform = 'scale(1)';
    }, 10);
}

function closeModal() {
    const modal = document.getElementById('issueDetailModal');
    const modalContent = modal.querySelector('.modal-content');

    // Add closing animation
    modalContent.style.transform = 'scale(0.95)';

    setTimeout(() => {
        modal.style.display = 'none';
        modalContent.style.transform = 'scale(1)';
    }, 200);
}

// Add keyboard navigation for accessibility
document.addEventListener('keydown', (event) => {
    const modal = document.getElementById('issueDetailModal');
    if (modal.style.display === 'block') {
        if (event.key === 'Escape') {
            closeModal();
        }
    }
});

// Initialize the application when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.onload);
} else {
    window.onload();
}
