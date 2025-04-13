// FLUX58 Video Editor - Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log("Editor script loaded");
    
    // Initialize editor
    initEditor();
    
    // Add event listeners
    addEventListeners();
    
    // Log project data
    console.log("Project data:", projectData);
});

// Main initialization function
function initEditor() {
    console.log("Initializing editor...");
    
    // Check if OpenShot is available via our API
    checkOpenShotStatus();
    
    // Initialize timeline
    initTimeline();
    
    // Initialize preview player
    initPreviewPlayer();
    
    // Initialize media library
    initMediaLibrary();
    
    // Initialize properties panel
    initPropertiesPanel();
    
    // Initialize theme switcher
    initThemeSwitcher();
}

// Check OpenShot library status
function checkOpenShotStatus() {
    console.log("Checking OpenShot status...");
    
    // Make an AJAX request to check OpenShot status
    fetch('/api/openshot/status')
        .then(response => response.json())
        .then(data => {
            console.log("OpenShot status:", data);
            
            // Update UI based on OpenShot availability
            if (data.available) {
                console.log("OpenShot is available:", data.version);
                document.querySelector('.editor-header').classList.add('openshot-available');
            } else {
                console.warn("OpenShot is not available. Some features will be limited.");
                showError("OpenShot library is not available. Some video editing features will be limited.");
            }
        })
        .catch(error => {
            console.error("Error checking OpenShot status:", error);
            showError("Error connecting to OpenShot. Some features may not work.");
        });
}

// Initialize timeline
function initTimeline() {
    console.log("Initializing timeline...");
    
    // Set initial timeline data
    updateTimelineDisplay();
    
    // Initialize timeline playhead dragging
    initPlayheadDragging();
    
    // Initialize clip dragging
    initClipDragging();
}

// Update timeline display based on project data
function updateTimelineDisplay() {
    // Update time markers
    const duration = projectData.timeline.duration || 60;
    const timeMarkers = document.querySelector('.timeline-time-markers');
    timeMarkers.innerHTML = '';
    
    const markerCount = Math.ceil(duration / 10);
    for (let i = 0; i <= markerCount; i++) {
        const minutes = Math.floor((i * 10) / 60);
        const seconds = (i * 10) % 60;
        const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        const marker = document.createElement('div');
        marker.className = 'time-marker';
        marker.textContent = timeString;
        marker.style.left = `${i * 100}px`;
        timeMarkers.appendChild(marker);
    }
    
    // Update total time display
    document.getElementById('total-time').textContent = formatTime(duration);
}

// Initialize preview player
function initPreviewPlayer() {
    console.log("Initializing preview player...");
    
    const playBtn = document.getElementById('play-btn');
    const prevFrameBtn = document.getElementById('prev-frame-btn');
    const nextFrameBtn = document.getElementById('next-frame-btn');
    const muteBtn = document.getElementById('mute-btn');
    const scrubber = document.querySelector('.timeline-scrubber');
    
    // Set up play button
    playBtn.addEventListener('click', function() {
        togglePlayback();
    });
    
    // Set up prev/next frame buttons
    prevFrameBtn.addEventListener('click', function() {
        seekFrame(-1);
    });
    
    nextFrameBtn.addEventListener('click', function() {
        seekFrame(1);
    });
    
    // Set up mute button
    muteBtn.addEventListener('click', function() {
        toggleMute();
    });
    
    // Set up scrubber
    scrubber.addEventListener('click', function(e) {
        seekToPosition(e);
    });
}

// Initialize media library
function initMediaLibrary() {
    console.log("Initializing media library...");
    
    const uploadBtn = document.getElementById('upload-media-btn');
    const uploadFirstBtn = document.getElementById('upload-first-media-btn');
    
    // Set up upload button
    if (uploadBtn) {
        uploadBtn.addEventListener('click', function() {
            showMediaUploadDialog();
        });
    }
    
    // Set up first upload button
    if (uploadFirstBtn) {
        uploadFirstBtn.addEventListener('click', function() {
            showMediaUploadDialog();
        });
    }
    
    // Initialize media items drag and drop
    initMediaDragAndDrop();
}

// Initialize properties panel
function initPropertiesPanel() {
    console.log("Initializing properties panel...");
    
    // Show "no selection" message if no clip is selected
    document.getElementById('no-selection').style.display = 'block';
    document.getElementById('clip-properties').style.display = 'none';
}

