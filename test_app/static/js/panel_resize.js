/**
 * OpenShot Video Editor - Panel Resize Functionality
 * Provides resizable panels for the editor interface
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize resizable panels
    initResizablePanels();
});

// Initialize resizable panels
function initResizablePanels() {
    console.log("Initializing resizable panels...");
    
    // Add resize handles to panels
    addResizeHandlesToPanels();
    
    // Initialize resize behaviors
    initPanelResizeBehaviors();
}

// Add resize handles to panels
function addResizeHandlesToPanels() {
    // Media panel (left panel)
    const mediaPanel = document.querySelector('.media-panel');
    if (mediaPanel) {
        const mediaPanelHandle = document.createElement('div');
        mediaPanelHandle.className = 'resize-handle resize-handle-horizontal media-panel-resize-handle';
        mediaPanelHandle.setAttribute('data-panel', 'media-panel');
        mediaPanelHandle.setAttribute('data-direction', 'horizontal');
        mediaPanel.appendChild(mediaPanelHandle);
    }
    
    // Properties panel (right panel)
    const propertiesPanel = document.querySelector('.properties-panel');
    if (propertiesPanel) {
        const propertiesPanelHandle = document.createElement('div');
        propertiesPanelHandle.className = 'resize-handle resize-handle-horizontal properties-panel-resize-handle';
        propertiesPanelHandle.setAttribute('data-panel', 'properties-panel');
        propertiesPanelHandle.setAttribute('data-direction', 'horizontal');
        propertiesPanel.appendChild(propertiesPanelHandle);
    }
    
    // Timeline panel (bottom panel)
    const timelinePanel = document.querySelector('.timeline-panel');
    if (timelinePanel) {
        const timelinePanelHandle = document.createElement('div');
        timelinePanelHandle.className = 'resize-handle resize-handle-vertical timeline-panel-resize-handle';
        timelinePanelHandle.setAttribute('data-panel', 'timeline-panel');
        timelinePanelHandle.setAttribute('data-direction', 'vertical');
        timelinePanel.appendChild(timelinePanelHandle);
    }
}

// Initialize panel resize behaviors
function initPanelResizeBehaviors() {
    const resizeHandles = document.querySelectorAll('.resize-handle');
    
    resizeHandles.forEach(handle => {
        handle.addEventListener('mousedown', startResize);
    });
}

// Start resize operation
function startResize(e) {
    e.preventDefault();
    
    const handle = e.target;
    const panel = document.querySelector(`.${handle.getAttribute('data-panel')}`);
    
    if (!panel) return;
    
    const direction = handle.getAttribute('data-direction');
    const isHorizontal = direction === 'horizontal';
    
    // Store initial sizes and mouse position
    const startX = e.clientX;
    const startY = e.clientY;
    const startWidth = panel.offsetWidth;
    const startHeight = panel.offsetHeight;
    
    // Add resizing class to body
    document.body.classList.add('resizing');
    
    // Add resizing class to panel
    panel.classList.add('resizing');
    
    // Add mouse move and mouse up event listeners
    document.addEventListener('mousemove', resize);
    document.addEventListener('mouseup', stopResize);
    
    // Resize function
    function resize(e) {
        if (isHorizontal) {
            // Handle horizontal resize
            const isLeftPanel = panel.classList.contains('media-panel');
            let newWidth = startWidth;
            
            if (isLeftPanel) {
                // Left panel (media panel)
                newWidth = startWidth + (e.clientX - startX);
            } else {
                // Right panel (properties panel)
                newWidth = startWidth - (e.clientX - startX);
            }
            
            // Apply min/max constraints
            newWidth = Math.max(200, Math.min(500, newWidth));
            
            // Apply new width
            panel.style.width = `${newWidth}px`;
        } else {
            // Handle vertical resize (timeline panel)
            const newHeight = startHeight - (e.clientY - startY);
            
            // Apply min/max constraints
            const maxHeight = window.innerHeight * 0.6; // Max 60% of viewport height
            const constrainedHeight = Math.max(150, Math.min(maxHeight, newHeight));
            
            // Apply new height
            panel.style.height = `${constrainedHeight}px`;
        }
    }
    
    // Stop resize function
    function stopResize() {
        document.body.classList.remove('resizing');
        panel.classList.remove('resizing');
        
        document.removeEventListener('mousemove', resize);
        document.removeEventListener('mouseup', stopResize);
        
        // Save panel sizes to localStorage for persistence
        savePanelSizes();
    }
}

// Save panel sizes to localStorage
function savePanelSizes() {
    const mediaPanel = document.querySelector('.media-panel');
    const propertiesPanel = document.querySelector('.properties-panel');
    const timelinePanel = document.querySelector('.timeline-panel');
    
    const panelSizes = {
        mediaPanel: mediaPanel ? mediaPanel.style.width : null,
        propertiesPanel: propertiesPanel ? propertiesPanel.style.width : null,
        timelinePanel: timelinePanel ? timelinePanel.style.height : null
    };
    
    localStorage.setItem('panelSizes', JSON.stringify(panelSizes));
}

// Load saved panel sizes
function loadPanelSizes() {
    const savedSizes = localStorage.getItem('panelSizes');
    
    if (savedSizes) {
        try {
            const sizes = JSON.parse(savedSizes);
            
            const mediaPanel = document.querySelector('.media-panel');
            const propertiesPanel = document.querySelector('.properties-panel');
            const timelinePanel = document.querySelector('.timeline-panel');
            
            if (mediaPanel && sizes.mediaPanel) {
                mediaPanel.style.width = sizes.mediaPanel;
            }
            
            if (propertiesPanel && sizes.propertiesPanel) {
                propertiesPanel.style.width = sizes.propertiesPanel;
            }
            
            if (timelinePanel && sizes.timelinePanel) {
                timelinePanel.style.height = sizes.timelinePanel;
            }
        } catch (e) {
            console.error('Error loading saved panel sizes:', e);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    loadPanelSizes();
});