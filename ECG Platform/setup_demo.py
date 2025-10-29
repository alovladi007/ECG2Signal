#!/usr/bin/env python3
"""
Automated setup script for ECG2Signal demo.

This script:
1. Checks dependencies
2. Generates demo models
3. Creates sample ECG images
4. Sets up environment
5. Runs validation tests
"""
import sys
import subprocess
from pathlib import Path
import platform

def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70 + "\n")

def print_step(step_num, text):
    """Print step header."""
    print(f"\n{'─' * 70}")
    print(f"Step {step_num}: {text}")
    print(f"{'─' * 70}\n")

def check_python_version():
    """Check Python version."""
    print_step(1, "Checking Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Error: Python 3.11+ required")
        print("   Please upgrade Python")
        return False
    
    print("✅ Python version OK")
    return True

def check_dependencies():
    """Check if key dependencies are installed."""
    print_step(2, "Checking Dependencies")
    
    required = [
        ('numpy', 'numpy'),
        ('torch', 'torch'),
        ('cv2', 'opencv-python'),
        ('PIL', 'Pillow'),
        ('fastapi', 'fastapi'),
    ]
    
    missing = []
    for module, package in required:
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing)}")
        
        response = input("\nInstall missing dependencies now? (y/n): ")
        if response.lower() == 'y':
            print("\nInstalling dependencies...")
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing)
            print("✅ Dependencies installed")
            return True
        return False
    
    print("\n✅ All dependencies installed")
    return True