// Add event listeners
function addEventListeners() {
    // Export button
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            showExportDialog();
        });
    }
    
    // Save button
    const saveBtn = document.getElementById('save-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
            saveProject();
        });
    }
    
    // AI Assist button
    const aiAssistBtn = document.getElementById('ai-assist-btn');
    if (aiAssistBtn) {
        aiAssistBtn.addEventListener('click', function() {
            showAIAssistDialog();
        });
    }
}

// UI Helper Functions

// Show media upload dialog
function showMediaUploadDialog() {
    console.log("Showing media upload dialog...");
    
    // Create modal dialog HTML
    const modalHTML = `
    <div class="modal fade" id="uploadMediaModal" tabindex="-1" aria-labelledby="uploadMediaModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content bg-dark text-light">
                <div class="modal-header">
                    <h5 class="modal-title" id="uploadMediaModalLabel">Upload Media</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="uploadMediaForm" enctype="multipart/form-data">
                        <div class="mb-3">
                            <label for="mediaFile" class="form-label">Select media file</label>
                            <input type="file" class="form-control bg-dark text-light" id="mediaFile" name="file" accept="video/*,audio/*,image/*">
                        </div>
                        <div class="mb-3">
                            <label for="mediaType" class="form-label">Media type</label>
                            <select class="form-select bg-dark text-light" id="mediaType" name="type">
                                <option value="video">Video</option>
                                <option value="audio">Audio</option>
                                <option value="image">Image</option>
                            </select>
                        </div>
                        <input type="hidden" name="project_id" value="${projectData.id}">
                    </form>
                    <div class="progress d-none mt-3" id="uploadProgress">
                        <div class="progress-bar bg-primary" role="progressbar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="uploadMediaBtn">Upload</button>
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Add modal to the document
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Initialize the modal
    const modal = new bootstrap.Modal(document.getElementById('uploadMediaModal'));
    modal.show();
    
    // Handle file upload
    document.getElementById('uploadMediaBtn').addEventListener('click', function() {
        const form = document.getElementById('uploadMediaForm');
        const formData = new FormData(form);
        const fileInput = document.getElementById('mediaFile');
        
        if (!fileInput.files.length) {
            alert('Please select a file to upload');
            return;
        }
        
        // Show progress bar
        const progressBar = document.querySelector('#uploadProgress .progress-bar');
        document.getElementById('uploadProgress').classList.remove('d-none');
        
        // Upload file with XHR to show progress
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/assets/upload', true);
        
        xhr.upload.onprogress = function(e) {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progressBar.style.width = percentComplete + '%';
            }
        };
        
        xhr.onload = function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                
                if (response.success) {
                    // Add the new asset to the project data
                    if (!projectData.assets) {
                        projectData.assets = [];
                    }
                    
                    projectData.assets.push(response.asset);
                    
                    // Close the modal
                    modal.hide();
                    
                    // Show success message
                    alert('Media uploaded successfully!');
                    
                    // Refresh the media library display
                    refreshMediaLibrary();
                } else {
                    alert('Error uploading media: ' + response.error);
                }
            } else {
                alert('Error uploading media. Please try again.');
            }
        };
        
        xhr.onerror = function() {
            alert('Error uploading media. Please try again.');
        };
        
        xhr.send(formData);
    });
    
    // Clean up the modal when it's hidden
    document.getElementById('uploadMediaModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// Refresh media library display
function refreshMediaLibrary() {
    const mediaList = document.querySelector('.media-list');
    const itemsSection = mediaList.querySelector('div:not(.mb-3):not(.ai-tools)');
    
    // Clear existing items (except the search box and AI tools)
    if (itemsSection) {
        itemsSection.innerHTML = '';
    }
    
    // Re-add the header
    let mediaItemsHTML = `
    <div class="d-flex justify-content-between mb-2">
        <div>
            <span class="text-light">Files</span>
        </div>
        <div>
            <a href="#" class="text-light small"><i class="bi bi-sort-down"></i> Date</a>
        </div>
    </div>
    `;
    
    // Add media items
    if (projectData.assets && projectData.assets.length > 0) {
        projectData.assets.forEach((asset, index) => {
            let icon = 'bi-file';
            let color = '#4a6cf7';
            
            if (asset.type === 'video') {
                icon = 'bi-film';
                color = '#4a6cf7';
            } else if (asset.type === 'audio') {
                icon = 'bi-music-note-beamed';
                color = '#50cd89';
            } else if (asset.type === 'image') {
                icon = 'bi-image';
                color = '#ffc700';
            }
            
            mediaItemsHTML += `
            <div class="media-item" data-asset-id="${asset.id}" draggable="true">
                <div class="d-flex align-items-center">
                    <i class="${icon} me-2" style="color: ${color};"></i>
                    <div>
                        <div class="fw-bold">${asset.name}
                            ${index === 0 ? '<span class="ai-badge"><i class="bi bi-stars"></i>AI</span>' : ''}
                        </div>
                        <small style="color: #a0a0c2;">${asset.duration || '--'}s</small>
                    </div>
                </div>
            </div>
            `;
        });
    } else {
        mediaItemsHTML += `
        <div class="text-center py-4">
            <i class="bi bi-upload display-6" style="color: #4a6cf7;"></i>
            <p class="mt-2" style="color: #a0a0c2;">No media files</p>
            <button class="btn btn-sm mt-2" style="background: linear-gradient(135deg, #4a6cf7, #7239ea); color: white;" id="upload-first-media-btn">Upload Media</button>
        </div>
        `;
    }
    
    // Add the HTML to the media list
    if (itemsSection) {
        itemsSection.innerHTML = mediaItemsHTML;
    } else {
        mediaList.insertAdjacentHTML('beforeend', mediaItemsHTML);
    }
    
    // Add event listeners for the new items
    const mediaItems = document.querySelectorAll('.media-item');
    const uploadFirstBtn = document.getElementById('upload-first-media-btn');
    
    mediaItems.forEach(item => {
        item.addEventListener('dragstart', function(e) {
            e.dataTransfer.setData('text/plain', item.dataset.assetId);
            e.dataTransfer.effectAllowed = 'copy';
        });
    });
    
    if (uploadFirstBtn) {
        uploadFirstBtn.addEventListener('click', function() {
            showMediaUploadDialog();
        });
    }
}

// Show export dialog
function showExportDialog() {
    console.log("Showing export dialog...");
    
    // Create modal dialog HTML
    const modalHTML = `
    <div class="modal fade" id="exportModal" tabindex="-1" aria-labelledby="exportModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content bg-dark text-light">
                <div class="modal-header">
                    <h5 class="modal-title" id="exportModalLabel">Export Video</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="exportForm">
                        <div class="mb-3">
                            <label for="exportFormat" class="form-label">Format</label>
                            <select class="form-select bg-dark text-light" id="exportFormat" name="format">
                                <option value="mp4">MP4 (H.264)</option>
                                <option value="webm">WebM (VP9)</option>
                                <option value="mov">MOV (ProRes)</option>
                                <option value="gif">GIF (Animated)</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="exportResolution" class="form-label">Resolution</label>
                            <select class="form-select bg-dark text-light" id="exportResolution" name="resolution">
                                <option value="1080p">1080p (1920x1080)</option>
                                <option value="720p">720p (1280x720)</option>
                                <option value="480p">480p (854x480)</option>
                                <option value="4k">4K (3840x2160)</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="exportQuality" class="form-label">Quality</label>
                            <select class="form-select bg-dark text-light" id="exportQuality" name="quality">
                                <option value="high">High (10 credits)</option>
                                <option value="medium">Medium (5 credits)</option>
                                <option value="low">Low (Free)</option>
                            </select>
                        </div>
                        <input type="hidden" name="project_id" value="${projectData.id}">
                    </form>
                    <div class="progress d-none mt-3" id="exportProgress">
                        <div class="progress-bar bg-primary" role="progressbar" style="width: 0%"></div>
                    </div>
                    <div class="d-none mt-3" id="exportStatus">
                        <div class="alert alert-info">
                            <div class="d-flex align-items-center">
                                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                                <span id="exportStatusText">Starting export...</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="startExportBtn">Export</button>
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Add modal to the document
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Initialize the modal
    const modal = new bootstrap.Modal(document.getElementById('exportModal'));
    modal.show();
    
    // Handle export
    document.getElementById('startExportBtn').addEventListener('click', function() {
        const form = document.getElementById('exportForm');
        const formData = new FormData(form);
        const exportData = {};
        
        // Convert FormData to JSON object
        for (const [key, value] of formData.entries()) {
            exportData[key] = value;
        }
        
        // Show progress and status
        document.getElementById('exportProgress').classList.remove('d-none');
        document.getElementById('exportStatus').classList.remove('d-none');
        document.getElementById('startExportBtn').disabled = true;
        
        // Make request to create export job
        fetch('/api/exports', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(exportData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Start polling for export status
                const exportId = data.export.id;
                pollExportStatus(exportId);
            } else {
                // Show error
                document.getElementById('exportStatusText').textContent = 'Error: ' + (data.error || 'Unknown error');
                document.getElementById('exportProgress').classList.add('d-none');
                document.getElementById('startExportBtn').disabled = false;
            }
        })
        .catch(error => {
            console.error('Error starting export:', error);
            document.getElementById('exportStatusText').textContent = 'Error starting export. Please try again.';
            document.getElementById('exportProgress').classList.add('d-none');
            document.getElementById('startExportBtn').disabled = false;
        });
    });
    
    // Clean up the modal when it's hidden
    document.getElementById('exportModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// Poll export status
function pollExportStatus(exportId) {
    const statusElement = document.getElementById('exportStatusText');
    const progressBar = document.querySelector('#exportProgress .progress-bar');
    
    const checkStatus = () => {
        fetch(`/api/exports/${exportId}`)
            .then(response => response.json())
            .then(data => {
                if (data.export) {
                    const export_job = data.export;
                    const progress = export_job.progress || 0;
                    
                    // Update progress bar
                    progressBar.style.width = `${progress}%`;
                    
                    // Update status text
                    statusElement.textContent = `${export_job.status}: ${progress}%`;
                    
                    // Check if export is complete
                    if (export_job.status === 'completed') {
                        statusElement.textContent = 'Export completed!';
                        
                        // Show download link
                        const exportStatus = document.getElementById('exportStatus');
                        exportStatus.innerHTML = `
                            <div class="alert alert-success">
                                <strong>Export completed!</strong><br>
                                <a href="/exports/${exportId}/download" class="btn btn-primary mt-2">
                                    <i class="bi bi-download"></i> Download Video
                                </a>
                            </div>
                        `;
                        
                        return;
                    } else if (export_job.status === 'failed') {
                        statusElement.textContent = 'Export failed: ' + (export_job.error || 'Unknown error');
                        return;
                    }
                    
                    // Continue polling if not complete
                    setTimeout(checkStatus, 2000);
                } else {
                    statusElement.textContent = 'Error: Could not get export status';
                }
            })
            .catch(error => {
                console.error('Error checking export status:', error);
                statusElement.textContent = 'Error checking export status. Retrying...';
                
                // Retry in 5 seconds
                setTimeout(checkStatus, 5000);
            });
    };
    
    // Start checking status
    checkStatus();
}

// Show AI assist dialog
function showAIAssistDialog() {
    console.log("Showing AI assist dialog...");
    alert("AI assist feature not implemented yet.");
}

// Initialize theme switcher
function initThemeSwitcher() {
    console.log("Initializing theme switcher...");
    
    // Add theme switcher button to editor header
    const editorHeader = document.querySelector('.editor-header > div:last-child');
    
    if (editorHeader) {
        // Create the theme switcher button and dropdown
        const themeSwitcherHTML = `
            <div class="theme-switcher me-2">
                <button class="btn btn-outline-light btn-sm" id="theme-toggle-btn">
                    <i class="bi bi-palette"></i> Theme
                </button>
                <div class="theme-dropdown">
                    <div class="theme-option" data-theme="default">
                        <div class="theme-color dark"></div>
                        <span>Dark (Default)</span>
                    </div>
                    <div class="theme-option" data-theme="blue">
                        <div class="theme-color blue"></div>
                        <span>Blue Ocean</span>
                    </div>
                    <div class="theme-option" data-theme="green">
                        <div class="theme-color green"></div>
                        <span>Forest Green</span>
                    </div>
                    <div class="theme-option" data-theme="high-contrast">
                        <div class="theme-color high-contrast"></div>
                        <span>High Contrast</span>
                    </div>
                </div>
            </div>
        `;
        
        // Insert the theme switcher before the first button
        editorHeader.insertAdjacentHTML('afterbegin', themeSwitcherHTML);
        
        // Add event listeners to theme options
        const themeOptions = document.querySelectorAll('.theme-option');
        themeOptions.forEach(option => {
            option.addEventListener('click', function() {
                const theme = this.dataset.theme;
                setTheme(theme);
                
                // Mark this option as active
                themeOptions.forEach(opt => opt.classList.remove('active'));
                this.classList.add('active');
                
                // Save theme preference to localStorage
                localStorage.setItem('editor_theme', theme);
            });
        });
        
        // Load saved theme preference or use default
        const savedTheme = localStorage.getItem('editor_theme');
        if (savedTheme) {
            setTheme(savedTheme);
            
            // Mark the saved theme option as active
            const activeOption = document.querySelector(`.theme-option[data-theme="${savedTheme}"]`);
            if (activeOption) {
                activeOption.classList.add('active');
            }
        } else {
            // Mark default theme as active
            const defaultOption = document.querySelector('.theme-option[data-theme="default"]');
            if (defaultOption) {
                defaultOption.classList.add('active');
            }
        }
    }
}

// Set the theme
function setTheme(theme) {
    // Remove any existing theme classes
    document.documentElement.classList.remove('theme-blue', 'theme-green', 'theme-high-contrast');
    
    // Add the selected theme class if not default
    if (theme !== 'default') {
        document.documentElement.classList.add(`theme-${theme}`);
    }
    
    console.log(`Theme set to: ${theme}`);
}

// Save project
function saveProject() {
    console.log("Saving project...");
    
    // Make an AJAX request to save project
    fetch(`/api/projects/${projectData.id}/save`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(projectData)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Project saved:", data);
        showSuccess("Project saved successfully");
    })
    .catch(error => {
        console.error("Error saving project:", error);
        showError("Error saving project");
    });
}

