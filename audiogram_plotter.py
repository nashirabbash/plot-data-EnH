#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# @file audiogram_plotter.py
# @brief Unified audiogram plotter for Elbicare and Pychoacoustics data
# @brief Supports dBA (Elbicare) and dB HL (Pychoacoustics) plotting

import os
import sys
import json
import re
import numpy as np
import matplotlib.pyplot as mplt
from matplotlib.offsetbox import AnchoredText as antext
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWidgets import QLabel, QFileDialog, QMessageBox

class AudiogramPlotter:
    def __init__(self):
        # RETSPL values from IEC 60318 (Table 2) for Pychoacoustics
        self.RETSPL = {
            125: 45.0,
            250: 27.0,
            500: 13.5,
            1000: 7.5,
            2000: 9.0,
            4000: 12.0,
            8000: 15.5
        }
        
        # Calibration file path for Elbicare (support PyInstaller frozen mode)
        def resource_path(relative_path):
            """Get absolute path to resource, works for dev and PyInstaller"""
            if getattr(sys, 'frozen', False):
                # Running in PyInstaller bundle
                base_path = sys._MEIPASS
            else:
                # Running in normal Python environment
                base_path = os.path.dirname(__file__)
            return os.path.join(base_path, relative_path)
        
        self.calib_file = resource_path("calib.json")
        
        # GUI setup
        self.app = None
        self.win = None
        
    def init_gui(self):
        """Initialize main GUI"""
        self.app = QApplication(sys.argv)
        
        self.win = QWidget()
        self.win.resize(350, 200)
        self.win.setWindowTitle("Audiogram Plotter - Enhanced")
        
        # Title label
        self.lbl_title = QLabel("Select Audiogram Data Type:", self.win)
        self.lbl_title.move(20, 20)
        self.lbl_title.resize(310, 30)
        self.lbl_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        # Button 1: Plot Elbicare
        self.btn_elbicare = QPushButton("Plot Elbicare", self.win)
        self.btn_elbicare.setToolTip("Load HT_*.TXT file (Elbicare format with amplitude data)")
        self.btn_elbicare.move(50, 70)
        self.btn_elbicare.resize(250, 40)
        self.btn_elbicare.setStyleSheet("font-size: 12px;")
        self.btn_elbicare.clicked.connect(self.load_elbicare)
        
        # Button 2: Plot Pychoacoustics
        self.btn_pyco = QPushButton("Plot Pyco Acoustic", self.win)
        self.btn_pyco.setToolTip("Load pychoacoustics TXT file (turnpointMean format)")
        self.btn_pyco.move(50, 120)
        self.btn_pyco.resize(250, 40)
        self.btn_pyco.setStyleSheet("font-size: 12px;")
        self.btn_pyco.clicked.connect(self.load_pychoacoustics)
        
        # Button: About
        self.btn_about = QPushButton("About", self.win)
        self.btn_about.setToolTip("Show information")
        self.btn_about.move(260, 10)
        self.btn_about.resize(70, 25)
        self.btn_about.clicked.connect(self.show_about)
    
    def load_elbicare(self):
        """Load and plot Elbicare TXT file"""
        opts = QFileDialog.Options()
        opts |= QFileDialog.DontUseNativeDialog
        fname, _ = QFileDialog.getOpenFileName(
            None,
            "Load Elbicare Data (HT_*.TXT)",
            "",
            "Text Files (*.txt *.TXT);;All Files (*)",
            options=opts
        )
        
        if fname:
            try:
                # Check if calibration file exists
                if not os.path.exists(self.calib_file):
                    QMessageBox.critical(
                        self.win,
                        "Calibration Error",
                        f"Calibration file not found:\n{self.calib_file}\n\n" +
                        "Please ensure calib_example.json is in the same folder."
                    )
                    return
                
                # Load calibration
                calib_data = self.load_json(self.calib_file)
                
                # Load Elbicare data
                elbi_data = self.load_json(fname)
                
                # Plot
                self.plot_elbicare(elbi_data, calib_data, fname)
                
            except Exception as e:
                QMessageBox.critical(
                    self.win,
                    "Error",
                    f"Failed to load or plot Elbicare data:\n{str(e)}"
                )
    
    def load_pychoacoustics(self):
        """Load and plot Pychoacoustics TXT file"""
        opts = QFileDialog.Options()
        opts |= QFileDialog.DontUseNativeDialog
        fname, _ = QFileDialog.getOpenFileName(
            None,
            "Load Pychoacoustics Data",
            "",
            "Text Files (*.txt *.TXT);;All Files (*)",
            options=opts
        )
        
        if fname:
            try:
                # Parse TXT file
                pyco_data = self.parse_pychoacoustics_txt(fname)
                
                # Plot
                self.plot_pychoacoustics(pyco_data, fname)
                
            except Exception as e:
                QMessageBox.critical(
                    self.win,
                    "Error",
                    f"Failed to load or plot Pychoacoustics data:\n{str(e)}"
                )
    
    def load_json(self, filename):
        """Load JSON file"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def parse_pychoacoustics_txt(self, filename):
        """Parse pychoacoustics TXT file and extract audiogram data"""
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        blocks = content.split('*******************************************************')
        
        audiogram_data = {
            "ch_0": {},  # Left ear
            "ch_1": {}   # Right ear
        }
        
        freq_hz_to_index = {
            125: 0, 250: 1, 500: 2, 1000: 3,
            2000: 4, 4000: 5, 8000: 6
        }
        
        for block in blocks:
            if not block.strip():
                continue
            
            ear_match = re.search(r'Ear:\s+(Left|Right)', block)
            if not ear_match:
                continue
            ear = ear_match.group(1)
            channel = "ch_0" if ear == "Left" else "ch_1"
            
            freq_match = re.search(r'Frequency \(Hz\):\s+(\d+)', block)
            if not freq_match:
                continue
            frequency = int(freq_match.group(1))
            
            turnpoint_match = re.search(r'turnpointMean\s+=\s+([\d.]+)', block)
            if not turnpoint_match:
                continue
            dbspl = float(turnpoint_match.group(1))
            
            if frequency in freq_hz_to_index:
                freq_idx = freq_hz_to_index[frequency]
                freq_key = f"freq_{freq_idx}"
                
                audiogram_data[channel][freq_key] = {
                    "freq_hz": frequency,
                    "dbSPL": dbspl
                }
        
        return {"audiogram": audiogram_data}
    
    def plot_elbicare(self, elbi_data, calib_data, filename):
        """Plot Elbicare data with calibration"""
        # Elbicare records test frequencies (0.625-20 kHz) but they correspond to
        # standard audiogram frequencies (250-8000 Hz)
        # The freq values in TXT are just labels, actual test is for standard freqs
        # freq_0: labeled 0.625 kHz → standard audiogram 250 Hz
        # freq_1: labeled 1.250 kHz → standard audiogram 500 Hz  
        # freq_2: labeled 2.500 kHz → standard audiogram 1000 Hz
        # freq_3: labeled 5.000 kHz → standard audiogram 2000 Hz
        # freq_4: labeled 10.000 kHz → standard audiogram 4000 Hz
        # freq_5: labeled 20.000 kHz → standard audiogram 8000 Hz
        
        elbi_freq_map = {
            0: (0.625, "250Hz", 250),   # Standard 250 Hz test
            1: (1.250, "500Hz", 500),   # Standard 500 Hz test
            2: (2.500, "1000Hz", 1000), # Standard 1000 Hz test
            3: (5.000, "2000Hz", 2000), # Standard 2000 Hz test
            4: (10.000, "4000Hz", 4000),# Standard 4000 Hz test
            5: (20.000, "8000Hz", 8000) # Standard 8000 Hz test
        }
        
        freq_list = []
        dbL = []
        dbR = []
        
        for idx in range(6):
            freq_key = f"freq_{idx}"
            
            if freq_key in elbi_data["audiogram"]["ch_0"]:
                freq_khz, calib_key, plot_freq = elbi_freq_map[idx]
                freq_list.append(plot_freq)
                
                # Left ear (ch_0)
                ampl_L = int(elbi_data["audiogram"]["ch_0"][freq_key]["ampl"])
                db_L = calib_data[calib_key][ampl_L] if ampl_L < len(calib_data[calib_key]) else 0
                dbL.append(db_L)
                
                # Right ear (ch_1)
                ampl_R = int(elbi_data["audiogram"]["ch_1"][freq_key]["ampl"])
                db_R = calib_data[calib_key][ampl_R] if ampl_R < len(calib_data[calib_key]) else 0
                dbR.append(db_R)
        
        # Calculate PTA (500, 1000, 2000, 4000 Hz = indices 1,2,3,4)
        if len(dbL) >= 5 and len(dbR) >= 5:
            pta_L = (dbL[1] + dbL[2] + dbL[3] + dbL[4]) / 4
            pta_R = (dbR[1] + dbR[2] + dbR[3] + dbR[4]) / 4
        else:
            pta_L = sum(dbL) / len(dbL) if dbL else 0
            pta_R = sum(dbR) / len(dbR) if dbR else 0
        
        # Plot
        mplt.close()
        fig, ax = mplt.subplots(figsize=(10, 6))
        
        # Plot Left Ear
        ax.plot(freq_list, dbL, '-', color='r', 
                marker='o', markersize=8, linewidth=2, label='Left Ear')
        for freq, db in zip(freq_list, dbL):
            ax.text(freq, db + 3, f'{db:.1f}', 
                   fontsize=8, ha='center', color='red')
        
        # Plot Right Ear
        ax.plot(freq_list, dbR, '--', color='b', 
                marker='x', markersize=8, linewidth=2, label='Right Ear')
        for freq, db in zip(freq_list, dbR):
            ax.text(freq, db - 4, f'{db:.1f}', 
                   fontsize=8, ha='center', color='blue')
        
        # Formatting
        ax.set_xscale('log')
        ax.set_xlabel('Frequency (Hz)', fontsize=12, fontweight='bold')
        ax.set_ylabel(f"Sound Level ({calib_data['audio_unit']})", fontsize=12, fontweight='bold')
        
        # Standard X-axis (125 to 8000 Hz - standar untuk semua plot)
        ax.set_xlim(100, 10000)
        ax.set_xticks([125, 250, 500, 1000, 2000, 4000, 8000])
        ax.set_xticklabels(['125', '250', '500', '1000', '2000', '4000', '8000'])
        
        # Y-axis (inverted: -20 di atas, 160 di bawah - standar audiogram)
        ax.set_ylim(160, -20)
        ax.set_yticks(np.arange(-20, 161, 10))
        ax.grid(True, which='both', linestyle='--', alpha=0.6)
        
        # Title
        short_name = Path(filename).name
        calib_text = f"CALIBRATION: {calib_data['headphone']} by {calib_data['author']} at {calib_data['tanggal']}"
        ax.set_title(f'Elbicare Audiogram: {short_name}\n{calib_text}', 
                    fontsize=10, pad=20)
        
        ax.legend(loc='upper right', fontsize=10)
        
        # PTA info
        pta_text = f"PTA Left: {pta_L:.1f} {calib_data['audio_unit']}\nPTA Right: {pta_R:.1f} {calib_data['audio_unit']}"
        pta_info = antext(pta_text, loc='lower left', 
                         prop=dict(size=9), frameon=True)
        ax.add_artist(pta_info)
        
        mplt.tight_layout()
        mplt.show()
        
        # Console output
        print("\n" + "="*60)
        print(f"ELBICARE AUDIOGRAM ({calib_data['audio_unit']})")
        print("="*60)
        print(f"{'Freq (Hz)':<12} {'Left Ear':<15} {'Right Ear':<15}")
        print("-"*60)
        for i, freq in enumerate(freq_list):
            print(f"{freq:<12} {dbL[i]:>10.2f} {calib_data['audio_unit']:<5} {dbR[i]:>10.2f} {calib_data['audio_unit']}")
        print("="*60)
        print(f"\nPTA Left:  {pta_L:.2f} {calib_data['audio_unit']}")
        print(f"PTA Right: {pta_R:.2f} {calib_data['audio_unit']}")
        print("="*60 + "\n")
    
    def plot_pychoacoustics(self, pyco_data, filename):
        """Plot Pychoacoustics data with RETSPL conversion to dB HL"""
        freq_list = [125, 250, 500, 1000, 2000, 4000, 8000]
        dbhl_left = []
        dbhl_right = []
        
        for i in range(7):
            freq_key = f"freq_{i}"
            
            if freq_key in pyco_data["audiogram"]["ch_0"]:
                # Left ear
                freq_hz = pyco_data["audiogram"]["ch_0"][freq_key]["freq_hz"]
                dbspl_L = pyco_data["audiogram"]["ch_0"][freq_key]["dbSPL"]
                dbhl_L = dbspl_L - self.RETSPL[freq_hz]
                dbhl_left.append(dbhl_L)
                
                # Right ear
                dbspl_R = pyco_data["audiogram"]["ch_1"][freq_key]["dbSPL"]
                dbhl_R = dbspl_R - self.RETSPL[freq_hz]
                dbhl_right.append(dbhl_R)
            else:
                dbhl_left.append(None)
                dbhl_right.append(None)
        
        # Remove None values
        valid_freq = [f for f, d in zip(freq_list, dbhl_left) if d is not None]
        valid_dbhl_L = [d for d in dbhl_left if d is not None]
        valid_dbhl_R = [d for d in dbhl_right if d is not None]
        
        # Calculate PTA (indices for 500, 1000, 2000, 4000 Hz = 2,3,4,5)
        if len(valid_dbhl_L) >= 6:
            pta_L = (valid_dbhl_L[2] + valid_dbhl_L[3] + valid_dbhl_L[4] + valid_dbhl_L[5]) / 4
            pta_R = (valid_dbhl_R[2] + valid_dbhl_R[3] + valid_dbhl_R[4] + valid_dbhl_R[5]) / 4
        else:
            pta_L = sum(valid_dbhl_L) / len(valid_dbhl_L) if valid_dbhl_L else 0
            pta_R = sum(valid_dbhl_R) / len(valid_dbhl_R) if valid_dbhl_R else 0
        
        # Plot
        mplt.close()
        fig, ax = mplt.subplots(figsize=(10, 6))
        
        # Plot Left Ear
        ax.plot(valid_freq, valid_dbhl_L, '-', color='r', 
                marker='o', markersize=8, linewidth=2, label='Left Ear')
        for freq, dbhl in zip(valid_freq, valid_dbhl_L):
            ax.text(freq, dbhl + 3, f'{dbhl:.1f}', 
                   fontsize=8, ha='center', color='red')
        
        # Plot Right Ear
        ax.plot(valid_freq, valid_dbhl_R, '--', color='b', 
                marker='x', markersize=8, linewidth=2, label='Right Ear')
        for freq, dbhl in zip(valid_freq, valid_dbhl_R):
            ax.text(freq, dbhl - 4, f'{dbhl:.1f}', 
                   fontsize=8, ha='center', color='blue')
        
        # Formatting
        ax.set_xscale('log')
        ax.set_xlabel('Frequency (Hz)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Hearing Level (dB HL)', fontsize=12, fontweight='bold')
        
        # Standard X-axis (125 to 8000 Hz - standar untuk semua plot)
        ax.set_xlim(100, 10000)
        ax.set_xticks([125, 250, 500, 1000, 2000, 4000, 8000])
        ax.set_xticklabels(['125', '250', '500', '1000', '2000', '4000', '8000'])
        
        # Y-axis (inverted: -20 di atas, 160 di bawah - standar audiogram)
        ax.set_ylim(160, -20)
        ax.set_yticks(np.arange(-20, 161, 10))
        ax.grid(True, which='both', linestyle='--', alpha=0.6)
        
        # Title
        short_name = Path(filename).name
        ax.set_title(f'Pychoacoustics Audiogram: {short_name}\nConverted from dB SPL to dB HL using RETSPL (IEC 60318)', 
                    fontsize=10, pad=20)
        
        ax.legend(loc='upper right', fontsize=10)
        
        # PTA info
        pta_text = f"PTA Left: {pta_L:.1f} dB HL\nPTA Right: {pta_R:.1f} dB HL"
        pta_info = antext(pta_text, loc='lower left', 
                         prop=dict(size=9), frameon=True)
        ax.add_artist(pta_info)
        
        # Conversion info
        info_text = "Conversion: dB HL = dB SPL - RETSPL"
        info_box = antext(info_text, loc='lower right', 
                         prop=dict(size=8, style='italic'), frameon=True)
        ax.add_artist(info_box)
        
        mplt.tight_layout()
        mplt.show()
        
        # Console output
        print("\n" + "="*60)
        print("PYCHOACOUSTICS AUDIOGRAM (dB HL)")
        print("="*60)
        print(f"{'Freq (Hz)':<12} {'Left Ear':<15} {'Right Ear':<15}")
        print("-"*60)
        for i, freq in enumerate(valid_freq):
            print(f"{freq:<12} {valid_dbhl_L[i]:>10.2f} dB HL {valid_dbhl_R[i]:>10.2f} dB HL")
        print("="*60)
        print(f"\nPTA Left:  {pta_L:.2f} dB HL")
        print(f"PTA Right: {pta_R:.2f} dB HL")
        print("="*60 + "\n")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.information(
            self.win,
            "About Audiogram Plotter",
            "Audiogram Plotter - Enhanced Version\n\n" +
            "Features:\n" +
            "• Plot Elbicare data (HT_*.TXT format)\n" +
            "  - Uses calibration file for dBA conversion\n" +
            "  - Frequency range: 625 Hz - 20 kHz\n\n" +
            "• Plot Pychoacoustics data\n" +
            "  - Converts dB SPL to dB HL using RETSPL\n" +
            "  - Standard audiogram: 125 Hz - 8 kHz\n\n" +
            "Both plots use Y-axis range: -20 to 160 dB\n\n" +
            "Version: 2.0"
        )
    
    def gui_run(self):
        """Run the GUI application"""
        self.init_gui()
        self.win.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    plotter = AudiogramPlotter()
    plotter.gui_run()