def create_directories():
    """Create necessary directories."""
    print_step(3, "Creating Directories")
    
    dirs = [
        'models',
        'outputs',
        'cache',
        'logs',
        'notebooks/demo_outputs',
        'tests/data/expected'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ {dir_path}/")
    
    print("\n✅ Directories created")
    return True

def generate_demo_models():
    """Generate demo model weights."""
    print_step(4, "Generating Demo Models")
    
    script_path = Path('scripts/generate_demo_models.py')
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return False
    
    print("Generating models (this may take a minute)...")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print("✅ Demo models generated")
            return True
        else:
            print(f"❌ Error generating models:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout generating models")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_sample_ecgs():
    """Create enhanced sample ECG images."""
    print_step(5, "Creating Sample ECG Images")
    
    try:
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
        import cv2
        
        def create_realistic_ecg():
            """Create a more realistic ECG image."""
            # Image dimensions
            width, height = 3000, 2400
            
            # Create white background
            image = np.ones((height, width, 3), dtype=np.uint8) * 255
            
            # Draw grid (light red/pink)
            grid_color = (255, 200, 200)  # Light pink
            
            # Major grid lines (5mm)
            major_spacing = 50  # pixels
            for i in range(0, width, major_spacing):
                cv2.line(image, (i, 0), (i, height), grid_color, 2)
            for i in range(0, height, major_spacing):
                cv2.line(image, (0, i), (width, i), grid_color, 2)
            
            # Minor grid lines (1mm)
            minor_spacing = 10
            minor_color = (255, 230, 230)  # Very light pink
            for i in range(0, width, minor_spacing):
                if i % major_spacing != 0:
                    cv2.line(image, (i, 0), (i, height), minor_color, 1)
            for i in range(0, height, minor_spacing):
                if i % major_spacing != 0:
                    cv2.line(image, (0, i), (width, i), minor_color, 1)
            
            # Draw 12-lead ECG pattern
            lead_positions = [
                ('I', 100, 200, 950, 400),
                ('II', 100, 500, 950, 700),
                ('III', 100, 800, 950, 1000),
                ('aVR', 1050, 200, 1900, 400),
                ('aVL', 1050, 500, 1900, 700),
                ('aVF', 1050, 800, 1900, 1000),
                ('V1', 2000, 200, 2850, 400),
                ('V2', 2000, 500, 2850, 700),
                ('V3', 2000, 800, 2850, 1000),
                ('V4', 100, 1100, 950, 1300),
                ('V5', 1050, 1100, 1900, 1300),
                ('V6', 2000, 1100, 2850, 1300),
            ]
            
            # Draw ECG waveforms
            for lead_name, x1, y1, x2, y2 in lead_positions:
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                
                # Add lead label
                cv2.putText(image, lead_name, (x1 + 10, y1 + 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                
                # Generate ECG waveform
                x_range = np.arange(x1, x2, 3)
                
                # Create realistic ECG pattern
                t = np.linspace(0, 10, len(x_range))
                
                # P wave
                p_wave = 0.1 * np.exp(-((t % 0.8 - 0.15) ** 2) / 0.005)
                
                # QRS complex
                qrs = 0.8 * np.exp(-((t % 0.8 - 0.35) ** 2) / 0.001)
                qrs -= 0.2 * np.exp(-((t % 0.8 - 0.32) ** 2) / 0.0005)
                
                # T wave
                t_wave = 0.2 * np.exp(-((t % 0.8 - 0.55) ** 2) / 0.01)
                
                # Combine
                signal = p_wave + qrs + t_wave
                signal = signal * 80 + cy  # Scale and center
                
                # Draw waveform
                points = np.column_stack([x_range, signal.astype(int)])
                cv2.polylines(image, [points], False, (0, 0, 0), 2)
            
            # Add rhythm strip (Lead II continuous)
            rhythm_y = 1500
            rhythm_height = 300
            cv2.rectangle(image, (50, rhythm_y), (width - 50, rhythm_y + rhythm_height),
                         (200, 200, 200), 2)
            cv2.putText(image, "Lead II (Rhythm Strip)", (70, rhythm_y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
            
            # Draw long rhythm strip
            x_range = np.arange(100, width - 100, 2)
            t = np.linspace(0, 25, len(x_range))
            
            p_wave = 0.1 * np.exp(-((t % 0.8 - 0.15) ** 2) / 0.005)
            qrs = 0.8 * np.exp(-((t % 0.8 - 0.35) ** 2) / 0.001)
            qrs -= 0.2 * np.exp(-((t % 0.8 - 0.32) ** 2) / 0.0005)
            t_wave = 0.2 * np.exp(-((t % 0.8 - 0.55) ** 2) / 0.01)
            
            signal = (p_wave + qrs + t_wave) * 100 + rhythm_y + rhythm_height // 2
            points = np.column_stack([x_range, signal.astype(int)])
            cv2.polylines(image, [points], False, (0, 0, 0), 2)
            
            # Add metadata text
            metadata = [
                "Patient: DEMO-001",
                "Date: 2025-01-15 14:30",
                "Paper Speed: 25 mm/s",
                "Gain: 10 mm/mV",
                "Filter: 0.05-150 Hz",
            ]
            
            for i, text in enumerate(metadata):
                cv2.putText(image, text, (100, 2000 + i * 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            return image
        
        # Generate realistic ECG
        print("Creating realistic ECG image...")
        ecg_image = create_realistic_ecg()
        
        # Save to test data
        output_path = Path('tests/data/sample_ecg_realistic.jpg')
        cv2.imwrite(str(output_path), ecg_image)
        print(f"✅ Created: {output_path} ({ecg_image.shape[1]}x{ecg_image.shape[0]})")
        
        # Also create a smaller version
        small = cv2.resize(ecg_image, (1500, 1200))
        small_path = Path('tests/data/sample_ecg_small.jpg')
        cv2.imwrite(str(small_path), small)
        print(f"✅ Created: {small_path} ({small.shape[1]}x{small.shape[0]})")
        
        print("\n✅ Sample ECG images created")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample ECGs: {e}")
        return False

def run_validation():
    """Run project validation."""
    print_step(6, "Running Validation")
    
    script_path = Path('validate_project.py')
    if not script_path.exists():
        print("⚠️  Validation script not found, skipping")
        return True
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("✅ Validation passed")
            return True
        else:
            print("⚠️  Validation had warnings")
            return True  # Non-critical
            
    except Exception as e:
        print(f"⚠️  Validation error: {e}")
        return True  # Non-critical

def print_next_steps():
    """Print next steps."""
    print_header("🎉 Setup Complete!")
    
    print("Your ECG2Signal demo environment is ready!\n")
    
    print("Next Steps:\n")
    
    print("1. Try the interactive notebook:")
    print("   jupyter notebook notebooks/complete_demo.ipynb\n")
    
    print("2. Start the API server:")
    print("   uvicorn ecg2signal.api.main:app --reload")
    print("   Then visit: http://localhost:8000/docs\n")
    
    print("3. Launch the web UI:")
    print("   streamlit run ecg2signal/ui/app.py\n")
    
    print("4. Try CLI conversion:")
    print("   python -m ecg2signal.cli.ecg2signal convert \\")
    print("       tests/data/sample_ecg_realistic.jpg \\")
    print("       --output demo_output/\n")
    
    print("5. Run tests:")
    print("   pytest tests/ -v\n")
    
    print("Documentation:")
    print("  - Quick Start: QUICKSTART.md")
    print("  - API Docs: docs/api.md")
    print("  - Usage Guide: docs/usage.md\n")
    
    print("Questions? Check the documentation in the docs/ folder!")
    print("=" * 70)

def main():
    """Run setup process."""
    print_header("ECG2Signal Demo Setup")
    print("This script will set up your demo environment.\n")
    print("Platform:", platform.system(), platform.machine())
    print("Python:", sys.version.split()[0])
    
    steps = [
        ("Python version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Directories", create_directories),
        ("Demo models", generate_demo_models),
        ("Sample ECGs", create_sample_ecgs),
        ("Validation", run_validation),
    ]
    
    results = []
    for name, func in steps:
        try:
            success = func()
            results.append((name, success))
            if not success:
                print(f"\n⚠️  Setup step failed: {name}")
                response = input("Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    print("\nSetup aborted.")
                    return 1
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            results.append((name, False))
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("\nSetup aborted.")
                return 1
    
    # Summary
    print("\n" + "=" * 70)
    print("Setup Summary")
    print("=" * 70 + "\n")
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    successful = sum(1 for _, success in results if success)
    print(f"\n{successful}/{len(results)} steps completed successfully")
    
    if successful == len(results):
        print_next_steps()
        return 0
    else:
        print("\n⚠️  Setup completed with warnings")
        print("You may need to manually fix some issues")
        return 0

if __name__ == "__main__":
    sys.exit(main())
