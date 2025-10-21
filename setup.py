"""
Setup script for CPG Inventory Management System

This script helps install and configure the application.
"""

from setuptools import setup, find_packages
import os
import sys

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Read README for long description
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cpg-inventory-system',
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='Smart Inventory and Sales Management System for CPG Companies',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/cpg-inventory-system',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.10',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'cpg-inventory=Home:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.yaml', '*.css', '*.md'],
    },
)

# Post-installation setup
def post_install():
    """Run post-installation tasks"""
    print("\n" + "="*60)
    print("CPG Inventory Management System - Setup")
    print("="*60 + "\n")
    
    # Create necessary directories
    directories = ['data', 'reports', 'logs', 'assets', 'utils']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}/")
    
    # Create __init__.py in utils if it doesn't exist
    init_file = 'utils/__init__.py'
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('# Utils package\n')
        print(f"✅ Created: {init_file}")
    
    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)
    print("\nTo run the application:")
    print("  streamlit run Home.py")
    print("\nDefault Login Credentials:")
    print("  Admin    - username: admin,    password: admin123")
    print("  Manager  - username: manager,  password: manager123")
    print("  Employee - username: employee, password: employee123")
    print("\n⚠️  Remember to change these passwords in production!")
    print("="*60 + "\n")

if __name__ == '__main__':
    post_install()
