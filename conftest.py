import os
import sys

# Get absolute path of project root directory
project_root = os.path.dirname(os.path.abspath(__file__))

# Add project root directory to the Python path
sys.path.insert(0, project_root) 