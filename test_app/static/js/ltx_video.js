/**
 * LTX-Video integration for OpenShot Web Editor
 * 
 * This module handles the client-side interactions with the LTX-Video API,
 * allowing users to generate videos from text prompts and import them into
 * their projects.
 */

class LTXVideoManager {
    constructor(projectId) {
        this.projectId = projectId;
        this.activeJobs = {};
        this.statusPollingInterval = null;
        this.uiElements = {
            generateButton: document.querySelector('.ai-prompt button'),
            promptInput: document.querySelector('.ai-prompt input'),
            aiToolsSection: document.querySelector('.ai-tools'),
            mediaList: document.querySelector('.media-list')
        };
        
        this.initialize();
    }
    
    initialize() {
        if (!this.uiElements.generateButton || !this.uiElements.promptInput) {
            console.error('Required UI elements not found. LTX Video integration not initialized.');
            return;
        }
        
        // Check LTX service status
        this.checkServiceStatus();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Start polling for active jobs
        this.startStatusPolling();
    }
    
    setupEventListeners() {
        // Add click event to the generate button
        this.uiElements.generateButton.addEventListener('click', () => {
            this.generateVideoFromPrompt();
        });
        
        // Add enter key press event to the prompt input
        this.uiElements.promptInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                this.generateVideoFromPrompt();
            }
        });
        
        // Add click event to the AI Assist button
        const aiAssistBtn = document.getElementById('ai-assist-btn');
        if (aiAssistBtn) {
            aiAssistBtn.addEventListener('click', () => {
                this.showAIAssistModal();
            });
        }
    }
    
    checkServiceStatus() {
        fetch('/api/ltx/status')
            .then(response => response.json())
            .then(status => {
                console.log('LTX service status:', status);
                
                // If service is not initialized, show status message
                if (!status.initialized) {
                    this.showInitializationStatus(status);
                }
            })
            .catch(error => {
                console.error('Error checking LTX service status:', error);
            });
    }
    
    showInitializationStatus(status) {
        const statusDiv = document.createElement('div');
        statusDiv.classList.add('ai-status');
        statusDiv.style.fontSize = '12px';
        statusDiv.style.color = '#a0a0c2';
        statusDiv.style.marginTop = '5px';
        
        if (status.gpu_available) {
            statusDiv.innerHTML = '<i class="bi bi-hourglass-split"></i> AI models loading... (this may take a minute)';
        } else {
            statusDiv.innerHTML = '<i class="bi bi-cpu"></i> AI running in CPU mode (slower performance)';
        }
        
        // Add to the AI tools section
        if (this.uiElements.aiToolsSection) {
            this.uiElements.aiToolsSection.appendChild(statusDiv);
        }
    }
    
    generateVideoFromPrompt() {
        const prompt = this.uiElements.promptInput.value.trim();
        
        if (!prompt) {
            this.showNotification('Please enter a text prompt', 'warning');
            return;
        }
        
        // Show loading state
        this.uiElements.generateButton.disabled = true;
        this.uiElements.generateButton.innerHTML = '<i class="bi bi-hourglass-split"></i>';
        
        // API request parameters
        const params = {
            prompt: prompt,
            height: 480,
            width: 704,
            num_frames: 121,
            guidance_scale: 3.0
        };
        
        // Call the API to generate the video
        fetch('/api/ltx/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 402) {
                    // Not enough credits
                    return response.json().then(data => {
                        throw new Error(`Not enough credits. Available: ${data.available}, Required: ${data.required}`);
                    });
                }
                throw new Error('Error starting generation job');
            }
            return response.json();
        })
        .then(data => {
            // Reset button state
            this.uiElements.generateButton.disabled = false;
            this.uiElements.generateButton.innerHTML = '<i class="bi bi-lightning"></i>';
            
            // Save job to active jobs
            this.activeJobs[data.job_id] = {
                prompt: prompt,
                startTime: new Date(),
                status: data.status
            };
            
            // Show notification
            this.showNotification('Video generation started. This may take a few minutes.', 'info');
            
            // Create job indicator in the UI
            this.createJobIndicator(data.job_id, prompt);
            
            // Clear the prompt input
            this.uiElements.promptInput.value = '';
        })
        .catch(error => {
            console.error('Error generating video:', error);
            
            // Reset button state
            this.uiElements.generateButton.disabled = false;
            this.uiElements.generateButton.innerHTML = '<i class="bi bi-lightning"></i>';
            
            // Show error notification
            this.showNotification(error.message || 'Error starting generation job', 'danger');
        });
    }
    
    createJobIndicator(jobId, prompt) {
        // Create a job indicator in the media library
        const jobDiv = document.createElement('div');
        jobDiv.classList.add('media-item', 'ai-job');
        jobDiv.dataset.jobId = jobId;
        jobDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-hourglass-split me-2" style="color: #9400D3;"></i>
                <div>
                    <div class="fw-bold">Generating: ${prompt.substring(0, 25)}${prompt.length > 25 ? '...' : ''} 
                        <span class="ai-badge"><i class="bi bi-stars"></i>AI</span>
                    </div>
                    <div class="progress mt-1" style="height: 5px;">
                        <div class="progress-bar progress-bar-animated progress-bar-striped" 
                             role="progressbar" style="width: 0%; background: linear-gradient(90deg, #9400D3, #4B0082);" 
                             aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                    <small style="color: #a0a0c2;">Starting generation...</small>
                </div>
            </div>
        `;
        
        // Add to the media list
        if (this.uiElements.mediaList) {
            this.uiElements.mediaList.prepend(jobDiv);
        }
    }
    
    updateJobIndicator(jobId, status) {
        const jobDiv = document.querySelector(`.ai-job[data-job-id="${jobId}"]`);
        if (!jobDiv) return;
        
        const progressBar = jobDiv.querySelector('.progress-bar');
        const statusText = jobDiv.querySelector('small');
        const icon = jobDiv.querySelector('.bi');
        
        if (!progressBar || !statusText || !icon) return;
        
        // Update progress bar
        if (status.progress) {
            progressBar.style.width = `${status.progress}%`;
            progressBar.setAttribute('aria-valuenow', status.progress);
        }
        
        // Update status text and icon
        if (status.status === 'completed') {
            statusText.textContent = 'Generation complete! Click to import.';
            icon.className = 'bi bi-check-circle-fill me-2';
            icon.style.color = '#00c853';
            
            // Remove progress animation
            progressBar.classList.remove('progress-bar-animated', 'progress-bar-striped');
            progressBar.style.width = '100%';
            
            // Add click handler to import
            jobDiv.style.cursor = 'pointer';
            jobDiv.addEventListener('click', () => {
                this.importGeneratedVideo(jobId);
            });
            
            // Remove from active jobs
            delete this.activeJobs[jobId];
            
        } else if (status.status === 'failed') {
            statusText.textContent = `Error: ${status.error || 'Generation failed'}`;
            icon.className = 'bi bi-x-circle-fill me-2';
            icon.style.color = '#f44336';
            
            // Remove progress animation
            progressBar.classList.remove('progress-bar-animated', 'progress-bar-striped');
            progressBar.style.width = '100%';
            progressBar.style.background = '#f44336';
            
            // Remove from active jobs
            delete this.activeJobs[jobId];
            
        } else if (status.status === 'processing') {
            statusText.textContent = `Generating video (${status.progress || 0}%)`;
        }
    }
    
    importGeneratedVideo(jobId) {
        // Show loading state
        const jobDiv = document.querySelector(`.ai-job[data-job-id="${jobId}"]`);
        if (jobDiv) {
            jobDiv.style.opacity = '0.7';
            const icon = jobDiv.querySelector('.bi');
            if (icon) {
                icon.className = 'bi bi-arrow-repeat me-2 spin';
            }
        }
        
        // Call the API to import the video
        fetch(`/api/ltx/import/${jobId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                project_id: this.projectId
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error importing video');
            }
            return response.json();
        })
        .then(data => {
            // Remove the job indicator
            if (jobDiv) {
                jobDiv.remove();
            }
            
            // Show success notification
            this.showNotification('Video imported successfully', 'success');
            
            // Reload assets
            this.reloadAssets();
        })
        .catch(error => {
            console.error('Error importing video:', error);
            
            // Reset job div state
            if (jobDiv) {
                jobDiv.style.opacity = '1';
                const icon = jobDiv.querySelector('.bi');
                if (icon) {
                    icon.className = 'bi bi-check-circle-fill me-2';
                }
            }
            
            // Show error notification
            this.showNotification(error.message || 'Error importing video', 'danger');
        });
    }
    
    startStatusPolling() {
        // Check status of active jobs every 5 seconds
        this.statusPollingInterval = setInterval(() => {
            this.pollActiveJobs();
        }, 5000);
    }
    
    pollActiveJobs() {
        // Get all job IDs from the active jobs object
        const jobIds = Object.keys(this.activeJobs);
        
        // Also check for any job indicators in the UI that might not be in our job object
        // (e.g., after page reload)
        const jobDivs = document.querySelectorAll('.ai-job[data-job-id]');
        jobDivs.forEach(div => {
            const jobId = div.dataset.jobId;
            if (jobId && !jobIds.includes(jobId)) {
                jobIds.push(jobId);
                // Add to active jobs if not already there
                if (!this.activeJobs[jobId]) {
                    this.activeJobs[jobId] = {
                        prompt: 'Unknown',
                        startTime: new Date(),
                        status: 'unknown'
                    };
                }
            }
        });
        
        // If no active jobs, stop polling
        if (jobIds.length === 0) {
            return;
        }
        
        // Check status of each job
        jobIds.forEach(jobId => {
            fetch(`/api/ltx/status/${jobId}`)
                .then(response => response.json())
                .then(status => {
                    // Update job status
                    if (this.activeJobs[jobId]) {
                        this.activeJobs[jobId].status = status.status;
                    }
                    
                    // Update job indicator
                    this.updateJobIndicator(jobId, status);
                })
                .catch(error => {
                    console.error(`Error checking status for job ${jobId}:`, error);
                });
        });
    }
    
    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.classList.add('alert', `alert-${type}`, 'notification');
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.maxWidth = '300px';
        notification.style.padding = '10px 15px';
        notification.style.borderRadius = '8px';
        notification.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s ease-in-out';
        
        notification.innerHTML = message;
        
        // Add to document
        document.body.appendChild(notification);
        
        // Fade in
        setTimeout(() => {
            notification.style.opacity = '1';
        }, 10);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }
    
    reloadAssets() {
        // Reload assets from the server
        fetch(`/api/project/${this.projectId}/assets`)
            .then(response => response.json())
            .then(data => {
                // Reload the page to show the new asset
                // A better approach would be to just add the new asset to the UI
                // but for simplicity, we'll reload the page
                window.location.reload();
            })
            .catch(error => {
                console.error('Error reloading assets:', error);
            });
    }
    
    showAIAssistModal() {
        // Create the modal
        const modalDiv = document.createElement('div');
        modalDiv.classList.add('modal', 'fade');
        modalDiv.id = 'aiAssistModal';
        modalDiv.tabIndex = '-1';
        modalDiv.setAttribute('aria-labelledby', 'aiAssistModalLabel');
        modalDiv.setAttribute('aria-hidden', 'true');
        
        modalDiv.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content" style="background-color: #252536; color: #e0e0e0; border: 1px solid #353545;">
                    <div class="modal-header" style="border-bottom: 1px solid #353545;">
                        <h5 class="modal-title" id="aiAssistModalLabel">
                            <i class="bi bi-robot" style="color: #9400D3;"></i> AI Assist
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="aiPromptTextarea" class="form-label">Tell me what you want to create:</label>
                            <textarea class="form-control" id="aiPromptTextarea" rows="3" 
                                      style="background-color: #2e2e40; color: #e0e0e0; border: 1px solid #353545;"
                                      placeholder="Describe the video you want to generate..."></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Video Settings:</label>
                            <div class="row g-2">
                                <div class="col-6">
                                    <div class="input-group input-group-sm">
                                        <span class="input-group-text" style="background-color: #2e2e40; color: #e0e0e0; border: 1px solid #353545;">Width</span>
                                        <input type="number" class="form-control" id="aiVideoWidth" value="704"
                                               style="background-color: #2e2e40; color: #e0e0e0; border: 1px solid #353545;">
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="input-group input-group-sm">
                                        <span class="input-group-text" style="background-color: #2e2e40; color: #e0e0e0; border: 1px solid #353545;">Height</span>
                                        <input type="number" class="form-control" id="aiVideoHeight" value="480"
                                               style="background-color: #2e2e40; color: #e0e0e0; border: 1px solid #353545;">
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Duration: <span id="durationValue">5</span> seconds</label>
                            <input type="range" class="form-range" min="3" max="10" value="5" id="durationRange"
                                   style="accent-color: #9400D3;">
                        </div>
                        <div class="small text-muted mb-3">
                            <i class="bi bi-info-circle"></i> This will use 15 credits from your account.
                        </div>
                    </div>
                    <div class="modal-footer" style="border-top: 1px solid #353545;">
                        <button type="button" class="btn btn-outline-light" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn" style="background: linear-gradient(90deg, #9400D3, #4B0082); color: white;" id="generateAiVideoBtn">
                            Generate Video
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add to document
        document.body.appendChild(modalDiv);
        
        // Initialize the modal
        const modal = new bootstrap.Modal(document.getElementById('aiAssistModal'));
        modal.show();
        
        // Set up event listeners
        const durationRange = document.getElementById('durationRange');
        const durationValue = document.getElementById('durationValue');
        
        if (durationRange && durationValue) {
            durationRange.addEventListener('input', () => {
                durationValue.textContent = durationRange.value;
            });
        }
        
        // Set up generate button
        const generateBtn = document.getElementById('generateAiVideoBtn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => {
                const prompt = document.getElementById('aiPromptTextarea').value.trim();
                const width = parseInt(document.getElementById('aiVideoWidth').value);
                const height = parseInt(document.getElementById('aiVideoHeight').value);
                const duration = parseInt(document.getElementById('durationRange').value);
                
                if (!prompt) {
                    this.showNotification('Please enter a text prompt', 'warning');
                    return;
                }
                
                // Hide modal
                modal.hide();
                
                // Generate video
                this.generateVideoWithOptions(prompt, width, height, duration);
            });
        }
        
        // Clean up when modal is hidden
        modalDiv.addEventListener('hidden.bs.modal', () => {
            modalDiv.remove();
        });
    }
    
    generateVideoWithOptions(prompt, width, height, duration) {
        // Show notification
        this.showNotification('Starting video generation...', 'info');
        
        // Calculate number of frames (assuming 25 fps)
        const numFrames = duration * 25;
        
        // API request parameters
        const params = {
            prompt: prompt,
            height: height,
            width: width,
            num_frames: numFrames,
            guidance_scale: 3.0
        };
        
        // Call the API to generate the video
        fetch('/api/ltx/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 402) {
                    // Not enough credits
                    return response.json().then(data => {
                        throw new Error(`Not enough credits. Available: ${data.available}, Required: ${data.required}`);
                    });
                }
                throw new Error('Error starting generation job');
            }
            return response.json();
        })
        .then(data => {
            // Save job to active jobs
            this.activeJobs[data.job_id] = {
                prompt: prompt,
                startTime: new Date(),
                status: data.status
            };
            
            // Show notification
            this.showNotification('Video generation started. This may take a few minutes.', 'info');
            
            // Create job indicator in the UI
            this.createJobIndicator(data.job_id, prompt);
        })
        .catch(error => {
            console.error('Error generating video:', error);
            
            // Show error notification
            this.showNotification(error.message || 'Error starting generation job', 'danger');
        });
    }
}

// Initialize when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Get project ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get('project_id');
    
    if (projectId) {
        // Initialize LTX Video Manager
        window.ltxManager = new LTXVideoManager(projectId);
    } else {
        console.error('Project ID not found in URL');
    }
});