// Playback Functions

// Toggle play/pause
function togglePlayback() {
    console.log("Toggle playback");
    
    const playBtn = document.getElementById('play-btn');
    const playIcon = playBtn.querySelector('i');
    
    if (playIcon.classList.contains('bi-play-fill')) {
        // Start playback
        playIcon.classList.remove('bi-play-fill');
        playIcon.classList.add('bi-pause-fill');
        startPlayback();
    } else {
        // Pause playback
        playIcon.classList.remove('bi-pause-fill');
        playIcon.classList.add('bi-play-fill');
        pausePlayback();
    }
}

// Start playback
function startPlayback() {
    console.log("Starting playback...");
    
    // For now, we'll just animate the playhead
    // This would be replaced with actual OpenShot playback
    animatePlayhead();
}

// Pause playback
function pausePlayback() {
    console.log("Pausing playback...");
    
    // Stop playhead animation
    if (window.playheadInterval) {
        clearInterval(window.playheadInterval);
    }
}

// Animate playhead
function animatePlayhead() {
    // Get current playhead position
    const playhead = document.querySelector('.timeline-playhead');
    const currentLeft = parseInt(playhead.style.left) || 0;
    
    // Clear any existing interval
    if (window.playheadInterval) {
        clearInterval(window.playheadInterval);
    }
    
    // Set up new interval to move playhead
    window.playheadInterval = setInterval(() => {
        const newPos = (parseInt(playhead.style.left) || 0) + 1;
        
        // Check if we've reached the end
        if (newPos >= 600) {
            clearInterval(window.playheadInterval);
            const playBtn = document.getElementById('play-btn');
            const playIcon = playBtn.querySelector('i');
            playIcon.classList.remove('bi-pause-fill');
            playIcon.classList.add('bi-play-fill');
            return;
        }
        
        // Update playhead position
        playhead.style.left = `${newPos}px`;
        
        // Update scrubber position
        updateScrubberPosition(newPos / 600);
        
        // Update current time display
        const totalTime = projectData.timeline.duration || 60;
        const currentTime = (newPos / 600) * totalTime;
        document.getElementById('current-time').textContent = formatTime(currentTime);
    }, 50);
}

