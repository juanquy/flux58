/**
 * Enhanced Timeline Fixes for OpenShot Editor
 * Completely rebuilds timeline if it's not visible
 * No longer relies on fix button - automatic operation
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Enhanced timeline fix script loaded');
    
    // Apply fixes immediately
    setTimeout(function() {
        console.log('Applying immediate timeline visibility fix');
        rebuildTimeline();
    }, 300);
    
    // Set up a more aggressive periodic check for timeline visibility
    setInterval(checkTimelineVisibility, 500);
    
    // Add media library event listener to ensure timeline doesn't disappear
    const mediaThumbnails = document.querySelectorAll('.media-thumbnail');
    mediaThumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            // Ensure timeline is visible after media interaction
            setTimeout(function() {
                rebuildTimeline();
            }, 300);
        });
    });
});

/**
 * Completely rebuild the timeline if it's not visible
 */
function rebuildTimeline() {
    // Get timeline panel
    const timelinePanel = document.querySelector('.timeline-panel');
    if (!timelinePanel) {
        console.error('Critical error: Timeline panel not found in DOM');
        createTimeline();
        return;
    }
    
    // Force display
    timelinePanel.style.display = 'flex';
    timelinePanel.style.visibility = 'visible';
    timelinePanel.style.opacity = '1';
    timelinePanel.style.height = '220px';
    timelinePanel.style.minHeight = '150px';
    timelinePanel.style.zIndex = '10';
    
    // Check if timeline is actually visible
    const timelinePanelRect = timelinePanel.getBoundingClientRect();
    if (timelinePanelRect.height < 20) {
        console.warn('Timeline has zero/small height, rebuilding it');
        createTimeline();
        return;
    }
    
    // Force all timeline elements to be visible
    const timelineElements = {
        '.timeline-header': 'block',
        '.timeline-time-markers': 'block',
        '.timeline-tracks': 'block',
        '.track': 'flex',
        '.track-label': 'flex',
        '.track-content': 'block',
        '.clip': 'block',
        '.timeline-playhead': 'block'
    };
    
    Object.entries(timelineElements).forEach(([selector, displayValue]) => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            el.style.display = displayValue;
            el.style.visibility = 'visible';
            el.style.opacity = '1';
        });
    });
    
    // Rebuild tracks if needed
    const tracks = document.querySelectorAll('.track');
    if (tracks.length === 0) {
        const tracksContainer = document.querySelector('.timeline-tracks');
        if (tracksContainer) {
            createDefaultTracks(tracksContainer);
        }
    }
    
    // Re-attach event handlers
    attachTimelineEvents();
    console.log('Timeline visibility fix complete');
}

/**
 * Create the entire timeline structure if it's missing
 */
