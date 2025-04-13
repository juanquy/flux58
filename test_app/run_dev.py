#!/usr/bin/env python3
import sys
import os
import socket
import subprocess
import time

# Use SQLite for easier testing with fallback
os.environ['DB_TYPE'] = 'sqlite'
os.environ['FLASK_SECRET_KEY'] = 'dev_secret_key_for_testing_only'

def check_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_process_using_port(port):
    """Get process using a port"""
    try:
        # Try using lsof (Linux/Mac)
        cmd = f"lsof -i :{port} -t"
        output = subprocess.check_output(cmd, shell=True).decode().strip()
        if output:
            return output.split('\n')[0]
    except subprocess.CalledProcessError:
        try:
            # Try using netstat (Linux)
            cmd = f"netstat -nlp | grep :{port} | awk '{{print $7}}' | cut -d'/' -f1"
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            if output:
                return output.split('\n')[0]
        except subprocess.CalledProcessError:
            pass
    return None

def prompt_kill_process(pid, port):
    """Ask user if they want to kill the process"""
    print(f"\033[91mERROR: Port {port} is already in use by process ID {pid}\033[0m")
    response = input(f"Do you want to kill the process using port {port}? (y/n): ")
    if response.lower() == 'y':
        try:
            # Try to kill the process
            subprocess.call(f"kill {pid}", shell=True)
            print(f"Process {pid} killed. Waiting for port to be freed...")
            
            # Wait for port to be freed
            for _ in range(5):  # Try for 5 seconds
                time.sleep(1)
                if not check_port_in_use(port):
                    print("Port is now available.")
                    return True
            
            print(f"\033[91mWarning: Process killed, but port {port} is still in use.\033[0m")
            print("Trying with more force...")
            subprocess.call(f"kill -9 {pid}", shell=True)
            time.sleep(2)
            
            if not check_port_in_use(port):
                print("Port is now available.")
                return True
            else:
                print(f"\033[91mERROR: Port {port} is still in use. Please try again later.\033[0m")
                return False
        except Exception as e:
            print(f"\033[91mERROR: Failed to kill process: {str(e)}\033[0m")
            return False
    return False

# Check if port 5000 is already in use
port = 5000
if check_port_in_use(port):
    pid = get_process_using_port(port)
    if pid:
        if not prompt_kill_process(pid, port):
            # User chose not to kill the process or killing failed
            print(f"\033[93mChoosing alternative port...\033[0m")
            # Try up to 10 alternative ports
            for alternative_port in range(5001, 5011):
                if not check_port_in_use(alternative_port):
                    port = alternative_port
                    print(f"\033[92mUsing alternative port {port}\033[0m")
                    break
            else:
                print(f"\033[91mERROR: All alternative ports are in use. Exiting.\033[0m")
                sys.exit(1)
    else:
        print(f"\033[91mERROR: Port {port} is in use, but couldn't identify the process.\033[0m")
        print(f"\033[93mTrying alternative port...\033[0m")
        # Try up to 10 alternative ports
        for alternative_port in range(5001, 5011):
            if not check_port_in_use(alternative_port):
                port = alternative_port
                print(f"\033[92mUsing alternative port {port}\033[0m")
                break
        else:
            print(f"\033[91mERROR: All alternative ports are in use. Exiting.\033[0m")
            sys.exit(1)

# Print environment for debugging
print("Environment variables:")
print("DB_HOST: {}".format(os.environ.get('DB_HOST')))
print("DB_PORT: {}".format(os.environ.get('DB_PORT')))
print("DB_NAME: {}".format(os.environ.get('DB_NAME')))
print("DB_USER: {}".format(os.environ.get('DB_USER')))
print("DB_PASS: {}".format(os.environ.get('DB_PASS')))
print("DB_TYPE: {}".format(os.environ.get('DB_TYPE')))

# Import app after setting environment variables
from app import app

if __name__ == '__main__':
    print(f"\033[92mStarting application on port {port}...\033[0m")
    app.run(host='0.0.0.0', port=port, debug=True)