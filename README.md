# RTL-SDR Fosphor Spectrum Analyzer

A complete, ready-to-use implementation of a spectrum analyzer using RTL-SDR devices with gr-fosphor waterfall display.



## Overview

This project provides a Python-based application that combines:
- RTL-SDR hardware support via gr-osmosdr
- The powerful gr-fosphor OpenCL-accelerated spectrum visualization 
- A simple, user-friendly interface with automatic fallbacks
- Proper environment setup to ensure all dependencies are found

The application offers:
- Real-time spectrum analysis with waterfall display
- Automatic RTL-SDR device detection
- Configurable frequency, sample rate, and gain settings
- Fallback to standard GNU Radio visualization if gr-fosphor is unavailable

## Features

- **OpenCL-accelerated display** using gr-fosphor for fluid visualization
- **Automatic device detection** to find connected RTL-SDR devices
- **Graceful fallbacks** if gr-fosphor or OpenCL is unavailable
- **Command-line interface** for easy configuration
- **Path management** to properly locate DLLs and dependencies

## Installation

### Pre-built Executable (Windows)

For Windows users, a pre-built executable see below

### From Source

1. Ensure you have GNU Radio with gr-osmosdr installed
2. Install gr-fosphor (optional but recommended)
3. Clone this repository:
   ```
   git clone https://github.com/e4mwak/RTL-SDR-Fosphor-Spectrum-Analyzer.git
   cd RTL-SDR-Fosphor-Spectrum-Analyzer
   ```
4. Run the application:
   ```
   python rtlsdr_fosphor.py
   ```

## Usage

### Basic Usage

```
python rtlsdr_fosphor.py
```

This starts the application with default settings (100 MHz center frequency, 2 MHz sample rate).

### Command Line Options

```
python rtlsdr_fosphor.py [-h] [-f FREQ] [-s SAMP_RATE] [-g GAIN] [-d DEVICE] [--detect]
```

- `-f`, `--freq`: Center frequency in Hz (default: 100e6)
- `-s`, `--samp-rate`: Sample rate in Hz (default: 2e6)
- `-g`, `--gain`: RF gain in dB (default: 20)
- `-d`, `--device`: RTL-SDR device index (default: 0)
- `--detect`: Detect available RTL-SDR devices and exit

### Examples

Tune to FM broadcast band:
```
python rtlsdr_fosphor.py -f 95.7e6
```

Use a higher sample rate:
```
python rtlsdr_fosphor.py -f 915e6 -s 2.4e6
```

Set a specific gain:
```
python rtlsdr_fosphor.py -f 145e6 -g 35
```

Use a specific RTL-SDR device (if you have multiple):
```
python rtlsdr_fosphor.py -d 1
```

## Requirements

- Python 3.x
- GNU Radio
- gr-osmosdr
- gr-fosphor (optional, but recommended)
- PyQt5
- RTL-SDR hardware

## Building the Executable

The executable was built using PyInstaller:

```
pyinstaller --onefile --noconsole rtlsdr_fosphor.py
```

## Troubleshooting

### No RTL-SDR Devices Found

1. Check that your RTL-SDR device is properly connected
2. Ensure the RTL-SDR drivers are installed
3. Try running with `--detect` flag to scan for devices

### Fosphor Not Working

1. Ensure you have OpenCL installed and functioning
2. Check that gr-fosphor is properly installed
3. The application will automatically fall back to standard GNU Radio visualization

### DLL Errors

The application attempts to manage paths to DLLs automatically, but if you encounter DLL-related issues:

1. Ensure GNU Radio, gr-osmosdr, and gr-fosphor are properly installed
2. Check your PATH environment variable includes the necessary directories

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details. This is derived from the [gr-fosphor](https://github.com/osmocom/gr-fosphor) project, which is also licensed under GPLv3.

## Acknowledgments

- [gr-fosphor](https://github.com/osmocom/gr-fosphor) for the OpenCL-accelerated spectrum visualization
- [GNU Radio](https://www.gnuradio.org/) for the software-defined radio framework
- [RTL-SDR](https://www.rtl-sdr.com/) for the affordable SDR hardware
- [gr-osmosdr](https://github.com/osmocom/gr-osmosdr) for the hardware support
