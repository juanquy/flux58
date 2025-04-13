/**
 * OpenShot Video Editor - Workflow Modes
 * Handles different editing workflow modes
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize workflow mode functionality
    initWorkflowModes();
    
    // Simulate audio visualization for demo purposes
    simulateAudioVisualization();
});

// Initialize workflow mode switching
function initWorkflowModes() {
    console.log("Initializing workflow modes...");
    
    // Get all workflow mode menu items
    const workflowItems = document.querySelectorAll('[data-workflow]');
    console.log(`Found ${workflowItems.length} workflow items`);
    
    // Add click handlers to workflow items
    workflowItems.forEach(item => {
        // Remove any existing listeners first to avoid duplicates
        const clonedItem = item.cloneNode(true);
        item.parentNode.replaceChild(clonedItem, item);
        
        clonedItem.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get workflow mode
            const workflowMode = this.dataset.workflow;
            console.log(`Workflow item clicked: ${workflowMode}`);
            
            // Update menu state
            updateWorkflowMenu(workflowMode);
            
            // Switch to this workflow mode
            switchWorkflowMode(workflowMode);
        });
    });
    
    // Add click handlers to close panel buttons
    const closePanelButtons = document.querySelectorAll('.close-panel');
    closePanelButtons.forEach(button => {
        // Remove any existing listeners first to avoid duplicates
        const clonedButton = button.cloneNode(true);
        button.parentNode.replaceChild(clonedButton, button);
        
        clonedButton.addEventListener('click', function() {
            const panelId = this.dataset.panel;
            console.log(`Close panel button clicked: ${panelId}`);
            hideWorkflowPanel(panelId);
            
            // Reset workflow menu
            updateWorkflowMenu('standard');
            
            // Remove color preview when closing the panel
            if (panelId === 'colorCorrectionPanel') {
                removeColorModeMarkers();
                
                // Remove the preview panel class
                const previewPanel = document.querySelector('.preview-panel');
                if (previewPanel) {
                    previewPanel.classList.remove('color-correction-preview');
                }
            }
        });
    });
    
    // Initialize color correction panel functionality
    initColorCorrectionPanel();
    
    // Initialize audio panel functionality
    initAudioPanel();
    
    // Initialize effects panel functionality
    initEffectsPanel();
    
    // Initialize text panel functionality
    initTextPanel();
    
    // Initialize AI panel functionality
    initAIPanel();
    
    console.log("Workflow modes initialization complete");
}

// Update workflow menu state
function updateWorkflowMenu(activeMode) {
    // Update dropdown button text
    const dropdownButton = document.getElementById('workflowSelector');
    if (dropdownButton) {
        let buttonText = 'Edit Mode';
        let buttonIcon = 'bi-gear-wide-connected';
        
        // Set button text and icon based on mode
        if (activeMode === 'color') {
            buttonText = 'Color Correction';
            buttonIcon = 'bi-palette';
        } else if (activeMode === 'audio') {
            buttonText = 'Audio Mixing';
            buttonIcon = 'bi-music-note-beamed';
        } else if (activeMode === 'effects') {
            buttonText = 'Visual Effects';
            buttonIcon = 'bi-magic';
        } else if (activeMode === 'text') {
            buttonText = 'Text & Graphics';
            buttonIcon = 'bi-fonts';
        } else if (activeMode === 'ai') {
            buttonText = 'AI-Assisted Mode';
            buttonIcon = 'bi-stars';
        } else {
            buttonText = 'Standard Editing';
            buttonIcon = 'bi-film';
        }
        
        // Update button content
        dropdownButton.innerHTML = `<i class="bi ${buttonIcon}"></i> ${buttonText}`;
        
        // Force repaint to ensure UI updates
        dropdownButton.style.display = 'none';
        dropdownButton.offsetHeight; // Force reflow
        dropdownButton.style.display = '';
        
        console.log(`Updated workflow menu button to: ${buttonText}`);
    }
    
    // Update active state in menu
    const menuItems = document.querySelectorAll('[data-workflow]');
    menuItems.forEach(item => {
        if (item.dataset.workflow === activeMode) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    
    // Log the mode change for debugging
    console.log(`Workflow mode updated to: ${activeMode}`);
}

// Switch to a specific workflow mode
function switchWorkflowMode(mode) {
    console.log(`Switching to ${mode} mode`);
    
    // Reset any previous UI state first
    // Hide all panels
    hideAllWorkflowPanels();
    
    // Remove color mode markers if they exist
    removeColorModeMarkers();
    
    // Remove all workflow-specific UI classes from panels
    document.querySelectorAll('.preview-panel, .timeline-panel, .properties-panel').forEach(panel => {
        panel.className = panel.className.split(' ').filter(c => !c.includes('-preview') && !c.includes('-timeline') && !c.includes('-properties')).join(' ');
    });
    
    // Remove all existing workflow mode classes from body
    document.body.classList.forEach(className => {
        if (className.startsWith('workflow-')) {
            document.body.classList.remove(className);
        }
    });
    
    // Add the new workflow mode class to body
    document.body.classList.add(`workflow-${mode}-mode`);
    
    // Show the appropriate panel based on mode
    switch (mode) {
        case 'color':
            // Show the color correction panel
            showWorkflowPanel('colorCorrectionPanel');
            updateToolbarForMode('color');
            
            // Add color preview mode UI
            const previewPanel = document.querySelector('.preview-panel');
            if (previewPanel) {
                previewPanel.classList.add('color-correction-preview');
            }
            
            // Add color mode markers with a delay to ensure DOM is ready
            setTimeout(() => {
                addColorModeMarkers();
                console.log("Color mode markers added");
                
                // Force a repaint/reflow to ensure UI updates
                document.body.style.display = 'none';
                requestAnimationFrame(() => {
                    document.body.style.display = '';
                });
            }, 100);
            break;
            
        case 'audio':
            showWorkflowPanel('audioMixingPanel');
            updateToolbarForMode('audio');
            
            // Add audio-specific UI changes
            const timelinePanel = document.querySelector('.timeline-panel');
            if (timelinePanel) {
                timelinePanel.classList.add('audio-mixing-timeline');
            }
            
            // Highlight audio tracks
            document.querySelectorAll('.track-content[data-track-type="audio"]').forEach(track => {
                track.style.backgroundColor = 'rgba(80, 205, 137, 0.1)';
            });
            break;
            
        case 'effects':
            showWorkflowPanel('visualEffectsPanel');
            updateToolbarForMode('effects');
            
            // Add effects-specific UI changes
            if (previewPanel) {
                previewPanel.classList.add('effects-preview');
            }
            
            const propertiesPanel = document.querySelector('.properties-panel');
            if (propertiesPanel) {
                propertiesPanel.classList.add('effects-properties');
                // Make properties panel wider for effects mode
                propertiesPanel.style.width = '360px';
            }
            break;
            
        case 'text':
            showWorkflowPanel('textGraphicsPanel');
            updateToolbarForMode('text');
            
            // Highlight text tracks
            document.querySelectorAll('.track-content[data-track-type="text"]').forEach(track => {
                track.style.backgroundColor = 'rgba(148, 0, 211, 0.1)';
            });
            break;
            
        case 'ai':
            showWorkflowPanel('aiAssistedPanel');
            updateToolbarForMode('ai');
            break;
            
        default:
            // Standard mode - no panel shown
            updateToolbarForMode('standard');
            
            // Reset any panel widths
            if (propertiesPanel) {
                propertiesPanel.style.width = '';
            }
            break;
    }
    
    // Apply UI changes based on the selected mode
    applyWorkflowTheme(mode);
    
    // Show notification
    showWorkflowNotification(mode);
    
    // Force UI update by triggering a resize event
    window.dispatchEvent(new Event('resize'));
    
    console.log(`Workflow mode switched to: ${mode}`);
}

// Show a specific workflow panel
function showWorkflowPanel(panelId) {
    console.log(`Attempting to show panel: ${panelId}`);
    const panel = document.getElementById(panelId);
    
    if (!panel) {
        console.error(`Panel with ID ${panelId} not found`);
        return;
    }
    
    // Make sure the panel is in the DOM
    if (!document.body.contains(panel)) {
        console.error(`Panel ${panelId} is not in the document`);
        return;
    }
    
    // Reset the panel style to ensure fresh display
    panel.style.display = 'block'; // First make it visible
    panel.style.opacity = '0';
    panel.style.transform = 'translateX(20px)';
    panel.style.zIndex = '500'; // Ensure panel is above other elements
    
    // Force layout calculation before animation
    void panel.offsetHeight; // This forces a reflow
    
    // Add animation with a slight delay
    setTimeout(() => {
        panel.style.opacity = '1';
        panel.style.transform = 'translateX(0)';
        
        // Log panel display for debugging
        console.log(`Panel ${panelId} is now displayed`);
        
        // Apply additional styling based on panel type
        if (panelId === 'colorCorrectionPanel') {
            enhanceColorCorrectionPanel();
        } else if (panelId === 'audioMixingPanel') {
            enhanceAudioMixingPanel();
        }
        
        // Force a reflow to ensure UI updates
        document.body.style.display = 'none';
        requestAnimationFrame(() => {
            document.body.style.display = '';
        });
    }, 50);  // Increased delay for better reliability
    
    // Add class to body to indicate panel is visible
    document.body.classList.add(`${panelId}-visible`);
}

// Function to enhance color correction panel
function enhanceColorCorrectionPanel() {
    console.log('Enhancing color correction panel');
    
    // Get required elements
    const colorPanel = document.getElementById('colorCorrectionPanel');
    const brightnessSlider = document.getElementById('brightness');
    const contrastSlider = document.getElementById('contrast');
    const saturationSlider = document.getElementById('saturation');
    const temperatureSlider = document.getElementById('temperature');
    
    // Debug missing elements
    if (!colorPanel) console.error('colorCorrectionPanel element missing');
    if (!brightnessSlider) console.error('brightness slider missing');
    if (!contrastSlider) console.error('contrast slider missing');
    if (!saturationSlider) console.error('saturation slider missing');
    if (!temperatureSlider) console.error('temperature slider missing');

    // Make sure controls are visible and properly initialized
    if (colorPanel) {
        console.log('Setting up color correction panel controls');
        
        // Make sure panel is visible
        colorPanel.style.display = 'block';
        
        // Reset sliders to default if they exist
        if (brightnessSlider) brightnessSlider.value = 0;
        if (contrastSlider) contrastSlider.value = 0;
        if (saturationSlider) saturationSlider.value = 0;
        if (temperatureSlider) temperatureSlider.value = 0;
        
        // Reset any active presets
        document.querySelectorAll('.color-preset').forEach(preset => {
            preset.classList.remove('active');
        });
        
        // Make sure preview is updated
        updateColorPreview();
        
        // Add panel visibility class to body
        document.body.classList.add('color-panel-visible');
        
        // Add color mode markers for the preview screens
        addColorModeMarkers();
        
        // Add class to preview panel
        const previewPanel = document.querySelector('.preview-panel');
        if (previewPanel) {
            previewPanel.classList.add('color-correction-preview');
        } else {
            console.error('Preview panel element not found');
        }
        
        // Make sure the panel contents are visible
        const panelSections = colorPanel.querySelectorAll('.panel-section-content');
        panelSections.forEach(section => {
            section.style.display = 'block';
        });
        
        console.log('Color correction panel fully enhanced with preview screens');
    } else {
        console.error('Could not find colorCorrectionPanel element');
    }
}

// Function to enhance audio mixing panel
function enhanceAudioMixingPanel() {
    // Get audio panel elements
    const audioPanel = document.getElementById('audioMixingPanel');
    const audioWave = document.querySelector('.audio-wave');
    
    if (audioPanel && audioWave) {
        console.log('Enhancing audio mixing panel');
        
        // Clear existing bars
        audioWave.innerHTML = '';
        
        // Add audio visualization bars
        for (let i = 0; i < 50; i++) {
            const bar = document.createElement('div');
            bar.className = 'bar';
            const height = Math.random() * 100;
            bar.style.height = `${height}%`;
            audioWave.appendChild(bar);
        }
        
        // Add panel visibility class to body
        document.body.classList.add('audio-panel-visible');
    }
}

// Hide a specific workflow panel
function hideWorkflowPanel(panelId) {
    const panel = document.getElementById(panelId);
    if (panel) {
        panel.style.opacity = '0';
        panel.style.transform = 'translateX(20px)';
        
        // Remove panel-specific body classes
        if (panelId === 'colorCorrectionPanel') {
            document.body.classList.remove('color-panel-visible');
        } else if (panelId === 'audioMixingPanel') {
            document.body.classList.remove('audio-panel-visible');
        }
        
        // After animation, hide panel
        setTimeout(() => {
            panel.style.display = 'none';
            
            // Remove any markers or enhancements when the panel is hidden
            if (panelId === 'colorCorrectionPanel') {
                removeColorModeMarkers();
            }
        }, 300);
    }
}

// Hide all workflow panels
function hideAllWorkflowPanels() {
    const panels = document.querySelectorAll('.workflow-panel');
    
    // Remove all panel visibility classes
    document.body.classList.remove('color-panel-visible', 'audio-panel-visible', 
                                  'effects-panel-visible', 'text-panel-visible',
                                  'ai-panel-visible');
    
    panels.forEach(panel => {
        panel.style.opacity = '0';
        panel.style.transform = 'translateX(20px)';
        
        // Get panel ID
        const panelId = panel.getAttribute('id');
        
        // After animation, hide panel
        setTimeout(() => {
            panel.style.display = 'none';
            
            // Remove any markers or enhancements when panels are hidden
            if (panelId === 'colorCorrectionPanel') {
                removeColorModeMarkers();
            }
        }, 300);
    });
}

// Show a notification when switching workflow modes
function showWorkflowNotification(mode) {
    // Create notification container if it doesn't exist
    let container = document.getElementById('notification-container');
    
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    // Create notification text based on mode
    let notificationText = 'Switched to Standard Editing mode';
    let notificationType = 'info';
    let icon = 'bi-film';
    
    if (mode === 'color') {
        notificationText = 'Switched to Color Correction mode';
        icon = 'bi-palette';
    } else if (mode === 'audio') {
        notificationText = 'Switched to Audio Mixing mode';
        icon = 'bi-music-note-beamed';
    } else if (mode === 'effects') {
        notificationText = 'Switched to Visual Effects mode';
        icon = 'bi-magic';
    } else if (mode === 'text') {
        notificationText = 'Switched to Text & Graphics mode';
        icon = 'bi-fonts';
    } else if (mode === 'ai') {
        notificationText = 'Switched to AI-Assisted mode';
        notificationType = 'success';
        icon = 'bi-stars';
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${notificationType}`;
    notification.style.backgroundColor = '#252536';
    notification.style.color = '#fff';
    notification.style.padding = '10px 15px';
    notification.style.borderRadius = '5px';
    notification.style.marginBottom = '10px';
    notification.style.boxShadow = '0 2px 10px rgba(0,0,0,0.3)';
    notification.style.display = 'flex';
    notification.style.alignItems = 'center';
    notification.style.transition = 'opacity 0.5s';
    
    notification.innerHTML = `
    <i class="bi ${icon}" style="margin-right: 8px;"></i>
    <span>${notificationText}</span>
    `;
    
    // Add notification to container
    container.appendChild(notification);
    
    // Update the dropdown button immediately
    const dropdownButton = document.getElementById('workflowSelector');
    if (dropdownButton) {
        let buttonText = 'Standard Editing';
        let buttonIcon = 'bi-film';
        
        if (mode === 'color') {
            buttonText = 'Color Correction';
            buttonIcon = 'bi-palette';
        } else if (mode === 'audio') {
            buttonText = 'Audio Mixing';
            buttonIcon = 'bi-music-note-beamed';
        } else if (mode === 'effects') {
            buttonText = 'Visual Effects';
            buttonIcon = 'bi-magic';
        } else if (mode === 'text') {
            buttonText = 'Text & Graphics';
            buttonIcon = 'bi-fonts';
        } else if (mode === 'ai') {
            buttonText = 'AI-Assisted Mode';
            buttonIcon = 'bi-stars';
        }
        
        dropdownButton.innerHTML = `<i class="bi ${buttonIcon}"></i> ${buttonText}`;
        
        // Force UI repaint
        dropdownButton.style.display = 'none';
        setTimeout(() => {
            dropdownButton.style.display = '';
        }, 0);
    }
    
    // Remove notification after timeout
    setTimeout(() => {
        notification.style.opacity = '0';
        
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 3000);
}

// Initialize color correction panel
function initColorCorrectionPanel() {
    // Get slider elements
    const sliders = document.querySelectorAll('.color-correction-panel input[type="range"]');
    
    // Add event listeners to sliders
    sliders.forEach(slider => {
        slider.addEventListener('input', updateColorPreview);
    });
    
    // Add event listeners to color presets
    const presets = document.querySelectorAll('.color-preset');
    presets.forEach(preset => {
        preset.addEventListener('click', function() {
            // Deselect all presets
            presets.forEach(p => p.classList.remove('active'));
            
            // Select this preset
            this.classList.add('active');
            
            // Apply preset values
            const presetName = this.getAttribute('title');
            applyColorPreset(presetName);
        });
    });
}

// Update color preview based on slider values
function updateColorPreview() {
    console.log('Updating color preview');
    
    // First update the small preview in the panel
    const panelPreview = document.querySelector('.color-preview');
    
    // Then update the main processed preview canvas
    const processedCanvas = document.getElementById('preview-canvas-processed');
    
    // Get all slider values
    const brightness = document.getElementById('brightness')?.value || 0;
    const contrast = document.getElementById('contrast')?.value || 0;
    const saturation = document.getElementById('saturation')?.value || 0;
    const temperature = document.getElementById('temperature')?.value || 0;
    const highlights = document.getElementById('highlights')?.value || 0;
    const shadows = document.getElementById('shadows')?.value || 0;
    const vibrance = document.getElementById('vibrance')?.value || 0;
    
    // Construct the CSS filter string
    const filterString = `
        brightness(${1 + brightness/100})
        contrast(${1 + contrast/100})
        saturate(${1 + saturation/100})
        ${temperature > 0 ? `sepia(${temperature/200})` : ''}
        ${temperature < 0 ? `hue-rotate(${temperature/-2}deg)` : ''}
        ${shadows < 0 ? `brightness(${1 + shadows/300}) contrast(${1 + Math.abs(shadows)/200})` : ''}
        ${shadows > 0 ? `brightness(${1 + shadows/300})` : ''}
        ${highlights !== 0 ? `opacity(${1 - Math.abs(highlights)/500})` : ''}
        ${vibrance > 0 ? `saturate(${1 + vibrance/100})` : ''}
        ${vibrance < 0 ? `grayscale(${Math.abs(vibrance)/200})` : ''}
    `;
    
    // Apply to small panel preview
    if (panelPreview) {
        panelPreview.style.filter = filterString;
    }
    
    // Apply to main processed preview
    if (processedCanvas) {
        processedCanvas.style.filter = filterString;
        
        // Add a subtle glow to indicate it's been processed
        processedCanvas.style.boxShadow = '0 0 20px rgba(74, 108, 247, 0.3)';
    }
    
    console.log(`Applied color filters: ${filterString.replace(/\s+/g, ' ').trim()}`);
}

// Apply color preset values
function applyColorPreset(presetName) {
    console.log(`Applying ${presetName} preset`);
    
    // Set slider values based on preset
    switch(presetName) {
        case 'Warm':
            setSliderValue('temperature', 30);
            setSliderValue('saturation', 20);
            setSliderValue('highlights', 10);
            break;
        case 'Cool':
            setSliderValue('temperature', -30);
            setSliderValue('saturation', 10);
            setSliderValue('highlights', -5);
            break;
        case 'Desaturated':
            setSliderValue('saturation', -80);
            setSliderValue('contrast', 20);
            break;
        case 'Cool Blue':
            setSliderValue('temperature', -40);
            setSliderValue('saturation', 15);
            setSliderValue('highlights', 5);
            break;
        case 'Golden':
            setSliderValue('temperature', 40);
            setSliderValue('saturation', 30);
            setSliderValue('highlights', 15);
            break;
        case 'Purple':
            setSliderValue('temperature', -20);
            setSliderValue('saturation', 20);
            setSliderValue('highlights', 10);
            setSliderValue('shadows', -10);
            break;
    }
    
    // Update preview
    updateColorPreview();
}

// Set slider value and trigger input event
function setSliderValue(sliderId, value) {
    const slider = document.getElementById(sliderId);
    if (slider) {
        slider.value = value;
        slider.dispatchEvent(new Event('input'));
    }
}

// Initialize audio panel
function initAudioPanel() {
    // Add event listeners to volume sliders
    const volumeSliders = document.querySelectorAll('.audio-mixing-panel input[type="range"]');
    volumeSliders.forEach(slider => {
        slider.addEventListener('input', function() {
            // Update volume visualization in a real implementation
            console.log(`Setting volume: ${this.value}`);
        });
    });
}

// Simulate audio visualization for demo purposes
function simulateAudioVisualization() {
    const audioWave = document.querySelector('.audio-wave');
    
    if (audioWave) {
        // Create audio bars
        for (let i = 0; i < 50; i++) {
            const bar = document.createElement('div');
            bar.className = 'bar';
            audioWave.appendChild(bar);
        }
        
        // Animate audio bars
        setInterval(() => {
            const bars = audioWave.querySelectorAll('.bar');
            bars.forEach(bar => {
                const height = Math.random() * 100;
                bar.style.height = `${height}%`;
            });
        }, 100);
    }
}

// Initialize effects panel
function initEffectsPanel() {
    // Add click handlers to effect items
    const effectItems = document.querySelectorAll('.effect-item');
    effectItems.forEach(item => {
        item.addEventListener('click', function() {
            // Select this effect
            const effectName = this.querySelector('div:last-child').textContent;
            console.log(`Selected effect: ${effectName}`);
            
            // Update effect selector
            const effectSelect = document.querySelector('.effect-controls select');
            if (effectSelect) {
                // Add option if it doesn't exist
                if (!Array.from(effectSelect.options).find(opt => opt.text === effectName)) {
                    const option = document.createElement('option');
                    option.text = effectName;
                    effectSelect.add(option);
                }
                
                // Select the option
                effectSelect.value = effectName;
            }
        });
    });
}

// Initialize text panel
function initTextPanel() {
    // Add click handlers to text templates
    const textTemplates = document.querySelectorAll('.text-template');
    textTemplates.forEach(template => {
        template.addEventListener('click', function() {
            // Get preview text
            const previewText = this.querySelector('.text-preview').textContent;
            
            // Update text input
            const textInput = document.querySelector('.text-graphics-panel input[type="text"]');
            if (textInput) {
                textInput.value = previewText;
            }
        });
    });
}

// Initialize AI panel
function initAIPanel() {
    // Add click handlers to AI suggestions
    const aiSuggestions = document.querySelectorAll('.ai-suggestion');
    aiSuggestions.forEach(suggestion => {
        suggestion.addEventListener('click', function() {
            // Get suggestion text
            const suggestionText = this.querySelector('div').textContent;
            
            // Show working state
            this.classList.add('active');
            
            // Simulate AI processing
            setTimeout(() => {
                // Show notification
                const container = document.getElementById('notification-container') || document.createElement('div');
                if (!container.id) {
                    container.id = 'notification-container';
                    document.body.appendChild(container);
                }
                
                const notification = document.createElement('div');
                notification.className = 'notification success';
                notification.innerHTML = `
                <i class="bi bi-stars"></i>
                <span>AI ${suggestionText} applied successfully</span>
                `;
                
                container.appendChild(notification);
                
                // Remove active state
                this.classList.remove('active');
                
                // Remove notification after timeout
                setTimeout(() => {
                    notification.classList.add('fade-out');
                    
                    setTimeout(() => {
                        notification.remove();
                    }, 500);
                }, 3000);
            }, 2000);
        });
    });
}

// Update timeline toolbar based on selected mode
function updateToolbarForMode(mode) {
    console.log(`Updating toolbar for ${mode} mode`);
    
    // Get timeline tools container
    const toolsContainer = document.querySelector('.timeline-header .tools');
    if (!toolsContainer) return;
    
    // Clear existing tools
    toolsContainer.innerHTML = '';
    
    // Add basic tools that are common to all modes
    toolsContainer.innerHTML = `
        <button class="btn btn-sm btn-outline-light" title="Split Clip" id="split-clip-btn">
            <i class="bi bi-scissors"></i>
        </button>
        <button class="btn btn-sm btn-outline-light" title="Delete Selected" id="delete-clip-btn">
            <i class="bi bi-trash"></i>
        </button>
    `;
    
    // Add mode-specific tools
    switch (mode) {
        case 'color':
            // Color correction tools
            toolsContainer.innerHTML += `
                <button class="btn btn-sm btn-outline-light" title="Color Correction" id="color-correction-btn">
                    <i class="bi bi-palette"></i>
                </button>
                <button class="btn btn-sm btn-outline-light" title="White Balance" id="white-balance-btn">
                    <i class="bi bi-brightness-high"></i>
                </button>
                <button class="btn btn-sm btn-outline-light" title="Color Grading" id="color-grading-btn">
                    <i class="bi bi-paint-bucket"></i>
                </button>
            `;
            break;
            
        case 'audio':
            // Audio tools
            toolsContainer.innerHTML += `
                <button class="btn btn-sm btn-outline-light" title="Audio Levels" id="audio-levels-btn">
                    <i class="bi bi-music-note-beamed"></i>
                </button>
                <button class="btn btn-sm btn-outline-light" title="Fade In/Out" id="audio-fade-btn">
                    <i class="bi bi-graph-up"></i>
                </button>
                <button class="btn btn-sm btn-outline-light" title="Noise Reduction" id="noise-reduction-btn">
                    <i class="bi bi-soundwave"></i>
                </button>
            `;
            break;
            
        case 'effects':
            // Effects tools
            toolsContainer.innerHTML += `
                <button class="btn btn-sm btn-outline-light" title="Add Effect" id="add-effect-btn">
                    <i class="bi bi-magic"></i>
                </button>
                <button class="btn btn-sm btn-outline-light" title="Transitions" id="transitions-btn">
                    <i class="bi bi-arrows-expand"></i>
                </button>
                <button class="btn btn-sm btn-outline-light" title="Keyframes" id="keyframes-btn">
                    <i class="bi bi-diamond"></i>
                </button>
            `;
            break;
            
        case 'text':
            // Text tools
            toolsContainer.innerHTML += `
                <button class="btn btn-sm btn-outline-light" title="Add Text" id="add-text-btn">
                    <i class="bi bi-fonts"></i>
                </button>
                <button class="btn btn-sm btn-outline-light" title="Text Animation" id="text-animation-btn">
                    <i class="bi bi-type-bold"></i>
                </button>
                <button class="btn btn-sm btn-outline-light" title="Lower Thirds" id="lower-thirds-btn">
                    <i class="bi bi-card-text"></i>
                </button>
            `;
            break;
            
        case 'ai':
            // AI tools
            toolsContainer.innerHTML += `
                <button class="btn btn-sm btn-primary" title="AI Auto Edit" id="ai-auto-edit-btn">
                    <i class="bi bi-stars"></i>
                </button>
                <button class="btn btn-sm btn-outline-light" title="Smart Trim" id="smart-trim-btn">
                    <i class="bi bi-lightning"></i>
                </button>
                <button class="btn btn-sm btn-outline-light" title="Generate Captions" id="generate-captions-btn">
                    <i class="bi bi-chat-square-text"></i>
                </button>
            `;
            break;
            
        default:
            // Standard editing tools
            toolsContainer.innerHTML += `
                <button class="btn btn-sm btn-outline-light" title="Add Track" id="add-track-btn">
                    <i class="bi bi-plus-lg"></i>
                </button>
            `;
            break;
    }
    
    // Add event listeners to the new buttons
    attachToolbarButtonListeners();
}

// Attach event listeners to toolbar buttons
function attachToolbarButtonListeners() {
    // Color correction tools
    document.getElementById('color-correction-btn')?.addEventListener('click', () => {
        console.log('Color correction tool clicked');
        showWorkflowPanel('colorCorrectionPanel');
    });
    
    // Audio tools
    document.getElementById('audio-levels-btn')?.addEventListener('click', () => {
        console.log('Audio levels tool clicked');
    });
    
    // Effects tools
    document.getElementById('add-effect-btn')?.addEventListener('click', () => {
        console.log('Add effect tool clicked');
    });
    
    // Text tools
    document.getElementById('add-text-btn')?.addEventListener('click', () => {
        console.log('Add text tool clicked');
    });
    
    // AI tools
    document.getElementById('ai-auto-edit-btn')?.addEventListener('click', () => {
        console.log('AI auto edit tool clicked');
        showNotification('AI auto edit processing...', 'info');
    });
}

// Show a notification message
function showNotification(message, type = 'info') {
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
    
    // Set icon based on type
    let icon = 'bi-info-circle';
    if (type === 'success') icon = 'bi-check-circle';
    if (type === 'warning') icon = 'bi-exclamation-triangle';
    if (type === 'error') icon = 'bi-x-circle';
    
    notification.innerHTML = `
        <i class="bi ${icon}"></i>
        <span>${message}</span>
    `;
    
    // Add notification to container
    container.appendChild(notification);
    
    // Remove notification after timeout
    setTimeout(() => {
        notification.classList.add('fade-out');
        
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 3000);
}

// Apply UI theme changes based on selected workflow mode
function applyWorkflowTheme(mode) {
    console.log(`Applying ${mode} mode UI theme`);
    
    // Get editor container
    const editor = document.querySelector('.editor-container');
    if (!editor) {
        console.error('Editor container not found');
        return;
    }
    
    // Apply specific UI adjustments for each mode
    const previewPanel = document.querySelector('.preview-panel');
    const mediaPanel = document.querySelector('.media-panel');
    const propertiesPanel = document.querySelector('.properties-panel');
    const timelinePanel = document.querySelector('.timeline-panel');
    
    // Debug missing elements
    if (!previewPanel) console.error('Preview panel not found');
    if (!mediaPanel) console.error('Media panel not found');
    if (!propertiesPanel) console.error('Properties panel not found');
    if (!timelinePanel) console.error('Timeline panel not found');
    
    // First reset all panel styles to their defaults
    // Reset background colors on tracks
    document.querySelectorAll('.track-content').forEach(elem => {
        elem.style.backgroundColor = '';
    });
    
    // Reset panel classes (but preserve base classes)
    if (previewPanel) {
        previewPanel.className = 'preview-panel';
    }
    if (timelinePanel) {
        timelinePanel.className = 'timeline-panel';
    }
    if (propertiesPanel) {
        propertiesPanel.className = 'properties-panel';
        propertiesPanel.style.width = ''; // Reset width
    }
    
    // Apply mode-specific UI changes
    switch (mode) {
        case 'color':
            // Color correction mode UI
            console.log('Applying color correction UI theme');
            if (previewPanel) {
                previewPanel.classList.add('color-correction-preview');
                console.log('Added color-correction-preview class to preview panel');
            }
            
            // Add color-specific preview markers
            addColorModeMarkers();
            
            // Add mode-specific header styling
            editor.style.setProperty('--current-mode-color', 'var(--theme-accent-primary, #4a6cf7)');
            break;
            
        case 'audio':
            // Audio mixing mode UI
            if (timelinePanel) {
                timelinePanel.classList.add('audio-mixing-timeline');
            }
            
            // Highlight audio tracks
            document.querySelectorAll('.track-content[data-track-type="audio"]').forEach(track => {
                track.style.backgroundColor = 'rgba(80, 205, 137, 0.1)';
                track.style.border = '1px solid rgba(80, 205, 137, 0.3)';
            });
            
            // Add mode-specific header styling
            editor.style.setProperty('--current-mode-color', '#50cd89');
            break;
            
        case 'effects':
            // Effects mode UI
            if (previewPanel) {
                previewPanel.classList.add('effects-preview');
            }
            
            if (propertiesPanel) {
                propertiesPanel.classList.add('effects-properties');
                // Make properties panel wider for effects mode
                propertiesPanel.style.width = '360px';
            }
            
            // Add mode-specific header styling
            editor.style.setProperty('--current-mode-color', '#ffc700');
            break;
            
        case 'text':
            // Text mode UI
            document.querySelectorAll('.track-content[data-track-type="text"]').forEach(track => {
                track.style.backgroundColor = 'rgba(148, 0, 211, 0.1)';
                track.style.border = '1px solid rgba(148, 0, 211, 0.3)';
            });
            
            // Add mode-specific header styling
            editor.style.setProperty('--current-mode-color', '#9400D3');
            break;
            
        case 'ai':
            // AI mode UI
            editor.classList.add('ai-mode');
            
            // Add mode-specific header styling
            editor.style.setProperty('--current-mode-color', '#9400D3');
            break;
            
        default:
            // Standard editing mode - panels already reset to default
            removeColorModeMarkers();
            
            // Reset mode-specific header styling
            editor.style.setProperty('--current-mode-color', 'var(--theme-accent-primary, #4a6cf7)');
            break;
    }
    
    // Make sure workflow theme CSS classes are applied to the body
    document.body.classList.add(`workflow-${mode}-mode`);
    
    // Force a UI refresh to ensure changes are applied
    setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
    }, 10);
    
    console.log(`${mode} mode UI theme applied`);
}

// Add color mode scopes and markers to the preview panel
function addColorModeMarkers() {
    // Get the preview panel element
    const previewPanel = document.querySelector('.preview-panel');
    if (!previewPanel) {
        console.error("Preview panel element not found");
        return;
    }
    
    // First clear any existing preview content
    const existingPreviewCanvas = document.getElementById('preview-canvas');
    if (existingPreviewCanvas) {
        // Store the original content to duplicate
        const originalContent = existingPreviewCanvas.innerHTML;
        
        // Clear the preview panel
        previewPanel.innerHTML = '';
        
        // Create two canvases - original and processed
        const originalCanvas = document.createElement('div');
        originalCanvas.id = 'preview-canvas-original';
        originalCanvas.className = 'video-canvas original';
        originalCanvas.innerHTML = originalContent;
        
        const processedCanvas = document.createElement('div');
        processedCanvas.id = 'preview-canvas-processed';
        processedCanvas.className = 'video-canvas processed';
        processedCanvas.innerHTML = originalContent;
        
        // Add both canvases to the preview panel
        previewPanel.appendChild(originalCanvas);
        previewPanel.appendChild(processedCanvas);
        
        // Add the color correction preview class
        previewPanel.classList.add('color-correction-preview');
        
        // Create markers for each canvas
        const originalMarkersDiv = document.createElement('div');
        originalMarkersDiv.id = 'color-mode-markers-original';
        originalMarkersDiv.className = 'color-mode-markers';
        originalMarkersDiv.innerHTML = `
            <div class="color-scope histogram" title="Histogram">
                <div class="scope-label">Histogram</div>
            </div>
        `;
        originalCanvas.appendChild(originalMarkersDiv);
        
        const processedMarkersDiv = document.createElement('div');
        processedMarkersDiv.id = 'color-mode-markers-processed';
        processedMarkersDiv.className = 'color-mode-markers';
        processedMarkersDiv.innerHTML = `
            <div class="color-scope waveform" title="Waveform">
                <div class="scope-label">Waveform</div>
            </div>
        `;
        processedCanvas.appendChild(processedMarkersDiv);
        
        // Style fixes
        originalMarkersDiv.style.display = 'flex';
        originalMarkersDiv.style.zIndex = '100';
        processedMarkersDiv.style.display = 'flex';
        processedMarkersDiv.style.zIndex = '100';
        
        console.log("Color mode preview created with two canvases and markers");
    } else {
        console.error("Original preview canvas not found");
    }
}

// Remove color mode markers and restore original preview
function removeColorModeMarkers() {
    // Get markers and remove them
    const originalMarkersDiv = document.getElementById('color-mode-markers-original');
    const processedMarkersDiv = document.getElementById('color-mode-markers-processed');
    
    if (originalMarkersDiv) originalMarkersDiv.remove();
    if (processedMarkersDiv) processedMarkersDiv.remove();
    
    // Check if we're in color correction mode with dual preview canvases
    const originalCanvas = document.getElementById('preview-canvas-original');
    const processedCanvas = document.getElementById('preview-canvas-processed');
    const previewPanel = document.querySelector('.preview-panel');
    
    if (originalCanvas && processedCanvas && previewPanel) {
        // We need to restore the original single canvas layout
        // Store the content from original canvas
        const originalContent = originalCanvas.innerHTML;
        
        // Clear the preview panel
        previewPanel.innerHTML = '';
        
        // Create a new single canvas with the original content
        const singleCanvas = document.createElement('div');
        singleCanvas.id = 'preview-canvas';
        singleCanvas.className = 'video-canvas';
        singleCanvas.innerHTML = originalContent;
        
        // Add the canvas back to the preview panel
        previewPanel.appendChild(singleCanvas);
        
        // Remove the color correction preview class
        previewPanel.classList.remove('color-correction-preview');
        
        console.log("Restored original preview layout");
    }
    
    // Also remove any legacy markers for backwards compatibility
    const legacyMarkersDiv = document.getElementById('color-mode-markers');
    if (legacyMarkersDiv) {
        legacyMarkersDiv.remove();
    }
}