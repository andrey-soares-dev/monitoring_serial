

## Generate Exe

```bash
pyinstaller --noconfirm --onefile --windowed --collect-all matplotlib --add-data "graphic.py;." --add-data "test_control.py;." main.py
```