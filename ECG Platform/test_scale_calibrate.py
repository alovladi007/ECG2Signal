
from ecg2signal.preprocess.scale_calibrate import pixels_to_time, pixels_to_voltage
from ecg2signal.types import PaperSettings

def test_pixels_to_time():
    settings = PaperSettings(paper_speed=25.0, gain=10.0, pixels_per_mm=10.0)
    time = pixels_to_time(250, settings)  # 250 pixels
    assert abs(time - 1.0) < 0.01  # Should be ~1 second

def test_pixels_to_voltage():
    settings = PaperSettings(paper_speed=25.0, gain=10.0, pixels_per_mm=10.0)
    voltage = pixels_to_voltage(100, settings)  # 100 pixels
    assert abs(voltage - 1.0) < 0.01  # Should be ~1 mV