function createTimeline() {
    console.log('Creating timeline from scratch');
    
    const previewPanel = document.querySelector('.preview-panel');
    if (!previewPanel) {
        console.error('Preview panel not found, cannot create timeline');
        return;
    }
    
    // Check if timeline exists but is not visible
    let timelinePanel = document.querySelector('.timeline-panel');
    if (timelinePanel) {
        // Remove it so we can rebuild
        timelinePanel.remove();
    }
    
    // Create timeline panel
    timelinePanel = document.createElement('div');
    timelinePanel.className = 'timeline-panel';
    timelinePanel.style.display = 'flex';
    timelinePanel.style.flexDirection = 'column';
    timelinePanel.style.height = '220px';
    timelinePanel.style.minHeight = '150px';
    timelinePanel.style.backgroundColor = '#232334';
    timelinePanel.style.borderTop = '1px solid #353545';
    
    // Create timeline header
    const timelineHeader = document.createElement('div');
    timelineHeader.className = 'timeline-header';
    timelineHeader.innerHTML = `
        <div class="tools">
            <button class="btn btn-sm btn-outline-light" id="split-clip-btn" title="Split Clip at Playhead">
                <i class="bi bi-scissors"></i>
            </button>
            <button class="btn btn-sm btn-outline-light" id="delete-clip-btn" title="Delete Selected Clip">
                <i class="bi bi-trash"></i>
            </button>
            <button class="btn btn-sm btn-outline-light" id="add-track-btn" title="Add Track">
                <i class="bi bi-plus-lg"></i>
            </button>
            <button class="btn btn-sm btn-outline-light" id="delete-track-btn" title="Delete Track">
                <i class="bi bi-dash-lg"></i>
            </button>
            <div class="btn-group">
                <button class="btn btn-sm btn-outline-light" id="undo-btn" title="Undo">
                    <i class="bi bi-arrow-counterclockwise"></i>
                </button>
                <button class="btn btn-sm btn-outline-light" id="redo-btn" title="Redo">
                    <i class="bi bi-arrow-clockwise"></i>
                </button>
            </div>
            <button class="btn btn-sm btn-outline-light" id="snap-to-grid-btn" title="Snap to Grid">
                <i class="bi bi-grid"></i>
            </button>
        </div>
        <div class="zoom">
            <button class="btn btn-sm btn-outline-light" title="Zoom Out">
                <i class="bi bi-zoom-out"></i>
            </button>
            <span>100%</span>
            <button class="btn btn-sm btn-outline-light" title="Zoom In">
                <i class="bi bi-zoom-in"></i>
            </button>
        </div>
    `;
    
    // Create time markers
    const timeMarkers = document.createElement('div');
    timeMarkers.className = 'timeline-time-markers';
    timeMarkers.innerHTML = `
        <div class="time-marker" style="left: 0px;">00:00</div>
        <div class="time-marker" style="left: 100px;">00:10</div>
        <div class="time-marker" style="left: 200px;">00:20</div>
        <div class="time-marker" style="left: 300px;">00:30</div>
        <div class="time-marker" style="left: 400px;">00:40</div>
        <div class="time-marker" style="left: 500px;">00:50</div>
        <div class="time-marker" style="left: 600px;">01:00</div>
    `;
    
    // Create tracks container
    const tracksContainer = document.createElement('div');
    tracksContainer.className = 'timeline-tracks';
    
    // Add playhead
    const playhead = document.createElement('div');
    playhead.className = 'timeline-playhead';
    tracksContainer.appendChild(playhead);
    
    // Create default tracks
    createDefaultTracks(tracksContainer);
    
    // Add all elements to timeline
    timelinePanel.appendChild(timelineHeader);
    timelinePanel.appendChild(timeMarkers);
    timelinePanel.appendChild(tracksContainer);
    
    // Add timeline to preview panel
    previewPanel.appendChild(timelinePanel);
    
    // Attach event handlers
    attachTimelineEvents();
    
    console.log('Timeline created successfully');
}

/**
 * Create default tracks for the timeline
 */
function createDefaultTracks(container) {
    const trackData = [
        { label: 'Video 1', id: 'video-track-1', type: 'video' },
        { label: 'Audio 1', id: 'audio-track-1', type: 'audio' },
        { label: 'Effects', id: 'effects-track', type: 'effect' },
        { label: 'AI Text', id: 'text-track', type: 'text' }
    ];
    
    trackData.forEach(track => {
        const trackElement = document.createElement('div');
        trackElement.className = 'track';
        trackElement.dataset.type = track.type;
        
        const trackLabel = document.createElement('div');
        trackLabel.className = 'track-label';
        trackLabel.textContent = track.label;
        
        const trackContent = document.createElement('div');
        trackContent.className = 'track-content';
        trackContent.id = track.id;
        
        trackElement.appendChild(trackLabel);
        trackElement.appendChild(trackContent);
        container.appendChild(trackElement);
    });
}

/**
 * Attach event handlers to timeline elements
 */
function attachTimelineEvents() {
    // Handle clip drag and drop
    const tracks = document.querySelectorAll('.track-content');
    tracks.forEach(track => {
        track.addEventListener('dragover', function(e) {
            e.preventDefault();
        });
        
        track.addEventListener('drop', function(e) {
            e.preventDefault();
            const assetId = e.dataTransfer.getData('asset-id');
            const assetType = e.dataTransfer.getData('asset-type');
            
            // Only allow drops on matching track types
            const trackType = this.closest('.track').dataset.type;
            if (
                (assetType === 'video' && trackType === 'video') ||
                (assetType === 'audio' && trackType === 'audio') ||
                (assetType === 'image' && (trackType === 'video' || trackType === 'effect'))
            ) {
                // Calculate position in track
                const rect = this.getBoundingClientRect();
                const position = e.clientX - rect.left;
                
                // Create clip at position
                createClip(this, assetId, position);
            }
        });
    });
    
    // Make media items draggable
    const mediaItems = document.querySelectorAll('.media-item');
    mediaItems.forEach(item => {
        item.addEventListener('dragstart', function(e) {
            e.dataTransfer.setData('asset-id', this.dataset.assetId);
            e.dataTransfer.setData('asset-type', this.dataset.assetType);
        });
    });
    
    // Handle split clip button
    const splitBtn = document.getElementById('split-clip-btn');
    if (splitBtn) {
        splitBtn.addEventListener('click', function() {
            const selectedClip = document.querySelector('.clip.selected');
            if (selectedClip) {
                const playhead = document.querySelector('.timeline-playhead');
                const playheadLeft = parseInt(playhead.style.left) || 110;
                const clipLeft = parseInt(selectedClip.style.left) || 0;
                const clipWidth = parseInt(selectedClip.style.width) || 100;
                
                if (playheadLeft > clipLeft && playheadLeft < clipLeft + clipWidth) {
                    // Can split - implementation would go here
                    console.log('Splitting clip at playhead position');
                    alert('Split clip functionality will be implemented in the next update.');
                }
            }
        });
    }
    
    // Add more event handlers as needed
}

