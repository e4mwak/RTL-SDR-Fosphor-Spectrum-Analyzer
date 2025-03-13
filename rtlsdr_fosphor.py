#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RTL-SDR Fosphor Spectrum Analyzer

This script provides a complete solution for running gr-fosphor with RTL-SDR devices.
It properly sets up the environment to ensure all dependencies are found.
"""

import os
import sys
import signal
import argparse
import traceback

# Add DLL directories to PATH before importing any other modules
def setup_dll_paths():
    # Add conda library bin directory to PATH for GLEW and GLFW
    conda_lib_bin = os.path.join(os.path.dirname(sys.executable), 'Library', 'bin')
    if os.path.exists(conda_lib_bin) and conda_lib_bin not in os.environ.get('PATH', '').split(os.pathsep):
        os.environ['PATH'] = conda_lib_bin + os.pathsep + os.environ.get('PATH', '')
        print(f"Added {conda_lib_bin} to PATH")
    
    # Add conda DLLs directory to PATH
    conda_dlls = os.path.join(os.path.dirname(sys.executable), 'DLLs')
    if os.path.exists(conda_dlls) and conda_dlls not in os.environ.get('PATH', '').split(os.pathsep):
        os.environ['PATH'] = conda_dlls + os.pathsep + os.environ.get('PATH', '')
        print(f"Added {conda_dlls} to PATH")
    
    # Add gr-fosphor lib directory to PATH if it exists
    gr_fosphor_lib = os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages', 'gnuradio', 'fosphor')
    if os.path.exists(gr_fosphor_lib) and gr_fosphor_lib not in os.environ.get('PATH', '').split(os.pathsep):
        os.environ['PATH'] = gr_fosphor_lib + os.pathsep + os.environ.get('PATH', '')
        print(f"Added {gr_fosphor_lib} to PATH")
    
    # Add conda Library/lib directory to PATH for additional DLLs
    conda_lib = os.path.join(os.path.dirname(sys.executable), 'Library', 'lib')
    if os.path.exists(conda_lib) and conda_lib not in os.environ.get('PATH', '').split(os.pathsep):
        os.environ['PATH'] = conda_lib + os.pathsep + os.environ.get('PATH', '')
        print(f"Added {conda_lib} to PATH")

# Setup DLL paths before importing any other modules
setup_dll_paths()

# Now try to import the required modules
try:
    from gnuradio import gr
    from gnuradio import blocks
    from gnuradio.filter import firdes
    from gnuradio.fft import window
    from PyQt5 import QtGui, QtCore, QtWidgets
    import sip
    import numpy as np
    
    # Try to import the fosphor module
    try:
        from gnuradio import fosphor
        print("Successfully imported fosphor module!")
        use_fosphor = True
    except ImportError as e:
        print(f"Error importing fosphor module: {e}")
        print("Falling back to standard GNU Radio blocks...")
        from gnuradio import qtgui
        use_fosphor = False
    except Exception as e:
        print(f"Unexpected error importing fosphor module: {e}")
        traceback.print_exc()
        print("Falling back to standard GNU Radio blocks...")
        from gnuradio import qtgui
        use_fosphor = False
    
    # Try to import the osmosdr module
    try:
        from osmosdr import source
        print("Successfully imported osmosdr module!")
    except ImportError as e:
        print(f"Error importing osmosdr module: {e}")
        print("Make sure gr-osmosdr is properly installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error importing osmosdr module: {e}")
        traceback.print_exc()
        sys.exit(1)
    
except Exception as e:
    print(f"Error importing required modules: {e}")
    traceback.print_exc()
    sys.exit(1)

# Function to detect available RTL-SDR devices
def detect_rtlsdr_devices():
    print("\nDetecting RTL-SDR devices...")
    devices = []
    
    for i in range(10):  # Try up to 10 potential devices
        try:
            # Create a temporary source to check if device exists
            src = source(args=f"rtl={i}")
            # Some versions of gr-osmosdr don't have get_device_name
            device_name = f"RTL-SDR #{i}"
            print(f"  Found device #{i}: {device_name}")
            devices.append((i, device_name))
            del src  # Clean up the source
        except Exception as e:
            if "Failed to open rtlsdr device" in str(e):
                # No more devices available
                if i == 0:
                    print("  No RTL-SDR devices found")
                break
            else:
                print(f"  Error checking device #{i}: {e}")
    
    return devices

# Main flowgraph class
class RtlsdrFosphor(gr.top_block):
    def __init__(self, center_freq=100e6, sample_rate=2e6, gain=20, device_index=0):
        gr.top_block.__init__(self, "RTL-SDR Fosphor Spectrum Analyzer")

        # Variables
        self.samp_rate = sample_rate
        self.center_freq = center_freq
        self.gain = gain
        self.device_index = device_index

        # Create the GUI application
        self.app = QtWidgets.QApplication.instance()
        if self.app is None:
            self.app = QtWidgets.QApplication(sys.argv)

        # Create the main window
        self.main_window = QtWidgets.QWidget()
        self.main_window.setWindowTitle("RTL-SDR Fosphor Spectrum Analyzer")
        self.main_window.resize(1200, 800)
        self.main_layout = QtWidgets.QVBoxLayout(self.main_window)

        # Create the RTL-SDR source
        print(f"\nCreating RTL-SDR source with device #{self.device_index}...")
        try:
            self.rtlsdr_source = source(args=f"rtl={self.device_index}")
            self.rtlsdr_source.set_sample_rate(self.samp_rate)
            self.rtlsdr_source.set_center_freq(self.center_freq)
            self.rtlsdr_source.set_freq_corr(0)
            self.rtlsdr_source.set_gain(self.gain)
            self.rtlsdr_source.set_if_gain(20)
            self.rtlsdr_source.set_bb_gain(20)
            self.rtlsdr_source.set_antenna('')
            self.rtlsdr_source.set_bandwidth(0)
            
            print(f"Using RTL-SDR device #{self.device_index}")
            # Try to get tuner type, but don't fail if it's not available
            try:
                if hasattr(self.rtlsdr_source, 'get_tuner_type'):
                    print(f"Tuner type: {self.rtlsdr_source.get_tuner_type()}")
            except:
                pass
        except Exception as e:
            print(f"Error creating RTL-SDR source: {e}")
            traceback.print_exc()
            sys.exit(1)

        # Create visualization based on availability
        if use_fosphor:
            self.setup_fosphor_visualization()
        else:
            self.setup_standard_visualization()

        # Show the main window
        self.main_window.show()
        print("Flowgraph connected successfully")

    def setup_fosphor_visualization(self):
        print("\nSetting up Fosphor visualization...")
        try:
            # Try QT sink first
            self.fosphor_sink = fosphor.qt_sink_c()
            self.fosphor_sink.set_frequency_range(self.center_freq, self.samp_rate)
            self.fosphor_win = sip.wrapinstance(self.fosphor_sink.qwidget(), QtWidgets.QWidget)
            self.main_layout.addWidget(self.fosphor_win)
            self.connect(self.rtlsdr_source, self.fosphor_sink)
            print("Using Fosphor QT sink for visualization")
        except Exception as e:
            print(f"Could not create Fosphor QT sink: {e}")
            traceback.print_exc()
            
            # Try GLFW sink as fallback
            try:
                print("Trying Fosphor GLFW sink as fallback...")
                self.fosphor_sink = fosphor.glfw_sink_c()
                self.fosphor_sink.set_frequency_range(self.center_freq, self.samp_rate)
                print("Using Fosphor GLFW Sink")
                self.connect(self.rtlsdr_source, self.fosphor_sink)
            except Exception as e:
                print(f"Could not create Fosphor GLFW sink: {e}")
                traceback.print_exc()
                print("Falling back to standard visualization...")
                self.setup_standard_visualization()

    def setup_standard_visualization(self):
        print("\nSetting up standard GNU Radio visualization...")
        try:
            # Import qtgui if not already imported
            if 'qtgui' not in sys.modules:
                from gnuradio import qtgui
                
            # Create frequency sink (FFT display)
            self.qtgui_freq_sink = qtgui.freq_sink_c(
                2048,  # FFT size
                window.WIN_BLACKMAN_hARRIS,  # Window type
                self.center_freq,  # Center frequency
                self.samp_rate,  # Bandwidth
                "RTL-SDR Spectrum",  # Title
                1,  # Number of inputs
            )
            self.qtgui_freq_sink.set_update_time(0.05)  # Faster updates
            self.qtgui_freq_sink.set_y_axis(-140, 10)
            self.qtgui_freq_sink.set_y_label('Relative Gain', 'dB')
            self.qtgui_freq_sink.enable_autoscale(False)
            self.qtgui_freq_sink.enable_grid(True)
            self.qtgui_freq_sink.set_fft_average(0.2)  # Some averaging for smoother display
            self.qtgui_freq_sink.enable_axis_labels(True)
            self.qtgui_freq_sink.enable_control_panel(True)

            # Create waterfall sink
            self.qtgui_waterfall_sink = qtgui.waterfall_sink_c(
                2048,  # FFT size
                window.WIN_BLACKMAN_hARRIS,  # Window type
                self.center_freq,  # Center frequency
                self.samp_rate,  # Bandwidth
                "RTL-SDR Waterfall",  # Title
                1,  # Number of inputs
            )
            self.qtgui_waterfall_sink.set_update_time(0.05)  # Faster updates
            self.qtgui_waterfall_sink.enable_grid(True)
            self.qtgui_waterfall_sink.enable_axis_labels(True)
            self.qtgui_waterfall_sink.set_intensity_range(-140, 10)

            # Add widgets to layout
            self._qtgui_freq_sink_win = sip.wrapinstance(self.qtgui_freq_sink.qwidget(), QtWidgets.QWidget)
            self._qtgui_waterfall_sink_win = sip.wrapinstance(self.qtgui_waterfall_sink.qwidget(), QtWidgets.QWidget)

            self.main_layout.addWidget(self._qtgui_freq_sink_win)
            self.main_layout.addWidget(self._qtgui_waterfall_sink_win)

            # Connect blocks
            self.connect(self.rtlsdr_source, self.qtgui_freq_sink)
            self.connect(self.rtlsdr_source, self.qtgui_waterfall_sink)

            print("Standard visualization setup complete")
        except Exception as e:
            print(f"Error setting up standard visualization: {e}")
            traceback.print_exc()
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='RTL-SDR Fosphor Spectrum Analyzer')
    parser.add_argument('-f', '--freq', type=float, default=100e6,
                        help='Center frequency in Hz (default: 100e6)')
    parser.add_argument('-s', '--samp-rate', type=float, default=2e6,
                        help='Sample rate in Hz (default: 2e6)')
    parser.add_argument('-g', '--gain', type=float, default=20,
                        help='RF gain in dB (default: 20)')
    parser.add_argument('-d', '--device', type=int, default=0,
                        help='RTL-SDR device index (default: 0)')
    parser.add_argument('--detect', action='store_true',
                        help='Detect available RTL-SDR devices and exit')
    args = parser.parse_args()
    
    # Detect RTL-SDR devices if requested
    if args.detect:
        devices = detect_rtlsdr_devices()
        if devices:
            print(f"\nFound {len(devices)} RTL-SDR device(s):")
            for idx, name in devices:
                print(f"  Device #{idx}: {name}")
            print("\nTo use a specific device, run with the -d/--device option.")
        sys.exit(0)
    
    # Create flowgraph
    tb = RtlsdrFosphor(
        center_freq=args.freq,
        sample_rate=args.samp_rate,
        gain=args.gain,
        device_index=args.device
    )
    
    # Set up signal handlers
    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    
    # Start flowgraph
    print(f"\nStarting RTL-SDR{' Fosphor' if use_fosphor else ''} Spectrum Analyzer with:")
    print(f"  Device Index: {args.device}")
    print(f"  Center Frequency: {args.freq/1e6:.3f} MHz")
    print(f"  Sample Rate: {args.samp_rate/1e6:.3f} MHz")
    print(f"  Gain: {args.gain} dB")
    print("Press Ctrl+C to exit")
    
    tb.start()
    tb.app.exec_()
    sig_handler()

if __name__ == '__main__':
    main()
