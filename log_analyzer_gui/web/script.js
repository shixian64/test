// Store the full list of detailed issues globally for access by showIssueDetails
let currentDetailedIssues = [];

window.onload = () => {
    document.getElementById('selectFileBtn').addEventListener('click', () => {
        document.getElementById('actualFileInput').click();
    });

    document.getElementById('actualFileInput').addEventListener('change', handleFileSelect);
    
    // Close modal if user clicks outside of the modal content or presses Escape
    window.onclick = function(event) {
        const modal = document.getElementById('issueDetailModal');
        if (event.target == modal) {
            closeModal();
        }
    }
    window.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && document.getElementById('issueDetailModal').style.display !== 'none') {
            closeModal();
        }
    });
};

async function handleFileSelect(event) {
    const file = event.target.files[0];
    const statusElement = document.getElementById('analysisStatus');
    const selectedFileInfoElement = document.getElementById('selectedFileInfo');
    const resultsSection = document.getElementById('resultsSection');
    const summaryStatsElement = document.getElementById('summaryStats');
    const detailedIssuesTableContainerElement = document.getElementById('detailedIssuesTableContainer');
    const selectFileBtn = document.getElementById('selectFileBtn');

    if (!file) {
        selectedFileInfoElement.textContent = 'No file selected.';
        statusElement.textContent = '';
        statusElement.className = ''; // Reset class
        resultsSection.style.display = 'none';
        return;
    }

    selectedFileInfoElement.textContent = `Selected file: ${file.name}`;
    statusElement.textContent = 'Reading file...';
    statusElement.className = 'status-info';
    resultsSection.style.display = 'none';
    summaryStatsElement.innerHTML = ''; 
    detailedIssuesTableContainerElement.innerHTML = ''; 
    currentDetailedIssues = []; 

    selectFileBtn.disabled = true;
    // Assuming a CSS class 'button-disabled' will be added for styling
    selectFileBtn.classList.add('button-disabled');


    const reader = new FileReader();
    reader.onload = async (e) => {
        const fileContent = e.target.result;
        statusElement.textContent = `Analyzing ${file.name}... Please wait.`;
        statusElement.className = 'status-info';
        try {
            console.log(`Sending content of ${file.name} to Python...`);
            let result = await eel.start_analysis_py(file.name, fileContent)();
            console.log("Result from Python:", result);
            
            statusElement.className = ''; // Reset class by default

            if (result.status === "error") {
                statusElement.textContent = `Analysis Failed: ${result.message}`;
                statusElement.className = 'status-error';
                resultsSection.style.display = 'none';
            } else if (result.status === "success" && result.analysis_data) {
                statusElement.textContent = result.message; // e.g., "Analysis complete. X issues found."
                statusElement.className = 'status-success';
                resultsSection.style.display = 'block';
                currentDetailedIssues = result.analysis_data.detailed_issues || [];
                
                const summary = result.analysis_data.summary_counts || {};
                let summaryHtml = '<ul>';
                let totalIssues = 0;
                for (const type in summary) {
                    summaryHtml += `<li>${type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: ${summary[type]}</li>`;
                    totalIssues += summary[type];
                }
                summaryHtml += '</ul>';
                
                if (totalIssues === 0) {
                    summaryStatsElement.innerHTML = '<p class="empty-state-message">No issues found in the log file.</p>';
                } else {
                    summaryStatsElement.innerHTML = summaryHtml;
                }


                if (currentDetailedIssues.length > 0) {
                    let tableHtml = '<table><thead><tr><th>#</th><th>Type</th><th>Timestamp</th><th>Details</th></tr></thead><tbody>';
                    currentDetailedIssues.forEach((issue, index) => {
                        const triggerLine = issue.trigger_line_str || "";
                        const timestampMatch = triggerLine.match(/^\s*Timestamp:\s*(\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3})/);
                        const timestamp = timestampMatch ? timestampMatch[1] : 'N/A';
                        
                        let briefDetails = issue.trigger_line_str ? issue.trigger_line_str.substring(0, 100) + '...' : 'N/A';
                        if (issue.type === "ANR" && issue.process_name) {
                            briefDetails = `Process: ${issue.process_name}`;
                        } else if (issue.type === "NativeCrashHint" && issue.signal_info) {
                            briefDetails = `Signal: ${issue.signal_info}`;
                        } else if (issue.type === "SystemError" && issue.error_subtype) {
                             briefDetails = `Subtype: ${issue.error_subtype}`;
                        }

                        tableHtml += `<tr onclick="showIssueDetails(${index})">`;
                        tableHtml += `<td>${index + 1}</td>`;
                        tableHtml += `<td>${issue.type || 'N/A'}</td>`;
                        tableHtml += `<td>${timestamp}</td>`;
                        tableHtml += `<td>${briefDetails}</td>`;
                        tableHtml += '</tr>';
                    });
                    tableHtml += '</tbody></table>';
                    detailedIssuesTableContainerElement.innerHTML = tableHtml;
                } else {
                    detailedIssuesTableContainerElement.innerHTML = '<p class="empty-state-message">No specific issues detected in this log file.</p>';
                }

            } else { // Should not happen if Python returns consistent status
                 statusElement.textContent = 'Received an unexpected response from Python.';
                 statusElement.className = 'status-error';
                 resultsSection.style.display = 'none';
            }

        } catch (error) {
            console.error("Error calling Python function 'start_analysis_py':", error);
            statusElement.textContent = `Analysis Error: ${error.message || 'Unknown error from Python. Check console.'}`;
            statusElement.className = 'status-error';
            resultsSection.style.display = 'none';
        } finally {
            selectFileBtn.disabled = false;
            selectFileBtn.classList.remove('button-disabled');
        }
    };
    reader.onerror = (e) => {
        console.error("FileReader error:", e);
        selectedFileInfoElement.textContent = 'Error reading file.';
        statusElement.textContent = 'Failed to read file.';
        statusElement.className = 'status-error';
        selectFileBtn.disabled = false;
        selectFileBtn.classList.remove('button-disabled');
    };
    reader.readAsText(file);
}

function showIssueDetails(index) {
    if (index < 0 || index >= currentDetailedIssues.length) {
        console.error("Invalid index for showIssueDetails:", index);
        return;
    }
    const issue = currentDetailedIssues[index];
    const modal = document.getElementById('issueDetailModal');
    const detailContentElement = document.getElementById('issueDetailContent');
    
    let formattedDetails = '';
    for (const key in issue) {
        const readableKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        formattedDetails += `${readableKey}: ${issue[key]}\n\n`;
    }
    
    detailContentElement.textContent = formattedDetails.trim();
    modal.style.display = 'block';
}

function closeModal() {
    const modal = document.getElementById('issueDetailModal');
    modal.style.display = 'none';
}
