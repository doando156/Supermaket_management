import os

def get_project_root():
    """Return the absolute path to the project root directory"""
    # Get the directory of this file (Code/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to reach the project root
    project_root = os.path.dirname(current_dir)
    return project_root

def get_image_path(image_name):
    """Return the absolute path to an image in the img directory"""
    return os.path.join(get_project_root(), 'img', image_name)