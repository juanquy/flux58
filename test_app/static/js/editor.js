/**
 * OpenShot Video Editor - Main JavaScript
 * Main functionality for the video editor interface
 */

// Initialize editor when DOM content is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("Editor script loaded");
    
    // Initialize editor
    initEditor();
    
    // Log project data
    console.log("Project data:", projectData);
    
    // Make sure the workflow selectors are properly initialized
    // This ensures the dropdown correctly shows the selected workflow mode
    setTimeout(() => {
        console.log("Ensuring workflow selectors are initialized");
        const workflowItems = document.querySelectorAll('[data-workflow]');
        if (workflowItems && workflowItems.length > 0) {
            console.log(`Found ${workflowItems.length} workflow items`);
            // Ensure Standard mode is initially selected
            updateWorkflowMenu('standard');
        } else {
            console.warn("No workflow items found");
        }
    }, 500);
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
    
    // Add event listeners for editor actions
    addEventListeners();
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
                showNotification('success', 'OpenShot library loaded successfully: ' + data.version);
            } else {
                console.warn("OpenShot is not available. Some features will be limited.");
                showNotification('warning', 'OpenShot library is not available. Some video editing features will be limited.');
            }
        })
        .catch(error => {
            console.error("Error checking OpenShot status:", error);
            showNotification('error', 'Error connecting to OpenShot. Some features may not work.');
        });
}

// Initialize timeline
function initTimeline() {
    console.log("Initializing timeline...");
    
    // Generate time markers
    generateTimeMarkers();
    
    // Initialize timeline playhead
    initPlayhead();
    
    // Initialize clip drag and drop functionality
    initClipDragAndDrop();
    
    // Populate timeline with any existing clips
    populateTimeline();
}

// Generate time markers based on project duration
function generateTimeMarkers() {
    const duration = projectData.timeline.duration || 60;
    const timeMarkers = document.getElementById('timeline-markers');
    
    if (!timeMarkers) return;
    
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

// Initialize playhead functionality
function initPlayhead() {
    const playhead = document.getElementById('timeline-playhead');
    const timelineTracks = document.getElementById('timeline-tracks');
    
    if (!playhead || !timelineTracks) return;
    
    // Set initial playhead position
    playhead.style.left = '0px';
    
    // Initialize playhead dragging
    let isDragging = false;
    
    // Handle playhead mousedown
    playhead.addEventListener('mousedown', function(e) {
        isDragging = true;
        e.preventDefault();
    });
    
    // Handle document mousemove to drag playhead
    document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        
        const rect = timelineTracks.getBoundingClientRect();
        let newPos = e.clientX - rect.left;
        
        // Ensure we stay within bounds
        newPos = Math.max(0, Math.min(rect.width, newPos));
        
        // Update playhead position
        playhead.style.left = `${newPos}px`;
        
        // Update scrubber position
        updateScrubberPosition(newPos / rect.width);
        
        // Update current time display
        const totalTime = projectData.timeline.duration || 60;
        const currentTime = (newPos / rect.width) * totalTime;
        document.getElementById('current-time').textContent = formatTime(currentTime);
    });
    
    // Handle document mouseup to stop dragging
    document.addEventListener('mouseup', function() {
        isDragging = false;
    });
    
    // Allow clicking directly on the timeline to move playhead
    timelineTracks.addEventListener('click', function(e) {
        if (e.target === playhead) return;
        
        const rect = timelineTracks.getBoundingClientRect();
        let newPos = e.clientX - rect.left;
        
        // Ensure we stay within bounds
        newPos = Math.max(0, Math.min(rect.width, newPos));
        
        // Update playhead position
        playhead.style.left = `${newPos}px`;
        
        // Update scrubber position
        updateScrubberPosition(newPos / rect.width);
        
        // Update current time display
        const totalTime = projectData.timeline.duration || 60;
        const currentTime = (newPos / rect.width) * totalTime;
        document.getElementById('current-time').textContent = formatTime(currentTime);
    });
}

// Initialize clip drag and drop functionality
function initClipDragAndDrop() {
    const trackContents = document.querySelectorAll('.track-content');
    
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
            
            // Get the asset ID from the dragged element
            const assetId = e.dataTransfer.getData('text/plain');
            
            // Calculate drop position relative to the track
            const rect = track.getBoundingClientRect();
            const dropPos = e.clientX - rect.left;
            
            // Add clip to timeline
            addClipToTimeline(track, assetId, dropPos);
        });
    });
}

// Populate timeline with existing clips from project data
function populateTimeline() {
    if (!projectData.timeline || !projectData.timeline.tracks) return;
    
    projectData.timeline.tracks.forEach(track => {
        const trackElement = document.querySelector(`.track-content[data-track-id="${track.id}"]`);
        
        if (!trackElement || !track.clips) return;
        
        track.clips.forEach(clip => {
            // Find the corresponding asset
            const asset = projectData.assets.find(a => a.id === clip.asset_id);
            
            if (!asset) return;
            
            // Create a clip element
            const clipElement = createClipElement(clip, asset);
            
            // Add clip to the track
            trackElement.appendChild(clipElement);
            
            // Initialize clip dragging
            initClipDragging(clipElement);
        });
    });
}

// Create a clip element for the timeline
function createClipElement(clip, asset) {
    const clipElement = document.createElement('div');
    clipElement.className = 'clip';
    clipElement.draggable = true;
    clipElement.dataset.clipId = clip.id;
    clipElement.dataset.assetId = asset.id;
    
    // Add appropriate class based on asset type
    if (asset.type === 'audio') {
        clipElement.classList.add('audio');
    } else if (asset.type === 'video') {
        clipElement.classList.add('video');
    } else if (asset.type === 'image') {
        clipElement.classList.add('image');
    } else if (asset.type === 'text') {
        clipElement.classList.add('text');
    } else if (asset.type === 'effect') {
        clipElement.classList.add('effect');
    }
    
    // Set position and duration
    clipElement.style.left = `${clip.position * 10}px`;
    clipElement.style.width = `${clip.duration * 10}px`;
    
    // Add clip label
    const clipLabel = document.createElement('div');
    clipLabel.className = 'clip-label';
    clipLabel.textContent = asset.name;
    clipElement.appendChild(clipLabel);
    
    return clipElement;
}

