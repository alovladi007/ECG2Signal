
# Model Architecture

## U-Net Segmentation

Separates ECG waveforms from grid and text.

**Architecture:**
- Encoder: 4 downsampling blocks
- Decoder: 4 upsampling blocks
- Skip connections
- Output: 3-channel mask (grid, waveform, text)

## Transformer OCR

Extracts text labels and metadata.

**Features:**
- Lead name recognition
- Paper speed detection
- Gain detection
- Patient metadata extraction

## Layout CNN

Detects 12-lead panel positions.

**Output:**
- Bounding boxes for 12 leads
- Rhythm strip detection
- Layout type classification