// Seek to frame
function seekFrame(direction) {
    console.log(`Seeking frame: ${direction}`);
    
    // Get current playhead position
    const playhead = document.querySelector('.timeline-playhead');
    let currentPos = parseInt(playhead.style.left) || 0;
    
    // Move by 5 pixels in the specified direction
    currentPos += (direction * 5);
    
    // Ensure we stay within bounds
    currentPos = Math.max(0, Math.min(600, currentPos));
    
    // Update playhead position
    playhead.style.left = `${currentPos}px`;
    
    // Update scrubber position
    updateScrubberPosition(currentPos / 600);
    
    // Update current time display
    const totalTime = projectData.timeline.duration || 60;
    const currentTime = (currentPos / 600) * totalTime;
    document.getElementById('current-time').textContent = formatTime(currentTime);
}

// Toggle mute
function toggleMute() {
    console.log("Toggle mute");
    
    const muteBtn = document.getElementById('mute-btn');
    const muteIcon = muteBtn.querySelector('i');
    
    if (muteIcon.classList.contains('bi-volume-up-fill')) {
        // Mute
        muteIcon.classList.remove('bi-volume-up-fill');
        muteIcon.classList.add('bi-volume-mute-fill');
    } else {
        // Unmute
        muteIcon.classList.remove('bi-volume-mute-fill');
        muteIcon.classList.add('bi-volume-up-fill');
    }
}

