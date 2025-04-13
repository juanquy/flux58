/**
 * Player and Media Preview Fixes
 * This file fixes issues with the media preview player and play button functionality
 */

// Wait for document to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("Initializing media player fixes...");
    
    // Fix play button functionality
    fixPlayButton();
    
    // Fix media thumbnails and preview
    fixMediaThumbnails();
    
    // Fix theme button duplication
    fixThemeButtons();
});

// Fix play button functionality
function fixPlayButton() {
    const playBtn = document.getElementById('play-btn');
    
    if (!playBtn) {
        console.error("Play button not found in the DOM");
        return;
    }
    
    console.log("Adding enhanced play button functionality");
    
    // Make sure it has the right icon and styling
    const playIcon = playBtn.querySelector('i');
    if (!playIcon) {
        playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
    }
    
    // Override the default click handler
    playBtn.addEventListener('click', function(e) {
        e.stopImmediatePropagation(); // Prevent multiple handlers
        const icon = this.querySelector('i');
        
        if (icon.classList.contains('bi-play-fill')) {
            // Switch to pause
            icon.classList.remove('bi-play-fill');
            icon.classList.add('bi-pause-fill');
            
            // Try to find and play video
            playVideoPreview();
        } else {
            // Switch to play
            icon.classList.remove('bi-pause-fill');
            icon.classList.add('bi-play-fill');
            
            // Pause any playing video
            pauseVideoPreview();
        }
    }, true);
}

// Play video in preview area
function playVideoPreview() {
    const previewCanvas = document.getElementById('preview-canvas');
    let videoElement = previewCanvas.querySelector('video');
    
    // If there's no video element, we need to create one
    if (!videoElement) {
        // Try to find a selected clip or first clip
        const selectedClip = document.querySelector('.clip.selected') || document.querySelector('.clip');
        
        if (selectedClip) {
            // Get asset info from the clip
            const assetId = selectedClip.dataset.assetId;
            
            // Find asset in project data
            const asset = window.projectData?.assets?.find(a => a.id === assetId);
            
            if (asset && asset.type === 'video' && asset.path) {
                // Clear preview content
                previewCanvas.innerHTML = '';
                
                // Create video element
                videoElement = document.createElement('video');
                videoElement.src = asset.path.startsWith('/') ? asset.path : '/' + asset.path;
                videoElement.className = 'w-100 h-100';
                videoElement.controls = false;
                
                // Add to preview
                previewCanvas.appendChild(videoElement);
            }
        }
    }
    
    // If we have a video element now, play it
    if (videoElement) {
        videoElement.play()
            .catch(err => {
                console.error("Error playing video:", err);
                showNotification("Error playing video. Check browser console for details.", "error");
            });
    } else {
        showNotification("No video to play. Try selecting a video clip first.", "info");
    }
}

// Pause video in preview area
function pauseVideoPreview() {
    const previewCanvas = document.getElementById('preview-canvas');
    const videoElement = previewCanvas.querySelector('video');
    
    if (videoElement) {
        videoElement.pause();
    }
}

// Fix media thumbnails and preview buttons
function fixMediaThumbnails() {
    // Find all media items
    const mediaItems = document.querySelectorAll('.media-item');
    
    mediaItems.forEach(item => {
        // Find or create thumbnail container
        let thumbnailContainer = item.querySelector('.media-thumbnail');
        
        if (!thumbnailContainer) {
            console.warn("Media item missing thumbnail container, creating one");
            const mediaInfo = item.querySelector('.media-info');
            
            if (mediaInfo) {
                thumbnailContainer = document.createElement('div');
                thumbnailContainer.className = 'media-thumbnail me-2';
                item.insertBefore(thumbnailContainer, mediaInfo);
            }
        }
        
        if (thumbnailContainer) {
            // Check if the thumbnail overlay exists
            let thumbnailOverlay = thumbnailContainer.querySelector('.thumbnail-overlay');
            
            if (!thumbnailOverlay) {
                thumbnailOverlay = document.createElement('div');
                thumbnailOverlay.className = 'thumbnail-overlay';
                thumbnailOverlay.innerHTML = '<i class="bi bi-play-circle"></i>';
                thumbnailContainer.appendChild(thumbnailOverlay);
            }
            
            // Make the thumbnail and overlay clickable
            thumbnailContainer.addEventListener('click', function(e) {
                e.stopPropagation();
                
                // Get asset ID from item
                const assetId = item.dataset.assetId;
                
                // Find asset in project data
                const asset = window.projectData?.assets?.find(a => a.id === assetId);
                
                if (asset) {
                    // Show preview of this media
                    showMediaPreview(asset);
                }
            });
        }
        
        // Fix preview button if it exists
        const previewBtn = item.querySelector('.media-preview-btn');
        if (previewBtn) {
            previewBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                
                // Get asset ID from item
                const assetId = item.dataset.assetId;
                
                // Find asset in project data
                const asset = window.projectData?.assets?.find(a => a.id === assetId);
                
                if (asset) {
                    // Show preview of this media
                    showMediaPreview(asset);
                }
            });
        }
    });
}