// Initialize dragging behavior for a clip
function initClipDragging(clipElement) {
    let isDragging = false;
    let startX, startLeft;
    
    clipElement.addEventListener('mousedown', function(e) {
        // Prevent from triggering on the resize handles
        if (e.target.classList.contains('clip-resize-handle')) return;
        
        isDragging = true;
        startX = e.clientX;
        startLeft = parseInt(clipElement.style.left) || 0;
        
        // Select this clip
        selectClip(clipElement);
        
        e.stopPropagation();
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        
        const dx = e.clientX - startX;
        let newLeft = startLeft + dx;
        
        // Ensure we stay within bounds (don't go negative)
        newLeft = Math.max(0, newLeft);
        
        // Update clip position
        clipElement.style.left = `${newLeft}px`;
        
        // Update clip properties in the panel
        updateClipPositionProperty(newLeft / 10);
    });
    
    document.addEventListener('mouseup', function() {
        if (!isDragging) return;
        
        isDragging = false;
        
        // Update the clip data in the project
        updateClipData(clipElement);
    });
    
    // Add resize handles to the clip
    addClipResizeHandles(clipElement);
}

// Add resize handles to a clip
function addClipResizeHandles(clipElement) {
    // Left resize handle
    const leftHandle = document.createElement('div');
    leftHandle.className = 'clip-resize-handle clip-resize-left';
    clipElement.appendChild(leftHandle);
    
    // Right resize handle
    const rightHandle = document.createElement('div');
    rightHandle.className = 'clip-resize-handle clip-resize-right';
    clipElement.appendChild(rightHandle);
    
    // Initialize resizing behavior for the left handle
    initClipResize(leftHandle, 'left');
    
    // Initialize resizing behavior for the right handle
    initClipResize(rightHandle, 'right');
}

// Initialize resize behavior for a clip handle
function initClipResize(handle, direction) {
    let isResizing = false;
    let startX, startWidth, startLeft;
    
    handle.addEventListener('mousedown', function(e) {
        isResizing = true;
        startX = e.clientX;
        const clipElement = handle.parentElement;
        startWidth = parseInt(clipElement.style.width) || 100;
        startLeft = parseInt(clipElement.style.left) || 0;
        
        // Select this clip
        selectClip(clipElement);
        
        e.stopPropagation();
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isResizing) return;
        
        const dx = e.clientX - startX;
        const clipElement = handle.parentElement;
        
        if (direction === 'right') {
            // Resize from the right (changes width)
            let newWidth = startWidth + dx;
            newWidth = Math.max(20, newWidth); // Minimum width of 20px
            clipElement.style.width = `${newWidth}px`;
            
            // Update clip duration in properties panel
            updateClipDurationProperty(newWidth / 10);
        } else {
            // Resize from the left (changes both left position and width)
            let newLeft = startLeft + dx;
            let newWidth = startWidth - dx;
            
            if (newWidth < 20) {
                newWidth = 20;
                newLeft = startLeft + startWidth - 20;
            }
            
            clipElement.style.left = `${newLeft}px`;
            clipElement.style.width = `${newWidth}px`;
            
            // Update clip position and duration in properties panel
            updateClipPositionProperty(newLeft / 10);
            updateClipDurationProperty(newWidth / 10);
        }
    });
    
    document.addEventListener('mouseup', function() {
        if (!isResizing) return;
        
        isResizing = false;
        
        // Update the clip data in the project
        const clipElement = handle.parentElement;
        updateClipData(clipElement);
    });
}

// Update clip data in the project
function updateClipData(clipElement) {
    if (!clipElement || !clipElement.dataset.clipId) return;
    
    const clipId = clipElement.dataset.clipId;
    const position = parseInt(clipElement.style.left) / 10;
    const duration = parseInt(clipElement.style.width) / 10;
    
    // Find the track and clip in project data
    projectData.timeline.tracks.forEach(track => {
        const clipIndex = track.clips.findIndex(c => c.id === clipId);
        
        if (clipIndex !== -1) {
            // Update clip data
            track.clips[clipIndex].position = position;
            track.clips[clipIndex].duration = duration;
        }
    });
}