// Seek to position
function seekToPosition(e) {
    const scrubber = document.querySelector('.timeline-scrubber');
    const rect = scrubber.getBoundingClientRect();
    const clickPos = (e.clientX - rect.left) / rect.width;
    
    // Update scrubber position
    updateScrubberPosition(clickPos);
    
    // Update playhead position
    const playhead = document.querySelector('.timeline-playhead');
    const newPos = clickPos * 600;
    playhead.style.left = `${newPos}px`;
    
    // Update current time display
    const totalTime = projectData.timeline.duration || 60;
    const currentTime = clickPos * totalTime;
    document.getElementById('current-time').textContent = formatTime(currentTime);
}

// Update scrubber position
function updateScrubberPosition(position) {
    // Ensure position is between 0 and 1
    position = Math.max(0, Math.min(1, position));
    
    // Update progress bar
    const progress = document.querySelector('.timeline-scrubber .progress');
    progress.style.width = `${position * 100}%`;
    
    // Update handle position
    const handle = document.querySelector('.timeline-scrubber .handle');
    handle.style.left = `${position * 100}%`;
}

// Initialize playhead dragging
function initPlayheadDragging() {
    const playhead = document.querySelector('.timeline-playhead');
    const timeline = document.querySelector('.timeline-tracks');
    
    let isDragging = false;
    
    playhead.addEventListener('mousedown', function(e) {
        isDragging = true;
        e.preventDefault();
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        
        const rect = timeline.getBoundingClientRect();
        let newPos = e.clientX - rect.left;
        
        // Ensure we stay within bounds
        newPos = Math.max(0, Math.min(rect.width, newPos));
        
        // Update playhead position
        playhead.style.left = `${newPos}px`;
        
        // Update scrubber position
        updateScrubberPosition(newPos / 600);
        
        // Update current time display
        const totalTime = projectData.timeline.duration || 60;
        const currentTime = (newPos / 600) * totalTime;
        document.getElementById('current-time').textContent = formatTime(currentTime);
    });
    
    document.addEventListener('mouseup', function() {
        isDragging = false;
    });
}

