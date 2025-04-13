// Initialize workspace switcher
function initWorkspaceSwitcher() {
    console.log("Initializing workspace switcher...");
    
    // Get all workspace selector links
    const workspaceLinks = document.querySelectorAll('.workspace-switcher .dropdown-item');
    
    // Add click event listener to each workspace link
    workspaceLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the workspace type from data attribute
            const workspaceType = this.getAttribute('data-workspace');
            
            // Switch to the selected workspace
            switchToWorkspace(workspaceType);
            
            // Update active state in menu
            workspaceLinks.forEach(item => item.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Load the last used workspace if available
    const lastWorkspace = localStorage.getItem('last_workspace') || 'standard';
    switchToWorkspace(lastWorkspace);
    
    // Update the active menu item
    const activeLink = document.querySelector(`.workspace-switcher .dropdown-item[data-workspace="${lastWorkspace}"]`);
    if (activeLink) {
        workspaceLinks.forEach(item => item.classList.remove('active'));
        activeLink.classList.add('active');
    }
}

// Switch to a specific workspace
function switchToWorkspace(workspaceType) {
    console.log(`Switching to ${workspaceType} workspace`);
    
    // Get the editor container
    const editorContainer = document.querySelector('.editor-container');
    
    // Remove all workspace classes
    editorContainer.classList.remove(
        'workspace-standard',
        'workspace-color-correction',
        'workspace-audio',
        'workspace-effects',
        'workspace-multicam',
        'workspace-custom'
    );
    
    // Add the new workspace class
    editorContainer.classList.add(`workspace-${workspaceType}`);
    
    // Save the current workspace to localStorage
    localStorage.setItem('last_workspace', workspaceType);
    
    // Specific workspace adjustments
    switch (workspaceType) {
        case 'standard':
            // Show standard preview, hide others
            document.getElementById('standard-preview').style.display = 'flex';
            document.getElementById('color-correction-preview').style.display = 'none';
            document.getElementById('color-scopes-panel').style.display = 'none';
            break;
            
        case 'color-correction':
            // Show color correction preview, hide standard
            document.getElementById('standard-preview').style.display = 'none';
            document.getElementById('color-correction-preview').style.display = 'flex';
            document.getElementById('color-scopes-panel').style.display = 'flex';
            
            // Initialize color scopes if needed
            initColorScopes();
            break;
            
        case 'audio':
            // Show standard preview, hide others
            document.getElementById('standard-preview').style.display = 'flex';
            document.getElementById('color-correction-preview').style.display = 'none';
            document.getElementById('color-scopes-panel').style.display = 'none';
            
            // Expand timeline for audio waveforms
            const timelinePanel = document.querySelector('.timeline-panel');
            if (timelinePanel) {
                timelinePanel.style.height = '300px';
            }
            break;
            
        case 'effects':
            // Show standard preview, hide others
            document.getElementById('standard-preview').style.display = 'flex';
            document.getElementById('color-correction-preview').style.display = 'none';
            document.getElementById('color-scopes-panel').style.display = 'none';
            
            // Expand properties panel for effects controls
            const propertiesPanel = document.querySelector('.properties-panel');
            if (propertiesPanel) {
                propertiesPanel.style.width = '400px';
            }
            break;
            
        case 'multicam':
            // Handle multicam view (would need additional templates)
            document.getElementById('standard-preview').style.display = 'flex';
            document.getElementById('color-correction-preview').style.display = 'none';
            document.getElementById('color-scopes-panel').style.display = 'none';
            showError("Multicam workspace coming soon");
            break;
            
        case 'custom':
            // Allow user to customize layout (future feature)
            showCustomLayoutDialog();
            break;
    }
    
    // Refresh UI elements
    window.dispatchEvent(new Event('resize'));
}

// Initialize color scopes for color correction workspace
function initColorScopes() {
    // Demo implementation - in a real app, these would display actual scopes
    const canvases = [
        document.getElementById('rgb-parade'),
        document.getElementById('vectorscope'),
        document.getElementById('histogram'),
        document.getElementById('waveform')
    ];
    
    canvases.forEach(canvas => {
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        
        // Set canvas width and height to match its display size
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw demo content
        if (canvas.id === 'rgb-parade') {
            drawRGBParadeDemo(ctx, canvas.width, canvas.height);
        } else if (canvas.id === 'vectorscope') {
            drawVectorscopeDemo(ctx, canvas.width, canvas.height);
        } else if (canvas.id === 'histogram') {
            drawHistogramDemo(ctx, canvas.width, canvas.height);
        } else if (canvas.id === 'waveform') {
            drawWaveformDemo(ctx, canvas.width, canvas.height);
        }
    });
}

// Draw RGB Parade demo
function drawRGBParadeDemo(ctx, width, height) {
    // Draw red channel
    ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
    ctx.beginPath();
    ctx.moveTo(width * 0.1, height);
    
    for (let x = 0; x < width * 0.3; x++) {
        const y = height - Math.abs(Math.sin(x * 0.1) * height * 0.8);
        ctx.lineTo(x + width * 0.05, y);
    }
    
    ctx.lineTo(width * 0.35, height);
    ctx.closePath();
    ctx.fill();
    
    // Draw green channel
    ctx.fillStyle = 'rgba(0, 255, 0, 0.5)';
    ctx.beginPath();
    ctx.moveTo(width * 0.37, height);
    
    for (let x = 0; x < width * 0.3; x++) {
        const y = height - Math.abs(Math.cos(x * 0.05) * height * 0.7);
        ctx.lineTo(x + width * 0.37, y);
    }
    
    ctx.lineTo(width * 0.67, height);
    ctx.closePath();
    ctx.fill();
    
    // Draw blue channel
    ctx.fillStyle = 'rgba(0, 0, 255, 0.5)';
    ctx.beginPath();
    ctx.moveTo(width * 0.7, height);
    
    for (let x = 0; x < width * 0.3; x++) {
        const y = height - Math.abs(Math.sin(x * 0.08) * height * 0.6);
        ctx.lineTo(x + width * 0.7, y);
    }
    
    ctx.lineTo(width, height);
    ctx.closePath();
    ctx.fill();
}

// Draw Vectorscope demo
function drawVectorscopeDemo(ctx, width, height) {
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 10;
    
    // Draw outer circle
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.stroke();
    
    // Draw color points
    const colors = [
        { angle: 0, color: 'red' },
        { angle: 60, color: 'yellow' },
        { angle: 120, color: 'green' },
        { angle: 180, color: 'cyan' },
        { angle: 240, color: 'blue' },
        { angle: 300, color: 'magenta' }
    ];
    
    colors.forEach(color => {
        const angle = color.angle * Math.PI / 180;
        const x = centerX + Math.cos(angle) * radius * 0.8;
        const y = centerY + Math.sin(angle) * radius * 0.8;
        
        ctx.fillStyle = color.color;
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
        ctx.font = '10px Arial';
        ctx.fillText(color.color, x + 7, y);
    });
    
    // Draw sample data
    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
    for (let i = 0; i < 100; i++) {
        const angle = Math.random() * Math.PI * 2;
        const distance = Math.random() * radius * 0.7;
        const x = centerX + Math.cos(angle) * distance;
        const y = centerY + Math.sin(angle) * distance;
        
        ctx.beginPath();
        ctx.arc(x, y, 1, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Draw Histogram demo
function drawHistogramDemo(ctx, width, height) {
    // Draw background grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.beginPath();
    for (let x = 0; x < width; x += width / 10) {
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
    }
    for (let y = 0; y < height; y += height / 5) {
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
    }
    ctx.stroke();
    
    // Draw RGB histograms
    const drawHistogram = (color, offset) => {
        ctx.fillStyle = color;
        
        for (let x = 0; x < width; x++) {
            const barHeight = Math.sin((x / width) * Math.PI + offset) * height * 0.4;
            ctx.fillRect(x, height - barHeight, 1, barHeight);
        }
    };
    
    drawHistogram('rgba(255, 0, 0, 0.3)', 0);
    drawHistogram('rgba(0, 255, 0, 0.3)', 0.5);
    drawHistogram('rgba(0, 0, 255, 0.3)', 1);
}

// Draw Waveform demo
function drawWaveformDemo(ctx, width, height) {
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.lineWidth = 1;
    
    // Draw horizontal lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.beginPath();
    for (let y = 0; y < height; y += height / 8) {
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
    }
    ctx.stroke();
    
    // Draw waveform
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.beginPath();
    ctx.moveTo(0, height / 2);
    
    for (let x = 0; x < width; x++) {
        const y = height / 2 + Math.sin(x * 0.05) * height * 0.2 + Math.sin(x * 0.01) * height * 0.2;
        ctx.lineTo(x, y);
    }
    
    ctx.stroke();
}

// Show custom layout dialog
function showCustomLayoutDialog() {
    showError("Custom layout options coming soon");
}