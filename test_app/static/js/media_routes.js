/**
 * Media Routes - Handles direct access to media files and thumbnails
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Media routes script loaded');
    
    // Fix path issues with media assets
    fixMediaPaths();
    
    // Set up periodic check for media updates
    setInterval(checkMediaUpdates, 3000);
});

/**
 * Fix media file paths to ensure they point to the right location
 */
function fixMediaPaths() {
    // Find all media items in the DOM
    const mediaItems = document.querySelectorAll('.media-item');
    
    mediaItems.forEach(item => {
        const assetId = item.dataset.assetId;
        if (!assetId) return;
        
        // Find the asset in project data
        const asset = window.projectData?.assets?.find(a => a.id === assetId);
        if (!asset) return;
        
        // Fix the path if it doesn't start with http or /
        if (asset.path && !asset.path.startsWith('http') && !asset.path.startsWith('/')) {
            asset.path = '/uploads/' + asset.path.split('/').pop();
            console.log(`Fixed path for asset ${asset.id}: ${asset.path}`);
        }
        
        // Add a proper thumbnail path
        if (asset.type === 'video' && !asset.thumbnail_path) {
            const filename = asset.path.split('/').pop();
            const baseFilename = filename.split('.')[0];
            asset.thumbnail_path = `/uploads/${baseFilename}_thumb.jpg`;
            console.log(`Added thumbnail path for asset ${asset.id}: ${asset.thumbnail_path}`);
        }
        
        // Find thumbnail container and update it if needed
        const thumbnailContainer = item.querySelector('.media-thumbnail');
        if (thumbnailContainer) {
            // Check if we already have a proper image
            let thumbnailImg = thumbnailContainer.querySelector('img.thumbnail-img');
            
            // If we're a video and have a thumbnail path, add the thumbnail image
            if (asset.type === 'video' && asset.thumbnail_path && !thumbnailImg) {
                // Clear any default content
                const defaultIcon = thumbnailContainer.querySelector('i');
                if (defaultIcon) {
                    defaultIcon.style.display = 'none';
                }
                
                // Create thumbnail image
                thumbnailImg = document.createElement('img');
                thumbnailImg.src = asset.thumbnail_path;
                thumbnailImg.alt = asset.name;
                thumbnailImg.className = 'thumbnail-img';
                thumbnailImg.onerror = function() {
                    console.warn(`Failed to load thumbnail for ${asset.id}`);
                    this.style.display = 'none';
                    if (defaultIcon) defaultIcon.style.display = 'block';
                };
                
                thumbnailContainer.appendChild(thumbnailImg);
            }
            
            // Ensure we have a proper overlay
            let thumbnailOverlay = thumbnailContainer.querySelector('.thumbnail-overlay');
            if (!thumbnailOverlay) {
                thumbnailOverlay = document.createElement('div');
                thumbnailOverlay.className = 'thumbnail-overlay';
                thumbnailOverlay.innerHTML = '<i class="bi bi-play-circle"></i>';
                thumbnailContainer.appendChild(thumbnailOverlay);
            }
            
            // Set up click handler for the thumbnail
            thumbnailContainer.addEventListener('click', function(e) {
                e.stopPropagation();
                console.log(`Clicked on thumbnail for asset ${asset.id}`);
                
                // Highlight the media item
                document.querySelectorAll('.media-item').forEach(item => {
                    item.classList.remove('selected');
                });
                item.classList.add('selected');
                
                // Show preview for this asset
                if (window.playerUtils) {
                    window.playerUtils.showMediaPreview(asset);
                } else {
                    // Fallback method
                    previewMediaItem(asset);
                }
            });
        }
    });
}

/**
 * Preview media item in the preview area
 */
function previewMediaItem(asset) {
    if (!asset) return;
    
    console.log(`Previewing asset: ${asset.id}, type: ${asset.type}, path: ${asset.path}`);
    
    const previewCanvas = document.getElementById('preview-canvas');
    if (!previewCanvas) {
        console.error("Preview canvas not found");
        return;
    }
    
    // Clear preview content
    previewCanvas.innerHTML = '';
    
    // Create appropriate preview based on asset type
    if (asset.type === 'video' && asset.path) {
        // Create video element with proper attributes
        const videoEl = document.createElement('video');
        videoEl.className = 'w-100 h-100';
        videoEl.controls = false; // We'll use our own controls
        videoEl.autoplay = false;
        videoEl.preload = 'auto';
        videoEl.src = asset.path;
        videoEl.onerror = function(e) {
            console.error(`Error loading video: ${e.target.error?.message || 'Unknown error'}`);
            previewCanvas.innerHTML = `
                <div class="d-flex justify-content-center align-items-center h-100 text-white">
                    <div class="text-center">
                        <i class="bi bi-exclamation-triangle display-4" style="color: #ffc107;"></i>
                        <h5 class="mt-3">Video Error</h5>
                        <p>Unable to play this video file.</p>
                        <p class="small text-muted">Path: ${asset.path}</p>
                    </div>
                </div>
            `;
        };
        
        // Simple hook for play button
        videoEl.addEventListener('canplay', function() {
            const playBtn = document.getElementById('play-btn');
            if (playBtn) {
                playBtn.addEventListener('click', function() {
                    if (videoEl.paused) {
                        videoEl.play().catch(err => {
                            console.error('Error playing video:', err);
                        });
                    } else {
                        videoEl.pause();
                    }
                });
            }
        });
        
        previewCanvas.appendChild(videoEl);
        
        // Notify
        showNotification(`Loaded video: ${asset.name}`, "success");
    } else if (asset.type === 'image' && asset.path) {
        const imgElement = document.createElement('img');
        imgElement.src = asset.path;
        imgElement.className = 'w-100 h-100';
        imgElement.style.objectFit = 'contain';
        
        previewCanvas.appendChild(imgElement);
        showNotification(`Loaded image: ${asset.name}`, "success");
    } else {
        previewCanvas.innerHTML = `
            <div class="d-flex justify-content-center align-items-center h-100 text-white">
                <div class="text-center">
                    <i class="bi bi-exclamation-triangle display-4" style="color: #ffc107;"></i>
                    <h5 class="mt-3">Preview Not Available</h5>
                    <p>Unable to preview this media file.</p>
                    <p class="small text-muted">Type: ${asset.type}, Path: ${asset.path || 'Unknown'}</p>
                </div>
            </div>
        `;
    }
}

/**
 * Check for media updates (new files added)
 */
function checkMediaUpdates() {
    // Get all media container elements
    const mediaContainers = document.querySelectorAll('[id$="-media-items"]');
    
    // If we have no media containers, nothing to update
    if (!mediaContainers.length) return;
    
    // If we have project data with assets but no media items, re-populate
    if (window.projectData?.assets?.length > 0) {
        const allMediaContainer = document.getElementById('all-media-items');
        
        if (allMediaContainer && !allMediaContainer.children.length) {
            console.log('Re-populating media containers');
            
            // Re-populate media containers
            fixMediaPaths();
        }
    }
}

/**
 * Show a notification message
 */
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

// Make functions available globally
window.mediaRoutes = {
    fixMediaPaths,
    previewMediaItem,
    showNotification
};