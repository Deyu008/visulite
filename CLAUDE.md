# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VisuLite is an interactive scientific data visualization and export tool built with PySide6 + Matplotlib. It provides a "plug-and-play" experience for browsing, preprocessing, and charting CSV/TSV/Excel/JSON data with Chinese language interface.

## Development Environment Setup

```bash
# Activate the conda environment (already created)
conda activate visulite

# Install dependencies if needed
pip install -r requirements.txt

# Run the application
python main.py
```

## Core Dependencies

- **PySide6 >= 6.7**: Qt6 GUI framework
- **pandas >= 2.0**: Data manipulation and analysis
- **numpy >= 1.24**: Numerical computing
- **matplotlib >= 3.8**: Plotting and visualization
- **openpyxl >= 3.1**: Excel file support

## Architecture Overview

The application follows a layered architecture with clear separation of concerns:

### Entry Points

- `main.py`: Application entry point that calls `visulite.run_app()`
- `visulite/app.py`: Application bootstrap with QApplication setup and dark theme

### Core Layers

**Models Layer** (`visulite/models/`):

- `app_state.py`: Central state management with AppState dataclass holding dataframe and chart config
- `chart_config.py`: Chart configuration dataclass
- `dataframe_model.py`: Qt table model for pandas DataFrame display

**Services Layer** (`visulite/services/`):

- `data_loader.py`: Multi-format data import (CSV/TSV/Excel/JSON) with metadata extraction
- `chart_manager.py`: Matplotlib chart rendering supporting 6 chart types (line, bar, scatter, histogram, boxplot, heatmap)
- `data_processor.py`: Data preprocessing (filtering, missing value handling)
- `export_manager.py`: Chart export to PNG/JPG/SVG/PDF with DPI settings
- `config_manager.py`: Chart configuration save/load functionality
- `batch_plotter.py`: Batch plotting for multiple files with same configuration
- `recent_files.py`: Recent file management for quick access

**UI Layer** (`visulite/ui/`):

- `main_window.py`: Main Qt window with control panels and matplotlib canvas
- `widgets.py`: Custom Qt widgets including MatplotlibCanvas integration
- `styles.py`: Application styling with dark theme QSS

**Common** (`visulite/common/`):

- `logging.py`: Centralized logging configuration

## Key Architecture Patterns

1. **Dependency Injection**: UI layer creates and injects service dependencies
2. **State Management**: Centralized AppState pattern keeps original and processed data separate
3. **Service Boundaries**: Clear separation between UI logic and business logic in services layer
4. **Configuration Management**: ChartConfig dataclass for serializable chart settings

## Common Development Commands

```bash
# Activate environment
conda activate visulite

# Run the application
python main.py

# Install/update dependencies
pip install -r requirements.txt

# Run specific module for testing
python -m visulite.app
```

## Adding New Chart Types

When extending chart functionality:

1. Add the new chart type to `ChartManager.SUPPORTED_TYPES` in `visulite/services/chart_manager.py`
2. Implement the corresponding `_plot_<type>()` method in ChartManager
3. Add the chart type option to the dropdown in `MainWindow._build_chart_group()` in `visulite/ui/main_window.py`

## Logging Convention

All modules use structured logging with namespace `visulite.<module>` for easy debugging:

```python
logger = logging.getLogger("visulite.module_name")
```

## Data Flow

1. **Data Loading**: DataLoader → DataFrame + Metadata → AppState
2. **Data Processing**: DataProcessor modifies DataFrame → AppState.update_view()
3. **Chart Rendering**: ChartManager uses AppState data + ChartConfig → MatplotlibCanvas
4. **Export**: ExportManager takes Matplotlib figure → file output
5. **Batch Processing**: BatchPlotter applies chart configuration across multiple files

## UI Layout Structure

- Left panel: Data import, chart settings, preprocessing, statistics (360px min width)
- Right area: Vertical splitter with data table (top) and chart canvas (bottom) in 3:2 ratio

## File Format Support

Supported data formats with automatic detection and encoding support:

- CSV/TSV: pandas.read_csv() with separator detection and multi-encoding fallback
- Excel: pandas.read_excel() via openpyxl
- JSON: pandas.read_json() with orient='records' fallback
- Encoding support: UTF-8, UTF-8-SIG, GBK, GB2312, UTF-16, Latin-1

- Reading images and web searches are both performed using MCP.