// Show media preview for an asset
function showMediaPreview(asset) {
    if (!asset) return;
    
    const previewCanvas = document.getElementById('preview-canvas');
    
    if (!previewCanvas) {
        console.error("Preview canvas not found");
        return;
    }
    
    // Clear preview content
    previewCanvas.innerHTML = '';
    
    // Create appropriate preview based on asset type
    if (asset.type === 'video' && asset.path) {
        const videoElement = document.createElement('video');
        videoElement.src = asset.path.startsWith('/') ? asset.path : '/' + asset.path;
        videoElement.className = 'w-100 h-100';
        videoElement.controls = false;
        videoElement.autoplay = false;
        
        previewCanvas.appendChild(videoElement);
        
        // Update play button to be in play state
        const playBtn = document.getElementById('play-btn');
        if (playBtn) {
            const icon = playBtn.querySelector('i');
            if (icon) {
                icon.className = 'bi bi-play-fill';
            }
        }
        
        showNotification(`Loaded video: ${asset.name}`, "success");
    } else if (asset.type === 'image' && asset.path) {
        const imgElement = document.createElement('img');
        imgElement.src = asset.path.startsWith('/') ? asset.path : '/' + asset.path;
        imgElement.className = 'w-100 h-100';
        imgElement.style.objectFit = 'contain';
        
        previewCanvas.appendChild(imgElement);
        
        showNotification(`Loaded image: ${asset.name}`, "success");
    } else if (asset.type === 'audio' && asset.path) {
        // For audio, add an audio element with controls
        const audioContainer = document.createElement('div');
        audioContainer.className = 'd-flex flex-column justify-content-center align-items-center h-100 text-white';
        
        audioContainer.innerHTML = `
            <i class="bi bi-music-note-beamed display-1" style="color: #50cd89;"></i>
            <h5 class="mt-3">${asset.name}</h5>
            <audio controls class="mt-3" src="${asset.path.startsWith('/') ? asset.path : '/' + asset.path}"></audio>
        `;
        
        previewCanvas.appendChild(audioContainer);
        
        showNotification(`Loaded audio: ${asset.name}`, "success");
    } else {
        previewCanvas.innerHTML = `
            <div class="d-flex justify-content-center align-items-center h-100 text-white">
                <div class="text-center">
                    <i class="bi bi-exclamation-triangle display-1" style="color: #ffc107;"></i>
                    <h5 class="mt-3">Preview Not Available</h5>
                    <p>Unable to preview this media file.</p>
                </div>
            </div>
        `;
        
        showNotification(`Unable to preview: ${asset.name}`, "error");
    }
}

// Fix duplicated theme buttons 
function fixThemeButtons() {
    // Find all editor buttons that might be duplicated
    const btnSelectors = [
        '#ai-assist-btn',
        '#export-btn',
        '#save-btn'
    ];
    
    btnSelectors.forEach(selector => {
        const buttons = document.querySelectorAll(selector);
        if (buttons.length > 1) {
            console.log(`Found ${buttons.length} instances of ${selector}, removing duplicates`);
            // Keep only the first one
            for (let i = 1; i < buttons.length; i++) {
                buttons[i].parentNode.removeChild(buttons[i]);
            }
        }
    });
    
    // Look for theme-related items
    const themeButtons = document.querySelectorAll('.theme-button, .theme-switcher');
    if (themeButtons.length > 1) {
        console.log(`Found ${themeButtons.length} theme buttons, removing duplicates`);
        for (let i = 1; i < themeButtons.length; i++) {
            themeButtons[i].style.display = 'none';
        }
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Check if notification container exists
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
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'exclamation-circle';
    
    notification.innerHTML = `
        <i class="bi bi-${icon} me-2"></i>
        <span>${message}</span>
    `;
    
    // Add to container
    container.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 3000);
}

// Initialize any additional functionality, for access from other scripts
window.playerUtils = {
    playVideoPreview,
    pauseVideoPreview,
    showMediaPreview,
    showNotification
};