// Initialize clip dragging
function initClipDragging() {
    const clips = document.querySelectorAll('.clip');
    
    clips.forEach(clip => {
        let isDragging = false;
        let startX, startLeft;
        
        clip.addEventListener('mousedown', function(e) {
            isDragging = true;
            startX = e.clientX;
            startLeft = parseInt(clip.style.left) || 0;
            
            // Show properties for selected clip
            showClipProperties(clip);
            
            e.preventDefault();
        });
        
        document.addEventListener('mousemove', function(e) {
            if (!isDragging) return;
            
            const dx = e.clientX - startX;
            let newLeft = startLeft + dx;
            
            // Ensure we stay within bounds
            newLeft = Math.max(0, newLeft);
            
            // Update clip position
            clip.style.left = `${newLeft}px`;
        });
        
        document.addEventListener('mouseup', function() {
            isDragging = false;
        });
    });
}

// Initialize media drag and drop
function initMediaDragAndDrop() {
    const mediaItems = document.querySelectorAll('.media-item');
    const trackContents = document.querySelectorAll('.track-content');
    
    mediaItems.forEach(item => {
        item.setAttribute('draggable', 'true');
        
        item.addEventListener('dragstart', function(e) {
            e.dataTransfer.setData('text/plain', item.dataset.assetId || 'demo-asset');
            e.dataTransfer.effectAllowed = 'copy';
        });
    });
    
    trackContents.forEach(track => {
        track.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            track.classList.add('drag-over');
        });
        
        track.addEventListener('dragleave', function() {
            track.classList.remove('drag-over');
        });
        
        track.addEventListener('drop', function(e) {
            e.preventDefault();
            track.classList.remove('drag-over');
            
            const assetId = e.dataTransfer.getData('text/plain');
            const trackRect = track.getBoundingClientRect();
            const dropPos = e.clientX - trackRect.left;
            
            // Add clip to timeline
            addClipToTimeline(track, assetId, dropPos);
        });
    });
}