// Add a clip to the timeline
function addClipToTimeline(trackElement, assetId, position) {
    // Find the asset in project data
    const asset = projectData.assets.find(a => a.id === assetId);
    
    if (!asset) {
        console.warn(`Asset with ID ${assetId} not found`);
        return;
    }
    
    // Create a unique ID for the clip
    const clipId = `clip-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
    
    // Create clip data
    const clipData = {
        id: clipId,
        asset_id: assetId,
        position: position / 10, // Convert from pixels to seconds
        duration: 5.0, // Default duration in seconds
        volume: 1.0,
        speed: 1.0,
        effects: []
    };
    
    // Add clip to project data
    const trackId = trackElement.dataset.trackId;
    const trackIndex = projectData.timeline.tracks.findIndex(t => t.id === trackId);
    
    if (trackIndex !== -1) {
        if (!projectData.timeline.tracks[trackIndex].clips) {
            projectData.timeline.tracks[trackIndex].clips = [];
        }
        
        projectData.timeline.tracks[trackIndex].clips.push(clipData);
    } else {
        console.warn(`Track with ID ${trackId} not found`);
    }
    
    // Create clip element
    const clipElement = createClipElement(clipData, asset);
    
    // Add clip to track
    trackElement.appendChild(clipElement);
    
    // Initialize clip dragging
    initClipDragging(clipElement);
    
    // Select the new clip
    selectClip(clipElement);
    
    // Show success notification
    showNotification('success', `Added ${asset.name} to timeline`);
}

// Select a clip and show its properties
function selectClip(clipElement) {
    // Deselect all clips
    document.querySelectorAll('.clip').forEach(clip => {
        clip.classList.remove('selected');
    });
    
    // Select this clip
    clipElement.classList.add('selected');
    
    // Show clip properties
    document.getElementById('no-selection').style.display = 'none';
    document.getElementById('clip-properties').style.display = 'block';
    
    // Update properties panel with clip data
    updatePropertiesPanel(clipElement);
}

// Update properties panel with clip data
function updatePropertiesPanel(clipElement) {
    const startTimeInput = document.getElementById('clip-start-time');
    const durationInput = document.getElementById('clip-duration');
    const volumeInput = document.getElementById('clip-volume');
    const posXInput = document.getElementById('clip-position-x');
    const posYInput = document.getElementById('clip-position-y');
    const scaleInput = document.getElementById('clip-scale');
    const rotationInput = document.getElementById('clip-rotation');
    
    // Get clip data from the element
    const position = parseInt(clipElement.style.left) / 10;
    const duration = parseInt(clipElement.style.width) / 10;
    
    // Update inputs
    if (startTimeInput) startTimeInput.value = position;
    if (durationInput) durationInput.value = duration;
    
    // Get clip data from project data
    const clipId = clipElement.dataset.clipId;
    const clipData = findClipDataById(clipId);
    
    if (clipData) {
        if (volumeInput) volumeInput.value = clipData.volume || 1.0;
        if (posXInput) posXInput.value = clipData.position_x || 0;
        if (posYInput) posYInput.value = clipData.position_y || 0;
        if (scaleInput) scaleInput.value = clipData.scale || 1.0;
        if (rotationInput) rotationInput.value = clipData.rotation || 0;
        
        // Update effects list
        updateEffectsList(clipData.effects || []);
    }
    
    // Add event listeners to inputs for updating clip data
    addPropertyChangeListeners(clipElement);
}

// Update the clip duration property in the panel
function updateClipDurationProperty(duration) {
    const durationInput = document.getElementById('clip-duration');
    if (durationInput) durationInput.value = duration;
}

// Update the clip position property in the panel
function updateClipPositionProperty(position) {
    const startTimeInput = document.getElementById('clip-start-time');
    if (startTimeInput) startTimeInput.value = position;
}

// Find clip data by ID in project data
function findClipDataById(clipId) {
    let foundClip = null;
    
    projectData.timeline.tracks.forEach(track => {
        if (!track.clips) return;
        
        const clip = track.clips.find(c => c.id === clipId);
        if (clip) foundClip = clip;
    });
    
    return foundClip;
}

// Update the effects list in the properties panel
function updateEffectsList(effects) {
    const effectsList = document.getElementById('active-effects');
    if (!effectsList) return;
    
    // Clear current effects
    effectsList.innerHTML = '';
    
    // Add each effect to the list
    effects.forEach(effect => {
        const effectItem = document.createElement('div');
        effectItem.className = 'list-group-item bg-transparent text-light border-secondary d-flex justify-content-between align-items-center';
        effectItem.dataset.effectId = effect.id;
        
        const effectName = document.createElement('div');
        effectName.textContent = effect.name;
        
        const removeButton = document.createElement('button');
        removeButton.className = 'btn btn-sm btn-outline-danger';
        removeButton.innerHTML = '<i class="bi bi-trash"></i>';
        
        // Add click handler to remove button
        removeButton.addEventListener('click', function() {
            removeEffect(effect.id);
        });
        
        effectItem.appendChild(effectName);
        effectItem.appendChild(removeButton);
        effectsList.appendChild(effectItem);
    });
}

// Remove an effect from a clip
function removeEffect(effectId) {
    // Find the selected clip
    const selectedClip = document.querySelector('.clip.selected');
    if (!selectedClip) return;
    
    const clipId = selectedClip.dataset.clipId;
    
    // Find clip data in project data
    projectData.timeline.tracks.forEach(track => {
        if (!track.clips) return;
        
        const clipIndex = track.clips.findIndex(c => c.id === clipId);
        if (clipIndex !== -1) {
            const clip = track.clips[clipIndex];
            
            // Remove the effect
            if (clip.effects) {
                const effectIndex = clip.effects.findIndex(e => e.id === effectId);
                if (effectIndex !== -1) {
                    clip.effects.splice(effectIndex, 1);
                    
                    // Update effects list
                    updateEffectsList(clip.effects);
                    
                    // Show notification
                    showNotification('info', 'Effect removed');
                }
            }
        }
    });
}

// Add event listeners to property inputs
function addPropertyChangeListeners(clipElement) {
    const startTimeInput = document.getElementById('clip-start-time');
    const durationInput = document.getElementById('clip-duration');
    const volumeInput = document.getElementById('clip-volume');
    const posXInput = document.getElementById('clip-position-x');
    const posYInput = document.getElementById('clip-position-y');
    const scaleInput = document.getElementById('clip-scale');
    const rotationInput = document.getElementById('clip-rotation');
    const effectSelect = document.getElementById('add-effect-select');
    
    // Start time input
    if (startTimeInput) {
        startTimeInput.addEventListener('change', function() {
            const newPosition = parseFloat(this.value);
            clipElement.style.left = `${newPosition * 10}px`;
            updateClipData(clipElement);
        });
    }
    
    // Duration input
    if (durationInput) {
        durationInput.addEventListener('change', function() {
            const newDuration = parseFloat(this.value);
            clipElement.style.width = `${newDuration * 10}px`;
            updateClipData(clipElement);
        });
    }
    
    // Volume input
    if (volumeInput) {
        volumeInput.addEventListener('input', function() {
            const clipId = clipElement.dataset.clipId;
            updateClipProperty(clipId, 'volume', parseFloat(this.value));
        });
    }
    
    // Position X input
    if (posXInput) {
        posXInput.addEventListener('change', function() {
            const clipId = clipElement.dataset.clipId;
            updateClipProperty(clipId, 'position_x', parseInt(this.value));
        });
    }
    
    // Position Y input
    if (posYInput) {
        posYInput.addEventListener('change', function() {
            const clipId = clipElement.dataset.clipId;
            updateClipProperty(clipId, 'position_y', parseInt(this.value));
        });
    }
    
    // Scale input
    if (scaleInput) {
        scaleInput.addEventListener('input', function() {
            const clipId = clipElement.dataset.clipId;
            updateClipProperty(clipId, 'scale', parseFloat(this.value));
        });
    }
    
    // Rotation input
    if (rotationInput) {
        rotationInput.addEventListener('input', function() {
            const clipId = clipElement.dataset.clipId;
            updateClipProperty(clipId, 'rotation', parseInt(this.value));
        });
    }
    
    // Effect select
    if (effectSelect) {
        effectSelect.addEventListener('change', function() {
            if (this.value) {
                addEffectToClip(clipElement.dataset.clipId, this.value);
                this.value = ''; // Reset select
            }
        });
    }
}

// Update a clip property in project data
function updateClipProperty(clipId, property, value) {
    projectData.timeline.tracks.forEach(track => {
        if (!track.clips) return;
        
        const clipIndex = track.clips.findIndex(c => c.id === clipId);
        if (clipIndex !== -1) {
            track.clips[clipIndex][property] = value;
        }
    });
}

// Add an effect to a clip
function addEffectToClip(clipId, effectType) {
    // Map of effect types to names
    const effectNames = {
        'fade': 'Fade',
        'blur': 'Blur',
        'color': 'Color Correction',
        'crop': 'Crop',
        'ai_enhance': 'AI Enhancement'
    };
    
    // Create a unique effect ID
    const effectId = `effect-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
    
    // Create effect data
    const effectData = {
        id: effectId,
        type: effectType,
        name: effectNames[effectType] || 'Effect',
        parameters: {}
    };
    
    // Add default parameters based on effect type
    if (effectType === 'fade') {
        effectData.parameters.duration = 1.0;
        effectData.parameters.type = 'in';
    } else if (effectType === 'blur') {
        effectData.parameters.amount = 5.0;
    } else if (effectType === 'color') {
        effectData.parameters.brightness = 0;
        effectData.parameters.contrast = 0;
        effectData.parameters.saturation = 0;
    }
    
    // Find clip in project data
    projectData.timeline.tracks.forEach(track => {
        if (!track.clips) return;
        
        const clipIndex = track.clips.findIndex(c => c.id === clipId);
        if (clipIndex !== -1) {
            if (!track.clips[clipIndex].effects) {
                track.clips[clipIndex].effects = [];
            }
            
            // Add effect to clip
            track.clips[clipIndex].effects.push(effectData);
            
            // Update effects list
            updateEffectsList(track.clips[clipIndex].effects);
            
            // Show notification
            showNotification('success', `Added ${effectData.name} effect`);
        }
    });
}

