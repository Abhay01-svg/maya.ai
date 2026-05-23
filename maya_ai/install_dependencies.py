#!/usr/bin/env python3
"""
Maya AI Dependencies Installer
Automatically installs required and optional libraries
"""

import subprocess
import sys
import importlib
from pathlib import Path

class DependencyInstaller:
    """Install Maya AI dependencies"""
    
    def __init__(self):
        self.core_dependencies = [
            "Flask==2.3.3",
            "Werkzeug==2.3.7",
            "requests==2.31.0",
            "numpy==1.24.3",
            "beautifulsoup4==4.12.2",
            "lxml==4.9.3",
            "psutil==5.9.5"
        ]
        
        self.optional_dependencies = {
            "Image Processing": [
                "Pillow==10.0.1",
                "pytesseract==0.3.10"
            ],
            "PDF Processing": [
                "PyPDF2==3.0.1",
                "pdfplumber==0.9.0"
            ],
            "Document Processing": [
                "python-docx==0.8.11"
            ],
            "Voice/Speech": [
                "SpeechRecognition==3.10.0",
                "pyttsx3==2.90"
            ],
            "Advanced ML": [
                "scikit-learn==1.3.0",
                "xgboost==1.7.6"
            ],
            "Scheduling": [
                "APScheduler==3.10.4"
            ]
        }
        
        self.installed_packages = set()
        self.failed_packages = set()
    
    def install_package(self, package_name):
        """Install a single package"""
        try:
            print(f"📦 Installing {package_name}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully installed {package_name}")
                self.installed_packages.add(package_name)
                return True
            else:
                print(f"❌ Failed to install {package_name}: {result.stderr}")
                self.failed_packages.add(package_name)
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout installing {package_name}")
            self.failed_packages.add(package_name)
            return False
        except Exception as e:
            print(f"❌ Error installing {package_name}: {e}")
            self.failed_packages.add(package_name)
            return False
    
    def check_package_installed(self, package_name):
        """Check if package is already installed"""
        try:
            # Handle package name vs import name differences
            import_name = package_name.split('==')[0].split('>=')[0].split('<=')[0]
            
            # Special cases for import names
            import_mapping = {
                'Pillow': 'PIL',
                'beautifulsoup4': 'bs4',
                'python-docx': 'docx',
                'pytesseract': 'pytesseract',
                'SpeechRecognition': 'speech_recognition',
                'pyttsx3': 'pyttsx3',
                'APScheduler': 'apscheduler',
                'scikit-learn': 'sklearn',
                'xgboost': 'xgboost',
                'pdfplumber': 'pdfplumber',
                'PyPDF2': 'PyPDF2'
            }
            
            import_name = import_mapping.get(import_name, import_name.lower())
            
            importlib.import_module(import_name)
            return True
        except ImportError:
            return False
        except Exception as e:
            print(f"⚠️  Error checking {package_name}: {e}")
            return False
    
    def install_core_dependencies(self):
        """Install core dependencies"""
        print("\n🔧 Installing Core Dependencies")
        print("=" * 50)
        
        for package in self.core_dependencies:
            if self.check_package_installed(package):
                print(f"✅ {package} already installed")
                self.installed_packages.add(package)
            else:
                self.install_package(package)
    
    def install_optional_dependencies(self):
        """Install optional dependencies by category"""
        print("\n🎯 Optional Dependencies")
        print("=" * 50)
        
        for category, packages in self.optional_dependencies.items():
            print(f"\n📂 {category}:")
            for package in packages:
                if self.check_package_installed(package):
                    print(f"  ✅ {package} already installed")
                    self.installed_packages.add(package)
                else:
                    print(f"  📦 Installing {package}...")
                    self.install_package(package)
    
    def install_all(self, install_optional=False):
        """Install all dependencies"""
        print("🚀 Maya AI Dependency Installer")
        print("=" * 50)
        
        # Install core dependencies
        self.install_core_dependencies()
        
        # Install optional dependencies if requested
        if install_optional:
            self.install_optional_dependencies()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print installation summary"""
        print("\n📊 Installation Summary")
        print("=" * 50)
        
        print(f"✅ Successfully installed: {len(self.installed_packages)} packages")
        print(f"❌ Failed to install: {len(self.failed_packages)} packages")
        
        if self.installed_packages:
            print("\n✅ Installed packages:")
            for package in sorted(self.installed_packages):
                print(f"  • {package}")
        
        if self.failed_packages:
            print("\n❌ Failed packages:")
            for package in sorted(self.failed_packages):
                print(f"  • {package}")
        
        # Recommendations
        print("\n💡 Recommendations:")
        if len(self.failed_packages) > 0:
            print("  • Try installing failed packages manually:")
            for package in sorted(self.failed_packages):
                print(f"    pip install {package}")
        
        print("  • For full functionality, install optional dependencies:")
        print("    python install_dependencies.py --optional")
        
        print("\n🎉 Installation complete! You can now run Maya AI.")

def main():
    """Main installation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Install Maya AI dependencies")
    parser.add_argument("--optional", action="store_true", 
                       help="Install optional dependencies for full functionality")
    parser.add_argument("--core-only", action="store_true", 
                       help="Install only core dependencies")
    
    args = parser.parse_args()
    
    installer = DependencyInstaller()
    
    if args.core_only:
        installer.install_core_dependencies()
        installer.print_summary()
    else:
        installer.install_all(install_optional=args.optional)

if __name__ == "__main__":
    main()
