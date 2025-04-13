#!/usr/bin/env python3
"""
OpenShot library fix script - sets up OpenShot Python bindings
"""
import os
import sys
import platform
import site
import shutil
import subprocess
from pathlib import Path

def main():
    """
    Main function to fix OpenShot library issues
    """
    print("Setting up OpenShot Library Python bindings...")
    
    # First, set environment variables
    os.environ["LD_LIBRARY_PATH"] = os.environ.get("LD_LIBRARY_PATH", "") + ":/usr/lib:/usr/local/lib"
    print(f"Set LD_LIBRARY_PATH: {os.environ['LD_LIBRARY_PATH']}")

    # Add common paths where OpenShot bindings might be
    potential_paths = [
        "/usr/lib/python3/dist-packages",
        "/usr/local/lib/python3/dist-packages",
        "/usr/lib/python3.8/site-packages",
        "/usr/local/lib/python3.8/site-packages",
        os.path.expanduser("~/OpenShot/openshot-server/build/src/bindings/python"),
        "/root/OpenShot/openshot-server/build/src/bindings/python"
    ]
    
    # Add paths to sys.path if they exist
    for path in potential_paths:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)
            print(f"Added path to Python: {path}")
    
    # Check if OpenShot libraries exist
    lib_paths = {
        "libopenshot.so": ["/usr/lib/libopenshot.so", "/usr/local/lib/libopenshot.so"],
        "libopenshot-audio.so": ["/usr/lib/libopenshot-audio.so", "/usr/local/lib/libopenshot-audio.so"]
    }
    
    libs_found = True
    for lib_name, paths in lib_paths.items():
        found = False
        for path in paths:
            if os.path.exists(path):
                print(f"Found {lib_name} at {path}")
                found = True
                break
        if not found:
            print(f"WARNING: {lib_name} not found in standard locations")
            libs_found = False
    
    # Try to import OpenShot to verify binding installation
    try:
        import openshot
        print(f"OpenShot Python binding imported successfully: {openshot.OPENSHOT_VERSION_FULL}")
        
        # Test a basic operation to verify it's working
        try:
            color = openshot.Color()
            print("OpenShot library functionality verified (created Color object)")
            return True
        except Exception as e:
            print(f"WARNING: OpenShot library imported but functionality test failed: {str(e)}")
    except ImportError as e:
        print(f"WARNING: Failed to import OpenShot Python bindings: {str(e)}")
        
        if libs_found:
            print("\nThe OpenShot libraries are installed but Python bindings are not working.")
            print("This is likely because the bindings weren't properly compiled or installed.")
            print("\nCreating symlink to system OpenShot bindings in virtual environment...")
            
            # Try to find the system openshot.so file
            openshot_so = None
            for path in potential_paths:
                potential_so = os.path.join(path, "openshot.so")
                if os.path.exists(potential_so):
                    openshot_so = potential_so
                    break
            
            if openshot_so:
                # Get the site-packages directory of the current virtual environment
                site_packages = site.getsitepackages()[0]
                try:
                    # Create a symlink to the system openshot.so
                    target = os.path.join(site_packages, "openshot.so")
                    print(f"Creating symlink from {openshot_so} to {target}")
                    if os.path.exists(target):
                        os.remove(target)
                    os.symlink(openshot_so, target)
                    print("Symlink created successfully!")
                    
                    # Try to import again after creating the symlink
                    try:
                        import openshot
                        print(f"SUCCESS! OpenShot Python binding imported successfully after fix: {openshot.OPENSHOT_VERSION_FULL}")
                        return True
                    except ImportError as e:
                        print(f"Still unable to import OpenShot after symlink: {str(e)}")
                except Exception as e:
                    print(f"Error creating symlink: {str(e)}")
            else:
                print("Could not find openshot.so file in system paths")
        
        print("\nUnable to fix OpenShot Python bindings. The application will run in fallback mode.")
        
    return False

if __name__ == "__main__":
    main()
