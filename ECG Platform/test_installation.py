#!/usr/bin/env python3
"""
Simple test runner to verify ECG2Signal installation.

Runs basic functionality tests without requiring full test suite.
"""
import sys
from pathlib import Path

def test_imports():
    """Test basic imports."""
    print("Testing imports...")
    try:
        import numpy as np
        import cv2
        import torch
        from ecg2signal import ECGConverter
        from ecg2signal.config import Settings
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration."""
    print("\nTesting configuration...")
    try:
        from ecg2signal.config import get_settings
        settings = get_settings()
        print(f"✅ Configuration loaded")
        print(f"   - Default paper speed: {settings.default_paper_speed} mm/s")
        print(f"   - Default gain: {settings.default_gain} mm/mV")
        print(f"   - Default sample rate: {settings.default_sample_rate} Hz")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_image_processing():
    """Test basic image processing."""
    print("\nTesting image processing...")
    try:
        import numpy as np
        import cv2
        from ecg2signal.preprocess import denoise, detect_page
        
        # Create test image
        test_img = np.random.randint(0, 255, (512, 512), dtype=np.uint8)
        
        # Test denoise
        denoised = denoise.denoise_image(test_img)
        assert denoised.shape == test_img.shape
        
        # Test page detection
        page = detect_page.detect_and_crop_page(test_img)
        assert page.shape[0] > 0 and page.shape[1] > 0
        
        print("✅ Image processing works")
        return True
    except Exception as e:
        print(f"❌ Image processing error: {e}")
        return False

def test_signal_processing():
    """Test signal processing."""
    print("\nTesting signal processing...")
    try:
        import numpy as np
        from ecg2signal.reconstruct import resample, postprocess
        
        # Create test signal
        test_signal = np.sin(np.linspace(0, 10 * np.pi, 1000))
        
        # Test resample
        resampled = resample.resample_signal(test_signal, target_fs=500.0)
        assert len(resampled) > 0
        
        # Test postprocess
        processed = postprocess.postprocess_signal(resampled)
        assert len(processed) == len(resampled)
        
        print("✅ Signal processing works")
        return True
    except Exception as e:
        print(f"❌ Signal processing error: {e}")
        return False

def test_io():
    """Test I/O operations."""
    print("\nTesting I/O operations...")
    try:
        import numpy as np
        import tempfile
        from pathlib import Path
        from ecg2signal.io import wfdb_io
        
        # Create test signals
        signals = {
            'I': np.sin(np.linspace(0, 10 * np.pi, 1000)),
            'II': np.sin(np.linspace(0, 10 * np.pi, 1000)) * 0.5
        }
        
        # Test WFDB write
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'test'
            wfdb_io.write_wfdb(signals, str(output_path), fs=500.0)
            
            # Check files exist
            assert (Path(tmpdir) / 'test.dat').exists()
            assert (Path(tmpdir) / 'test.hea').exists()
        
        print("✅ I/O operations work")
        return True
    except Exception as e:
        print(f"❌ I/O error: {e}")
        return False

def test_api():
    """Test API can be imported."""
    print("\nTesting API...")
    try:
        from ecg2signal.api import main
        from ecg2signal.api import schemas
        print("✅ API imports work")
        return True
    except Exception as e:
        print(f"❌ API error: {e}")
        return False

def test_sample_file():
    """Test with sample file if available."""
    print("\nTesting with sample file...")
    
    sample_path = Path('tests/data/sample_ecg_photo.jpg')
    if not sample_path.exists():
        print("⚠️  Sample file not found, skipping")
        return True
    
    try:
        from ecg2signal.io import image_io
        
        # Load image
        img = image_io.load_image(str(sample_path))
        assert img is not None
        assert len(img.shape) in [2, 3]
        
        print(f"✅ Successfully loaded sample: {img.shape}")
        return True
    except Exception as e:
        print(f"❌ Sample file error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 70)
    print("ECG2Signal Quick Test")
    print("=" * 70)
    print("\nRunning basic functionality tests...\n")
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Image Processing", test_image_processing),
        ("Signal Processing", test_signal_processing),
        ("I/O Operations", test_io),
        ("API", test_api),
        ("Sample File", test_sample_file),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70 + "\n")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your installation is working correctly.")
        print("\nNext steps:")
        print("  - Run the demo notebook: jupyter notebook notebooks/complete_demo.ipynb")
        print("  - Start the API: uvicorn ecg2signal.api.main:app --reload")
        print("  - Try the CLI: python -m ecg2signal.cli.ecg2signal convert --help")
        return 0
    else:
        print("\n⚠️  Some tests failed. You may need to:")
        print("  - Install missing dependencies: pip install -r requirements.txt")
        print("  - Generate demo models: python scripts/generate_demo_models.py")
        print("  - Check the documentation for troubleshooting")
        return 1

if __name__ == "__main__":
    sys.exit(main())
