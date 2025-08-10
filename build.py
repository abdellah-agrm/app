# build.py
import PyInstaller.__main__
import os
import shutil

def build_application():
    # Clean up previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Run PyInstaller
    PyInstaller.__main__.run([
        'src/main.py',
        '--onefile',
        '--windowed',
        '--name=PhoneStoreManager',
        '--icon=assets/icon.ico',  # You should provide an icon file
        '--add-data=data;data',
        '--noconfirm'
    ])
    
    print("Build completed. The executable is in the 'dist' folder.")

if __name__ == "__main__":
    build_application()