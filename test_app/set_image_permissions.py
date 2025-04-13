#!/usr/bin/env python3
import os
import stat

def set_file_permissions(directory):
    """Set permissions for all files in the directory to be readable and writable by all"""
    print(f"Setting permissions for files in {directory}")
    
    # First, ensure the directory has correct permissions
    os.chmod(directory, 0o755)
    
    # Set permissions for all files in the directory
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        if os.path.isfile(filepath):
            # Make file readable and writable by all (644 permission)
            os.chmod(filepath, 0o644)
            print(f"  Set permissions for {filename}")
        elif os.path.isdir(filepath):
            # Recurse into subdirectories
            set_file_permissions(filepath)

if __name__ == "__main__":
    # Set permissions for custom image directory
    img_dir = "/root/OpenShot/test_app/static/img/custom"
    if os.path.exists(img_dir):
        set_file_permissions(img_dir)
        print("Successfully set permissions for the custom image directory")
    else:
        print(f"Directory {img_dir} does not exist")