// Initialize preview player
function initPreviewPlayer() {
    console.log("Initializing preview player...");
    
    const playBtn = document.getElementById('play-btn');
    const prevFrameBtn = document.getElementById('prev-frame-btn');
    const nextFrameBtn = document.getElementById('next-frame-btn');
    const muteBtn = document.getElementById('mute-btn');
    const scrubber = document.querySelector('.timeline-scrubber');
    
    // Initialize preview player state
    window.playerState = {
        isPlaying: false,
        isMuted: false,
        currentTime: 0,
        duration: projectData.timeline.duration || 60
    };
    
    // Set up play button
    if (playBtn) {
        playBtn.addEventListener('click', function() {
            togglePlayback();
        });
    }
    
    // Set up previous frame button
    if (prevFrameBtn) {
        prevFrameBtn.addEventListener('click', function() {
            seekFrame(-1);
        });
    }
    
    // Set up next frame button
    if (nextFrameBtn) {
        nextFrameBtn.addEventListener('click', function() {
            seekFrame(1);
        });
    }
    
    // Set up mute button
    if (muteBtn) {
        muteBtn.addEventListener('click', function() {
            toggleMute();
        });
    }
    
    // Set up scrubber
    if (scrubber) {
        scrubber.addEventListener('click', function(e) {
            seekToPosition(e);
        });
    }
}

// Toggle playback (play/pause)
function togglePlayback() {
    const playBtn = document.getElementById('play-btn');
    const playIcon = playBtn?.querySelector('i');
    
    if (!playIcon) return;
    
    window.playerState.isPlaying = !window.playerState.isPlaying;
    
    if (window.playerState.isPlaying) {
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

// Start video playback
function startPlayback() {
    // Clear any existing interval
    if (window.playbackInterval) {
        clearInterval(window.playbackInterval);
    }
    
    // Get timeline and playhead elements
    const timelineTracks = document.getElementById('timeline-tracks');
    const playhead = document.getElementById('timeline-playhead');
    
    if (!timelineTracks || !playhead) return;
    
    // Get current playhead position
    let currentPos = parseInt(playhead.style.left) || 0;
    const timelineWidth = timelineTracks.offsetWidth;
    
    // Set up interval to move playhead
    window.playbackInterval = setInterval(() => {
        currentPos += 2; // Move by 2px per frame (adjust for desired speed)
        
        // Check if we've reached the end
        if (currentPos >= timelineWidth) {
            clearInterval(window.playbackInterval);
            togglePlayback(); // Auto-pause at the end
            currentPos = 0; // Reset to beginning
        }
        
        // Update playhead position
        playhead.style.left = `${currentPos}px`;
        
        // Update scrubber position
        updateScrubberPosition(currentPos / timelineWidth);
        
        // Update current time display
        const totalTime = window.playerState.duration;
        const currentTime = (currentPos / timelineWidth) * totalTime;
        document.getElementById('current-time').textContent = formatTime(currentTime);
        
        // Update player state
        window.playerState.currentTime = currentTime;
    }, 30); // ~30fps
}

// Pause video playback
function pausePlayback() {
    if (window.playbackInterval) {
        clearInterval(window.playbackInterval);
    }
}

// Seek to a specific frame (forward or backward)
function seekFrame(direction) {
    // Get playhead element
    const playhead = document.getElementById('timeline-playhead');
    const timelineTracks = document.getElementById('timeline-tracks');
    
    if (!playhead || !timelineTracks) return;
    
    // Get current position
    let currentPos = parseInt(playhead.style.left) || 0;
    
    // Calculate one frame worth of pixels (assuming 30fps)
    const totalTime = window.playerState.duration;
    const timelineWidth = timelineTracks.offsetWidth;
    const pixelsPerSecond = timelineWidth / totalTime;
    const pixelsPerFrame = pixelsPerSecond / 30;
    
    // Move by one frame in the specified direction
    currentPos += direction * pixelsPerFrame;
    
    // Ensure we stay within bounds
    currentPos = Math.max(0, Math.min(timelineWidth, currentPos));
    
    // Update playhead position
    playhead.style.left = `${currentPos}px`;
    
    // Update scrubber position
    updateScrubberPosition(currentPos / timelineWidth);
    
    // Update current time display
    const currentTime = (currentPos / timelineWidth) * totalTime;
    document.getElementById('current-time').textContent = formatTime(currentTime);
    
    // Update player state
    window.playerState.currentTime = currentTime;
}

// Toggle mute
function toggleMute() {
    const muteBtn = document.getElementById('mute-btn');
    const muteIcon = muteBtn?.querySelector('i');
    
    if (!muteIcon) return;
    
    window.playerState.isMuted = !window.playerState.isMuted;
    
    if (window.playerState.isMuted) {
        // Mute
        muteIcon.classList.remove('bi-volume-up-fill');
        muteIcon.classList.add('bi-volume-mute-fill');
    } else {
        // Unmute
        muteIcon.classList.remove('bi-volume-mute-fill');
        muteIcon.classList.add('bi-volume-up-fill');
    }
}

// Seek to a specific position by clicking on the scrubber
function seekToPosition(e) {
    const scrubber = document.querySelector('.timeline-scrubber');
    
    if (!scrubber) return;
    
    const rect = scrubber.getBoundingClientRect();
    const clickPos = (e.clientX - rect.left) / rect.width;
    
    // Update scrubber position
    updateScrubberPosition(clickPos);
    
    // Update playhead position
    const playhead = document.getElementById('timeline-playhead');
    const timelineTracks = document.getElementById('timeline-tracks');
    
    if (playhead && timelineTracks) {
        const timelineWidth = timelineTracks.offsetWidth;
        const newPos = clickPos * timelineWidth;
        playhead.style.left = `${newPos}px`;
    }
    
    // Update current time display
    const totalTime = window.playerState.duration;
    const currentTime = clickPos * totalTime;
    document.getElementById('current-time').textContent = formatTime(currentTime);
    
    // Update player state
    window.playerState.currentTime = currentTime;
}

// Update the scrubber position
function updateScrubberPosition(position) {
    const progress = document.querySelector('.timeline-scrubber .progress');
    const handle = document.querySelector('.timeline-scrubber .handle');
    
    if (!progress || !handle) return;
    
    // Ensure position is between 0 and 1
    position = Math.max(0, Math.min(1, position));
    
    // Update progress bar width
    progress.style.width = `${position * 100}%`;
    
    // Update handle position
    handle.style.left = `${position * 100}%`;
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
    
    // Make media items draggable
    const mediaItems = document.querySelectorAll('.media-item');
    
    mediaItems.forEach(item => {
        item.setAttribute('draggable', 'true');
        
        item.addEventListener('dragstart', function(e) {
            e.dataTransfer.setData('text/plain', item.dataset.assetId);
            e.dataTransfer.effectAllowed = 'copy';
        });
        
        // Add click handler to select media item
        item.addEventListener('click', function() {
            // Deselect all media items
            document.querySelectorAll('.media-item').forEach(mi => {
                mi.classList.remove('selected');
            });
            
            // Select this item
            item.classList.add('selected');
        });
    });
}

// Show media upload dialog
function showMediaUploadDialog() {
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
                            <label for="mediaName" class="form-label">Name</label>
                            <input type="text" class="form-control bg-dark text-light" id="mediaName" name="name" placeholder="Enter media name">
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
    
    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Create and show modal
    const modal = new bootstrap.Modal(document.getElementById('uploadMediaModal'));
    modal.show();
    
    // Set up file input to auto-fill name
    const fileInput = document.getElementById('mediaFile');
    const nameInput = document.getElementById('mediaName');
    
    if (fileInput && nameInput) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                // Get filename without extension
                const filename = this.files[0].name.split('.').slice(0, -1).join('.');
                nameInput.value = filename;
                
                // Auto-detect media type
                const mediaType = document.getElementById('mediaType');
                const fileType = this.files[0].type;
                
                if (fileType.startsWith('video/')) {
                    mediaType.value = 'video';
                } else if (fileType.startsWith('audio/')) {
                    mediaType.value = 'audio';
                } else if (fileType.startsWith('image/')) {
                    mediaType.value = 'image';
                }
            }
        });
    }
    
    // Handle upload button click
    const uploadButton = document.getElementById('uploadMediaBtn');
    
    if (uploadButton) {
        uploadButton.addEventListener('click', function() {
            const form = document.getElementById('uploadMediaForm');
            
            if (!form) return;
            
            const formData = new FormData(form);
            
            // Validate form
            if (!formData.get('file') || !formData.get('file').size) {
                showNotification('error', 'Please select a file to upload');
                return;
            }
            
            // Show progress bar
            const progressBar = document.querySelector('#uploadProgress .progress-bar');
            const progressContainer = document.getElementById('uploadProgress');
            
            if (progressContainer) {
                progressContainer.classList.remove('d-none');
            }
            
            // Upload file with XHR to show progress
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/assets/upload', true);
            
            xhr.upload.onprogress = function(e) {
                if (e.lengthComputable && progressBar) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    progressBar.style.width = percentComplete + '%';
                }
            };
            
            xhr.onload = function() {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        
                        if (response.success) {
                            // Add the new asset to project data
                            projectData.assets.push(response.asset);
                            
                            // Close modal
                            modal.hide();
                            
                            // Refresh media library
                            refreshMediaLibrary();
                            
                            // Show success notification
                            showNotification('success', 'Media uploaded successfully');
                        } else {
                            showNotification('error', response.error || 'Error uploading media');
                        }
                    } catch (e) {
                        showNotification('error', 'Error parsing server response');
                    }
                } else {
                    showNotification('error', 'Server error: ' + xhr.status);
                }
            };
            
            xhr.onerror = function() {
                showNotification('error', 'Network error during upload');
            };
            
            xhr.send(formData);
        });
    }
    
    // Clean up when modal is hidden
    const modalElement = document.getElementById('uploadMediaModal');
    
    if (modalElement) {
        modalElement.addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }
}

