"""PyInstaller hook override for openpyxl.

Some environments intermittently expose transient '*.ldtmp' files in the
openpyxl package directory. PyInstaller treats these as data files and fails
if the transient file disappears mid-build.

We defensively exclude '*.ldtmp' to keep packaging stable.
"""

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("openpyxl", excludes=["**/*.ldtmp"])