// Add clip to timeline
function addClipToTimeline(track, assetId, position) {
    console.log(`Adding clip ${assetId} to timeline at position ${position}`);
    
    // Find asset in project data
    let asset = projectData.assets.find(a => a.id === assetId);
    
    // If asset not found, use dummy data
    if (!asset) {
        asset = {
            id: `dummy-${Math.random().toString(36).substring(2, 9)}`,
            name: "New Clip",
            type: track.id.includes('audio') ? 'audio' : 'video'
        };
    }
    
    // Create clip element
    const clip = document.createElement('div');
    clip.className = 'clip';
    
    // Add audio class if needed
    if (asset.type === 'audio') {
        clip.classList.add('audio');
    }
    
    // Add effect class if needed
    if (track.id.includes('effect')) {
        clip.classList.add('effect');
    }
    
    // Set clip properties
    clip.textContent = asset.name;
    clip.style.left = `${position}px`;
    clip.style.width = '150px';
    clip.dataset.clipId = `clip-${Math.random().toString(36).substring(2, 9)}`;
    clip.dataset.assetId = asset.id;
    
    // Add clip to track
    track.appendChild(clip);
    
    // Initialize dragging for new clip
    let isDragging = false;
    let startX, startLeft;
    
    clip.addEventListener('mousedown', function(e) {
        isDragging = true;
        startX = e.clientX;
        startLeft = parseInt(clip.style.left) || 0;
        
        // Show properties for selected clip
        showClipProperties(clip);
        
        e.preventDefault();
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        
        const dx = e.clientX - startX;
        let newLeft = startLeft + dx;
        
        // Ensure we stay within bounds
        newLeft = Math.max(0, newLeft);
        
        // Update clip position
        clip.style.left = `${newLeft}px`;
    });
    
    document.addEventListener('mouseup', function() {
        isDragging = false;
    });
}

// Show clip properties
function showClipProperties(clip) {
    // Hide no selection message
    document.getElementById('no-selection').style.display = 'none';
    
    // Show clip properties
    document.getElementById('clip-properties').style.display = 'block';
    
    // Update form fields with clip data
    document.getElementById('clip-start-time').value = parseInt(clip.style.left) / 10 || 0;
    document.getElementById('clip-duration').value = parseInt(clip.style.width) / 10 || 15;
    
    // Highlight selected clip
    document.querySelectorAll('.clip').forEach(c => {
        c.classList.remove('selected');
    });
    clip.classList.add('selected');
}

// Format time (seconds to MM:SS:FF format)
function formatTime(seconds) {
    const min = Math.floor(seconds / 60).toString().padStart(2, '0');
    const sec = Math.floor(seconds % 60).toString().padStart(2, '0');
    const frames = Math.floor((seconds * 30) % 30).toString().padStart(2, '0');
    
    return `${min}:${sec}:${frames}`;
}

// Show success notification
function showSuccess(message) {
    // For now, just alert
    console.log("SUCCESS:", message);
}

// Show error notification
function showError(message) {
    // For now, just alert
    console.error("ERROR:", message);
}