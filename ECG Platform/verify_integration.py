#!/usr/bin/env python3
"""
Verification script for ECG2Signal integration.

This script verifies that all modules are properly integrated and importable.
"""

import sys
from pathlib import Path


def test_imports():
    """Test that all major imports work."""
    print("Testing imports...")
    errors = []

    # Test main package
    try:
        from ecg2signal import ECGConverter, Settings, ECGResult
        print("✓ Main package imports successful")
    except ImportError as e:
        errors.append(f"✗ Main package import failed: {e}")

    # Test subpackages
    subpackages = {
        "io": ["load_image", "save_image", "export_wfdb"],
        "preprocess": ["denoise_image", "detect_grid", "dewarp_image"],
        "layout": ["LeadLayoutDetector", "OCREngine"],
        "segment": ["separate_layers", "trace_curves"],
        "reconstruct": ["raster_to_signal", "resample_signals"],
        "clinical": ["compute_intervals", "compute_quality_metrics"],
        "training": ["train_unet", "generate_synthetic_ecg"],
        "utils": ["timeit"],
        "api": ["app"],
        "cli": ["cli"],
    }

    for subpkg, items in subpackages.items():
        try:
            module = __import__(f"ecg2signal.{subpkg}", fromlist=items)
            for item in items:
                if hasattr(module, item):
                    continue
                else:
                    errors.append(f"✗ ecg2signal.{subpkg}.{item} not found")
            print(f"✓ ecg2signal.{subpkg} imports successful")
        except ImportError as e:
            errors.append(f"✗ ecg2signal.{subpkg} import failed: {e}")

    return errors


def test_structure():
    """Test that the package structure is correct."""
    print("\nTesting package structure...")
    errors = []

    base_path = Path(__file__).parent / "ecg2signal"

    required_dirs = [
        "io",
        "preprocess",
        "layout",
        "segment",
        "segment/models",
        "reconstruct",
        "clinical",
        "training",
        "api",
        "cli",
        "ui",
        "utils",
    ]

    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        init_file = dir_path / "__init__.py"

        if not dir_path.exists():
            errors.append(f"✗ Directory missing: ecg2signal/{dir_name}")
        elif not init_file.exists():
            errors.append(f"✗ __init__.py missing: ecg2signal/{dir_name}")
        else:
            print(f"✓ ecg2signal/{dir_name} exists with __init__.py")

    return errors


def test_entry_points():
    """Test that entry points exist."""
    print("\nTesting entry points...")
    errors = []

    entry_files = [
        "run_api.py",
        "run_ui.py",
        "pyproject.toml",
    ]

    for file_name in entry_files:
        file_path = Path(__file__).parent / file_name
        if file_path.exists():
            print(f"✓ {file_name} exists")
        else:
            errors.append(f"✗ {file_name} missing")

    return errors


def test_docs():
    """Test that documentation exists."""
    print("\nTesting documentation...")
    errors = []

    doc_files = [
        "README.md",
        "SETUP.md",
        "QUICKSTART.md",
        "INTEGRATION_SUMMARY.md",
    ]

    for file_name in doc_files:
        file_path = Path(__file__).parent / file_name
        if file_path.exists():
            print(f"✓ {file_name} exists")
        else:
            errors.append(f"✗ {file_name} missing")

    return errors


def test_config():
    """Test configuration system."""
    print("\nTesting configuration...")
    errors = []

    try:
        from ecg2signal.config import Settings, get_settings

        settings = Settings(log_level="DEBUG")
        assert settings.log_level == "DEBUG"

        settings2 = get_settings()
        assert settings2 is not None

        print("✓ Configuration system working")
    except Exception as e:
        errors.append(f"✗ Configuration test failed: {e}")

    return errors


def main():
    """Run all verification tests."""
    print("=" * 70)
    print("ECG2Signal Integration Verification")
    print("=" * 70)

    all_errors = []

    # Run all tests
    all_errors.extend(test_imports())
    all_errors.extend(test_structure())
    all_errors.extend(test_entry_points())
    all_errors.extend(test_docs())
    all_errors.extend(test_config())

    # Summary
    print("\n" + "=" * 70)
    if all_errors:
        print(f"VERIFICATION FAILED with {len(all_errors)} error(s):")
        for error in all_errors:
            print(f"  {error}")
        print("=" * 70)
        return 1
    else:
        print("✓ ALL VERIFICATION TESTS PASSED!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Install the package: pip install -e .")
        print("  2. Read QUICKSTART.md to get started")
        print("  3. Run tests: pytest tests/test_integration.py")
        print("  4. Try the CLI: ecg2signal --help")
        print("=" * 70)
        return 0


if __name__ == "__main__":
    sys.exit(main())