/**
 * Create a clip element on a track
 */
function createClip(trackContent, assetId, position) {
    // Find the asset data
    let asset = null;
    if (window.projectData && window.projectData.assets) {
        asset = window.projectData.assets.find(a => a.id === assetId);
    }
    
    if (!asset) {
        console.warn('Asset not found for ID:', assetId);
        return;
    }
    
    // Round position to nearest 10px for grid snapping
    position = Math.round(position / 10) * 10;
    
    // Create clip element
    const clip = document.createElement('div');
    clip.className = 'clip';
    if (asset.type === 'audio') {
        clip.classList.add('audio');
    } else if (asset.type === 'effect') {
        clip.classList.add('effect');
    }
    
    // Set clip properties
    clip.textContent = asset.name;
    clip.dataset.assetId = assetId;
    clip.dataset.clipId = 'clip-' + Date.now();
    clip.style.left = position + 'px';
    clip.style.width = '100px'; // Default width
    
    // Add click handler
    clip.addEventListener('click', function(e) {
        // Select this clip
        document.querySelectorAll('.clip').forEach(c => {
            c.classList.remove('selected');
        });
        clip.classList.add('selected');
        
        // Update properties panel
        updatePropertiesPanel(asset);
    });
    
    // Add the clip to the track
    trackContent.appendChild(clip);
    
    console.log('Clip created:', asset.name);
}

/**
 * Update properties panel with selected clip info
 */
function updatePropertiesPanel(asset) {
    const noSelection = document.getElementById('no-selection');
    const clipProperties = document.getElementById('clip-properties');
    
    if (noSelection) noSelection.style.display = 'none';
    if (clipProperties) clipProperties.style.display = 'block';
    
    // More property updates would go here
}

/**
 * Check if timeline is visible and fix if not
 */
function checkTimelineVisibility() {
    const timelinePanel = document.querySelector('.timeline-panel');
    if (!timelinePanel) {
        console.warn('Timeline panel not found in periodic check');
        return;
    }
    
    const isVisible = 
        window.getComputedStyle(timelinePanel).display !== 'none' && 
        window.getComputedStyle(timelinePanel).visibility !== 'hidden' && 
        timelinePanel.getBoundingClientRect().height > 50;
    
    if (!isVisible) {
        console.warn('Timeline not visible, rebuilding');
        rebuildTimeline();
    }
}

// Add event listeners for media library interactions
document.addEventListener('DOMContentLoaded', function() {
    // Listen for media tab changes
    const mediaTabs = document.querySelectorAll('[data-bs-toggle="tab"]');
    mediaTabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function() {
            // Ensure timeline stays visible when switching media tabs
            setTimeout(rebuildTimeline, 100);
        });
    });
    
    // Listen for media uploads - this is critical for timeline persistence
    const uploadBtns = document.querySelectorAll('[id$="-media-btn"]');
    uploadBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Schedule multiple timeline rebuilds after upload interaction
            setTimeout(rebuildTimeline, 500);
            setTimeout(rebuildTimeline, 1500);
            setTimeout(rebuildTimeline, 3000);
        });
    });
    
    // Ensure timeline is rebuilt when media items are dragged
    document.addEventListener('dragstart', function() {
        // Timeline can disappear during drag operations
        setTimeout(rebuildTimeline, 100);
    });
    
    document.addEventListener('dragend', function() {
        // Rebuild timeline after drag completes
        setTimeout(rebuildTimeline, 100);
    });
});

// Make functions available globally
window.timelineFix = {
    rebuildTimeline,
    createTimeline,
    checkTimelineVisibility
};