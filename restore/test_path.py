import sys
import os

print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("Python path:", sys.path)

try:
    import psycopg2
    print("psycopg2 is installed!")
except ImportError:
    print("psycopg2 is not installed.")

try:
    from flask import Flask
    print("Flask is installed!")
except ImportError:
    print("Flask is not installed.")