// Refresh the media library display
function refreshMediaLibrary() {
    const container = document.querySelector('.media-items-container');
    
    if (!container) return;
    
    if (projectData.assets && projectData.assets.length > 0) {
        // Clear the "no media" message if it exists
        container.innerHTML = '';
        
        // Add media items
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
            
            const mediaItem = document.createElement('div');
            mediaItem.className = 'media-item';
            mediaItem.draggable = true;
            mediaItem.dataset.assetId = asset.id;
            
            mediaItem.innerHTML = `
                <div class="media-item-thumbnail">
                    <i class="${icon}" style="color: ${color};"></i>
                </div>
                <div class="media-item-info">
                    <div class="fw-bold">${asset.name}
                        ${index === 0 ? '<span class="ai-badge"><i class="bi bi-stars"></i>AI</span>' : ''}
                    </div>
                    <small style="color: #a0a0c2;">${asset.duration || '--'}s</small>
                </div>
            `;
            
            container.appendChild(mediaItem);
            
            // Add drag event listeners
            mediaItem.addEventListener('dragstart', function(e) {
                e.dataTransfer.setData('text/plain', asset.id);
                e.dataTransfer.effectAllowed = 'copy';
            });
            
            // Add click event listener
            mediaItem.addEventListener('click', function() {
                // Deselect all media items
                document.querySelectorAll('.media-item').forEach(item => {
                    item.classList.remove('selected');
                });
                
                // Select this item
                this.classList.add('selected');
            });
        });
    } else {
        // Show "no media" message
        container.innerHTML = `
        <div class="text-center py-4">
            <i class="bi bi-upload display-6" style="color: #4a6cf7;"></i>
            <p class="mt-2" style="color: #a0a0c2;">No media files</p>
            <button class="btn btn-sm mt-2" style="background: linear-gradient(135deg, #4a6cf7, #7239ea); color: white;" id="upload-first-media-btn">Upload Media</button>
        </div>
        `;
        
        // Add event listener to new upload button
        const uploadFirstBtn = document.getElementById('upload-first-media-btn');
        
        if (uploadFirstBtn) {
            uploadFirstBtn.addEventListener('click', function() {
                showMediaUploadDialog();
            });
        }
    }
}

// Initialize properties panel
function initPropertiesPanel() {
    console.log("Initializing properties panel...");
    
    // Set up panel section toggling
    const sectionHeaders = document.querySelectorAll('.panel-section-header');
    
    sectionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            const icon = this.querySelector('i');
            
            if (content.style.display === 'none') {
                content.style.display = 'block';
                if (icon) {
                    icon.classList.remove('bi-chevron-right');
                    icon.classList.add('bi-chevron-down');
                }
            } else {
                content.style.display = 'none';
                if (icon) {
                    icon.classList.remove('bi-chevron-down');
                    icon.classList.add('bi-chevron-right');
                }
            }
        });
    });
    
    // Show "no selection" message initially
    document.getElementById('no-selection').style.display = 'block';
    document.getElementById('clip-properties').style.display = 'none';
}

