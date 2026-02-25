# UI Smoke Checklist

This checklist is for validating VisuLite Studio user workflows before release.

## Launch

- Launch `python main.py` (no crash on startup).
- Verify window renders correctly at 100% and 125% DPI.

## Data Loading

- Open a CSV file via `文件 -> 打开文件`.
- Drag-and-drop a CSV file onto the window.
- Verify the dataset badges update (rows/columns/missing).
- Verify `最近文件` menu and command-bar quick entries update.

## Table

- Use global table search (`Ctrl+F`), type a keyword, confirm filtered row count changes.
- Clear search and confirm rows return.
- Sort by clicking a numeric column header.

## Preprocess + History

- Slice first N rows.
- Convert a column type (e.g. `int` -> `string`).
- Apply a text filter and numeric range filter.
- Fill missing values (mean/median/zero/ffill/bfill).
- Use `Ctrl+Z` / `Ctrl+Y` to undo/redo data changes; confirm table and stats update.

## Chart

- Pick X column and one or more Y columns.
- Click `更新图表` in the sidebar fixed action dock.
- Switch chart type (line/bar/scatter/histogram/boxplot/heatmap).
- Toggle legend/grid.

## Export

- Export chart to PNG and verify the file opens.
- Verify "打开文件" and "打开文件夹" actions work in the success dialog.

## Layout

- Toggle sidebar (`Ctrl+B`) and confirm it fully collapses/restores without clipping.
- Toggle chart focus mode (`Ctrl+2`) and restore balanced view (`Ctrl+1`).

