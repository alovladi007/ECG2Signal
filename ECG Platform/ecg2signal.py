
"""CLI for ECG2Signal."""
import typer
from pathlib import Path
from ecg2signal import ECGConverter
from ecg2signal.config import get_settings
from loguru import logger

app = typer.Typer(help="ECG2Signal: Convert ECG images to digital signals")

@app.command()
def convert(
    input_path: Path = typer.Argument(..., help="Input ECG image or PDF"),
    output: Path = typer.Option("./output", "--output", "-o", help="Output directory"),
    format: str = typer.Option("wfdb", "--format", "-f", help="Export format"),
    paper_speed: float = typer.Option(25.0, "--speed", "-s", help="Paper speed (mm/s)"),
    gain: float = typer.Option(10.0, "--gain", "-g", help="Gain (mm/mV)"),
):
    """Convert ECG image to digital signals."""
    if not input_path.exists():
        typer.echo(f"Error: Input file not found: {input_path}", err=True)
        raise typer.Exit(1)
    
    output.mkdir(parents=True, exist_ok=True)
    
    converter = ECGConverter(get_settings())
    
    typer.echo(f"Converting {input_path}...")
    result = converter.convert(str(input_path), paper_speed=paper_speed, gain=gain)
    
    typer.echo(f"Quality score: {result.quality_metrics.overall_score:.2f}")
    typer.echo(f"Exporting to {output}...")
    
    if format == "all":
        result.export_all(str(output))
    elif format == "wfdb":
        result.export_wfdb(str(output))
    elif format == "edf":
        result.export_edf(str(output / "ecg.edf"))
    elif format == "json":
        result.export_json(str(output / "ecg.json"))
    elif format == "csv":
        result.export_csv(str(output))
    
    typer.echo(f"✓ Conversion complete!")

@app.command()
def batch(
    input_dir: Path = typer.Argument(..., help="Input directory with ECG images"),
    output_dir: Path = typer.Option("./output", "--output", "-o"),
    workers: int = typer.Option(4, "--workers", "-w"),
):
    """Batch process ECG images."""
    files = list(input_dir.glob("**/*.jpg")) + list(input_dir.glob("**/*.pdf"))
    typer.echo(f"Found {len(files)} files")
    
    converter = ECGConverter(get_settings())
    converter.convert_batch([str(f) for f in files], str(output_dir))

def main():
    app()

if __name__ == "__main__":
    main()