// Add event listeners for editor actions
function addEventListeners() {
    console.log("Adding event listeners...");
    
    // Save button
    const saveBtn = document.getElementById('save-btn');
    
    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
            saveProject();
        });
    }
    
    // Export button
    const exportBtn = document.getElementById('export-btn');
    
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            showExportDialog();
        });
    }
    
    // AI Assist button
    const aiAssistBtn = document.getElementById('ai-assist-btn');
    
    if (aiAssistBtn) {
        aiAssistBtn.addEventListener('click', function() {
            showAIAssistDialog();
        });
    }
    
    // Split clip button
    const splitClipBtn = document.getElementById('split-clip-btn');
    
    if (splitClipBtn) {
        splitClipBtn.addEventListener('click', function() {
            splitSelectedClip();
        });
    }
    
    // Delete clip button
    const deleteClipBtn = document.getElementById('delete-clip-btn');
    
    if (deleteClipBtn) {
        deleteClipBtn.addEventListener('click', function() {
            deleteSelectedClip();
        });
    }
    
    // Add track button
    const addTrackBtn = document.getElementById('add-track-btn');
    
    if (addTrackBtn) {
        addTrackBtn.addEventListener('click', function() {
            addNewTrack();
        });
    }
    
    // Zoom buttons
    const zoomInBtn = document.getElementById('zoom-in-btn');
    const zoomOutBtn = document.getElementById('zoom-out-btn');
    
    if (zoomInBtn) {
        zoomInBtn.addEventListener('click', function() {
            changeZoom(0.1);
        });
    }
    
    if (zoomOutBtn) {
        zoomOutBtn.addEventListener('click', function() {
            changeZoom(-0.1);
        });
    }
}

// Save the project
function saveProject() {
    console.log("Saving project...");
    
    // Show saving notification
    showNotification('info', 'Saving project...');
    
    // Make AJAX request to save project
    fetch(`/api/projects/${projectData.id}/save`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(projectData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Server error: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Show success notification
            showNotification('success', 'Project saved successfully');
        } else {
            // Show error notification
            showNotification('error', data.error || 'Error saving project');
        }
    })
    .catch(error => {
        console.error('Error saving project:', error);
        showNotification('error', 'Error saving project: ' + error.message);
    });
}

// Show export dialog
function showExportDialog() {
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
                            <label for="exportName" class="form-label">Export Name</label>
                            <input type="text" class="form-control bg-dark text-light" id="exportName" name="name" value="${projectData.name} - Export">
                        </div>
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
                    <div class="export-cost mb-3">
                        <p>Required credits: <span id="export-credit-cost">10</span></p>
                    </div>
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
    
    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Create and show modal
    const modal = new bootstrap.Modal(document.getElementById('exportModal'));
    modal.show();
    
    // Update credit cost when quality changes
    const qualitySelect = document.getElementById('exportQuality');
    const creditCost = document.getElementById('export-credit-cost');
    
    if (qualitySelect && creditCost) {
        qualitySelect.addEventListener('change', function() {
            const costs = {
                'high': 10,
                'medium': 5,
                'low': 0
            };
            
            creditCost.textContent = costs[this.value] || 0;
        });
    }
    
    // Handle export button click
    const exportButton = document.getElementById('startExportBtn');
    
    if (exportButton) {
        exportButton.addEventListener('click', function() {
            const form = document.getElementById('exportForm');
            
            if (!form) return;
            
            const formData = new FormData(form);
            const exportData = {};
            
            // Convert FormData to object
            for (const [key, value] of formData.entries()) {
                exportData[key] = value;
            }
            
            // Show progress and status
            const progressContainer = document.getElementById('exportProgress');
            const statusContainer = document.getElementById('exportStatus');
            
            if (progressContainer) progressContainer.classList.remove('d-none');
            if (statusContainer) statusContainer.classList.remove('d-none');
            
            // Disable export button
            exportButton.disabled = true;
            
            // Send export request
            fetch('/api/exports', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(exportData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Server error: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Begin polling for export status
                    const exportId = data.export.id;
                    pollExportStatus(exportId);
                } else {
                    showExportError(data.error || 'Export creation failed');
                }
            })
            .catch(error => {
                console.error('Error creating export:', error);
                showExportError('Error: ' + error.message);
            });
        });
    }
    
    // Clean up when modal is hidden
    const modalElement = document.getElementById('exportModal');
    
    if (modalElement) {
        modalElement.addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }
}

// Poll for export status
function pollExportStatus(exportId) {
    const statusText = document.getElementById('exportStatusText');
    const progressBar = document.querySelector('#exportProgress .progress-bar');
    
    if (!statusText || !progressBar) return;
    
    // Set up polling function
    const checkExportStatus = () => {
        fetch(`/api/exports/${exportId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            if (data.export) {
                const export_data = data.export;
                const progress = export_data.progress || 0;
                
                // Update progress bar
                progressBar.style.width = `${progress}%`;
                
                // Update status text
                statusText.textContent = `${export_data.status || 'Processing'}: ${progress}%`;
                
                // Check if export is complete
                if (export_data.status === 'completed') {
                    // Show completed message with download link
                    document.getElementById('exportStatus').innerHTML = `
                    <div class="alert alert-success">
                        <p class="mb-2"><strong>Export completed!</strong></p>
                        <a href="${export_data.download_url || `/api/exports/${exportId}/download`}" 
                           class="btn btn-primary" download>
                            <i class="bi bi-download"></i> Download
                        </a>
                    </div>
                    `;
                    
                    // Enable export button
                    document.getElementById('startExportBtn').disabled = false;
                    
                    // Show notification
                    showNotification('success', 'Export completed successfully');
                    
                    return; // Stop polling
                }
                
                // Check if export failed
                if (export_data.status === 'failed') {
                    showExportError(export_data.error || 'Export failed');
                    return; // Stop polling
                }
                
                // Continue polling
                setTimeout(checkExportStatus, 2000);
            } else {
                showExportError('Invalid response from server');
            }
        })
        .catch(error => {
            console.error('Error checking export status:', error);
            statusText.textContent = 'Error checking status, retrying...';
            
            // Continue polling with longer delay
            setTimeout(checkExportStatus, 5000);
        });
    };
    
    // Start polling
    checkExportStatus();
}

// Show export error
function showExportError(message) {
    const statusContainer = document.getElementById('exportStatus');
    
    if (statusContainer) {
        statusContainer.innerHTML = `
        <div class="alert alert-danger">
            <p><i class="bi bi-exclamation-triangle"></i> ${message}</p>
        </div>
        `;
    }
    
    // Enable export button
    const exportButton = document.getElementById('startExportBtn');
    if (exportButton) exportButton.disabled = false;
    
    // Show notification
    showNotification('error', 'Export failed: ' + message);
}

// Show AI assist dialog
function showAIAssistDialog() {
    const modalHTML = `
    <div class="modal fade" id="aiAssistModal" tabindex="-1" aria-labelledby="aiAssistModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content bg-dark text-light">
                <div class="modal-header" style="background: linear-gradient(90deg, #9400D3, #4B0082); color: white;">
                    <h5 class="modal-title" id="aiAssistModalLabel"><i class="bi bi-stars me-2"></i>AI Video Assistant</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-4">
                        <label for="aiPrompt" class="form-label">What would you like to do?</label>
                        <div class="input-group mb-3">
                            <input type="text" class="form-control bg-dark text-light" id="aiPrompt" 
                                placeholder="e.g., Create an intro sequence, Generate background music...">
                            <button class="btn btn-primary" type="button" id="aiSubmitPrompt">
                                <i class="bi bi-lightning"></i> Generate
                            </button>
                        </div>
                        <div class="text-muted small">Cost: 5 credits per generation</div>
                    </div>
                    
                    <div class="row mb-4">
                        <div class="col-12">
                            <h6 class="border-bottom pb-2 mb-3">Quick Actions</h6>
                        </div>
                        <div class="col-md-4 mb-3">
                            <div class="ai-action-card p-3 bg-dark border border-secondary rounded text-center">
                                <i class="bi bi-music-note-beamed fs-3 mb-2" style="color: #4a6cf7;"></i>
                                <h6>Generate Music</h6>
                                <p class="small text-muted mb-2">Create custom background music</p>
                                <button class="btn btn-sm btn-outline-light w-100">Select</button>
                            </div>
                        </div>
                        <div class="col-md-4 mb-3">
                            <div class="ai-action-card p-3 bg-dark border border-secondary rounded text-center">
                                <i class="bi bi-camera-video fs-3 mb-2" style="color: #50cd89;"></i>
                                <h6>Create B-roll</h6>
                                <p class="small text-muted mb-2">Generate supplementary footage</p>
                                <button class="btn btn-sm btn-outline-light w-100">Select</button>
                            </div>
                        </div>
                        <div class="col-md-4 mb-3">
                            <div class="ai-action-card p-3 bg-dark border border-secondary rounded text-center">
                                <i class="bi bi-magic fs-3 mb-2" style="color: #ffc700;"></i>
                                <h6>Enhance Video</h6>
                                <p class="small text-muted mb-2">Improve video quality</p>
                                <button class="btn btn-sm btn-outline-light w-100">Select</button>
                            </div>
                        </div>
                    </div>
                    
                    <div id="aiResultContainer" class="d-none">
                        <h6 class="border-bottom pb-2 mb-3">Results</h6>
                        <div id="aiResultContent" class="p-3 bg-dark border border-secondary rounded">
                            <!-- AI results will appear here -->
                        </div>
                        <div class="d-flex justify-content-end mt-3">
                            <button class="btn btn-success" id="aiApplyChanges">
                                <i class="bi bi-check2"></i> Apply to Project
                            </button>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Create and show modal
    const modal = new bootstrap.Modal(document.getElementById('aiAssistModal'));
    modal.show();
    
    // Handle AI prompt submission
    const submitButton = document.getElementById('aiSubmitPrompt');
    
    if (submitButton) {
        submitButton.addEventListener('click', function() {
            const prompt = document.getElementById('aiPrompt').value;
            
            if (!prompt) {
                showNotification('warning', 'Please enter a prompt');
                return;
            }
            
            // Disable submit button and show loading state
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
            
            // Show the result container with a loading message
            const resultContainer = document.getElementById('aiResultContainer');
            const resultContent = document.getElementById('aiResultContent');
            
            if (resultContainer && resultContent) {
                resultContainer.classList.remove('d-none');
                resultContent.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary mb-3" role="status"></div>
                    <p>Processing your request...</p>
                    <p class="text-muted small">This may take up to 30 seconds</p>
                </div>
                `;
                
                // Simulate AI processing (replace with real API call)
                setTimeout(() => {
                    // Show AI response
                    resultContent.innerHTML = `
                    <div>
                        <div class="mb-3">
                            <h6 class="mb-2">Generated Response</h6>
                            <p>I've created a response for "${prompt}".</p>
                            <p>This feature is currently in development. In the future, you'll be able to generate AI content directly in the editor.</p>
                        </div>
                        <div class="alert alert-info">
                            <i class="bi bi-info-circle me-2"></i> AI Generation is coming soon. This is a preview of the interface.
                        </div>
                    </div>
                    `;
                    
                    // Re-enable submit button
                    submitButton.disabled = false;
                    submitButton.innerHTML = '<i class="bi bi-lightning"></i> Generate';
                    
                    // Show notification
                    showNotification('info', 'AI generation feature coming soon');
                }, 2000);
            }
        });
    }
    
    // Clean up when modal is hidden
    const modalElement = document.getElementById('aiAssistModal');
    
    if (modalElement) {
        modalElement.addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }
}

// Split the selected clip
function splitSelectedClip() {
    const selectedClip = document.querySelector('.clip.selected');
    
    if (!selectedClip) {
        showNotification('warning', 'Please select a clip to split');
        return;
    }
    
    // Get playhead position
    const playhead = document.getElementById('timeline-playhead');
    
    if (!playhead) {
        showNotification('error', 'Playhead not found');
        return;
    }
    
    const playheadPos = parseInt(playhead.style.left) || 0;
    
    // Get clip position and width
    const clipLeft = parseInt(selectedClip.style.left) || 0;
    const clipWidth = parseInt(selectedClip.style.width) || 100;
    const clipRight = clipLeft + clipWidth;
    
    // Check if playhead is within clip
    if (playheadPos <= clipLeft || playheadPos >= clipRight) {
        showNotification('warning', 'Playhead must be positioned within the clip to split');
        return;
    }
    
    // Calculate split position relative to clip
    const splitPos = playheadPos - clipLeft;
    
    // Resize current clip
    selectedClip.style.width = `${splitPos}px`;
    
    // Create new clip (second part)
    const newClip = selectedClip.cloneNode(true);
    const newClipId = `clip-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
    
    newClip.dataset.clipId = newClipId;
    newClip.style.left = `${playheadPos}px`;
    newClip.style.width = `${clipRight - playheadPos}px`;
    
    // Add new clip to track
    selectedClip.parentNode.appendChild(newClip);
    
    // Initialize dragging for new clip
    initClipDragging(newClip);
    
    // Update clip data in project
    updateSplitClipData(selectedClip, newClip);
    
    // Show notification
    showNotification('success', 'Clip split successfully');
}

// Update project data after splitting a clip
function updateSplitClipData(originalClip, newClip) {
    const originalClipId = originalClip.dataset.clipId;
    const newClipId = newClip.dataset.clipId;
    const assetId = originalClip.dataset.assetId;
    
    // Find the original clip in project data
    projectData.timeline.tracks.forEach(track => {
        if (!track.clips) return;
        
        const clipIndex = track.clips.findIndex(c => c.id === originalClipId);
        
        if (clipIndex !== -1) {
            const originalClipData = track.clips[clipIndex];
            
            // Update original clip duration
            const newDuration = parseInt(originalClip.style.width) / 10;
            originalClipData.duration = newDuration;
            
            // Create new clip data
            const newClipData = {
                id: newClipId,
                asset_id: assetId,
                position: parseInt(newClip.style.left) / 10,
                duration: parseInt(newClip.style.width) / 10,
                volume: originalClipData.volume || 1.0,
                speed: originalClipData.speed || 1.0,
                effects: [...(originalClipData.effects || [])]
            };
            
            // Add new clip to track
            track.clips.push(newClipData);
        }
    });
}

// Delete the selected clip
function deleteSelectedClip() {
    const selectedClip = document.querySelector('.clip.selected');
    
    if (!selectedClip) {
        showNotification('warning', 'Please select a clip to delete');
        return;
    }
    
    // Get clip ID
    const clipId = selectedClip.dataset.clipId;
    
    // Remove clip element from DOM
    selectedClip.remove();
    
    // Remove clip from project data
    let deleted = false;
    
    projectData.timeline.tracks.forEach(track => {
        if (!track.clips) return;
        
        const clipIndex = track.clips.findIndex(c => c.id === clipId);
        
        if (clipIndex !== -1) {
            track.clips.splice(clipIndex, 1);
            deleted = true;
        }
    });
    
    // Hide properties panel and show no selection
    document.getElementById('no-selection').style.display = 'block';
    document.getElementById('clip-properties').style.display = 'none';
    
    // Show notification
    if (deleted) {
        showNotification('success', 'Clip deleted');
    }
}

// Add a new track to the timeline
function addNewTrack() {
    // Find the tracks container
    const tracksContainer = document.getElementById('timeline-tracks');
    
    if (!tracksContainer) {
        showNotification('error', 'Timeline tracks container not found');
        return;
    }
    
    // Create a new track ID and name
    const trackCount = projectData.timeline.tracks.length + 1;
    const trackId = `${trackCount}`;
    const trackName = `Track ${trackCount}`;
    
    // Create track element
    const trackElement = document.createElement('div');
    trackElement.className = 'track';
    
    // Determine track type (alternate between video and audio)
    const trackType = trackCount % 2 === 0 ? 'audio' : 'video';
    
    trackElement.innerHTML = `
    <div class="track-label">${trackName}</div>
    <div class="track-content" id="${trackType}-track-${trackId}" data-track-type="${trackType}" data-track-id="${trackId}"></div>
    `;
    
    // Add track to container
    tracksContainer.appendChild(trackElement);
    
    // Add track to project data
    projectData.timeline.tracks.push({
        id: trackId,
        name: trackName,
        type: trackType,
        clips: []
    });
    
    // Initialize clip drag and drop for the new track
    const trackContent = trackElement.querySelector('.track-content');
    
    trackContent.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
        trackContent.classList.add('drag-over');
    });
    
    trackContent.addEventListener('dragleave', function() {
        trackContent.classList.remove('drag-over');
    });
    
    trackContent.addEventListener('drop', function(e) {
        e.preventDefault();
        trackContent.classList.remove('drag-over');
        
        // Get the asset ID from the dragged element
        const assetId = e.dataTransfer.getData('text/plain');
        
        // Calculate drop position relative to the track
        const rect = trackContent.getBoundingClientRect();
        const dropPos = e.clientX - rect.left;
        
        // Add clip to timeline
        addClipToTimeline(trackContent, assetId, dropPos);
    });
    
    // Show notification
    showNotification('success', `Added new ${trackType} track`);
}

// Change the timeline zoom level
function changeZoom(change) {
    // Get current zoom level
    const zoomLevel = parseFloat(projectData.timeline.scale) || 1.0;
    
    // Calculate new zoom level
    let newZoom = zoomLevel + change;
    
    // Limit zoom range
    newZoom = Math.max(0.1, Math.min(2.0, newZoom));
    
    // Update project data
    projectData.timeline.scale = newZoom;
    
    // Update zoom level display
    const zoomDisplay = document.getElementById('zoom-level');
    
    if (zoomDisplay) {
        zoomDisplay.textContent = `${Math.round(newZoom * 100)}%`;
    }
    
    // Apply zoom to timeline
    applyTimelineZoom(newZoom);
}

// Apply zoom level to timeline
function applyTimelineZoom(scale) {
    const trackContents = document.querySelectorAll('.track-content');
    
    trackContents.forEach(track => {
        // Scale the track content
        track.style.transform = `scaleX(${scale})`;
        track.style.transformOrigin = 'left';
        
        // Adjust clip positions and widths
        const clips = track.querySelectorAll('.clip');
        
        clips.forEach(clip => {
            // No need to adjust clip styles as they inherit the transform
        });
    });
    
    // Regenerate time markers to reflect the new scale
    generateTimeMarkers();
}

// Show a notification
function showNotification(type, message) {
    // Create notification container if it doesn't exist
    let container = document.getElementById('notification-container');
    
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        document.body.appendChild(container);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // Add icon based on type
    let icon = 'bi-info-circle';
    
    if (type === 'success') {
        icon = 'bi-check-circle';
    } else if (type === 'error') {
        icon = 'bi-exclamation-circle';
    } else if (type === 'warning') {
        icon = 'bi-exclamation-triangle';
    }
    
    notification.innerHTML = `
    <i class="bi ${icon}"></i>
    <span>${message}</span>
    `;
    
    // Add notification to container
    container.appendChild(notification);
    
    // Remove notification after 5 seconds
    setTimeout(() => {
        notification.classList.add('fade-out');
        
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 5000);
}

// Format time (seconds to MM:SS:FF format)
function formatTime(seconds) {
    const min = Math.floor(seconds / 60).toString().padStart(2, '0');
    const sec = Math.floor(seconds % 60).toString().padStart(2, '0');
    const frames = Math.floor((seconds * 30) % 30).toString().padStart(2, '0');
    
    return `${min}:${sec}:${frames}`;
}