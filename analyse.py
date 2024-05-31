import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from time import gmtime, strftime

LOG_DIR = "logs/"
PLOT_DIR = "plots/"

class QRSDetectorOffline(object):
    def __init__(self, ecg_data_path, verbose=True, log_data=False, plot_data=False, show_plot=False):
        self.ecg_data_path = ecg_data_path
        self.signal_frequency = 100  # Assuming data is sampled at 100 Hz
        self.integration_window = 15  # Change proportionally when adjusting frequency (in samples)
        self.findpeaks_limit = 0.35
        self.findpeaks_spacing = 50  # Change proportionally when adjusting frequency (in samples)
        self.refractory_period = 120  # Change proportionally when adjusting frequency (in samples)
        self.qrs_peak_filtering_factor = 0.125
        self.noise_peak_filtering_factor = 0.125
        self.qrs_noise_diff_weight = 0.25
        self.ecg_data_raw = None
        self.detected_peaks_indices = None
        self.detected_peaks_values = None
        self.qrs_peak_value = 0.0
        self.noise_peak_value = 0.0
        self.threshold_value = 0.0
        self.qrs_peaks_indices = np.array([], dtype=int)
        self.noise_peaks_indices = np.array([], dtype=int)
        self.ecg_data_detected = None
        self.rr_intervals = None
        self.load_ecg_data()
        self.detect_peaks()
        self.detect_qrs()
        if verbose:
            self.print_detection_data()
        if log_data:
            if not os.path.exists(LOG_DIR):
                os.makedirs(LOG_DIR)
            self.log_path = "{:s}QRS_offline_detector_log_{:s}.csv".format(LOG_DIR,
                                                                           strftime("%Y_%m_%d_%H_%M_%S", gmtime()))
            self.log_detection_data()
        if plot_data:
            if not os.path.exists(PLOT_DIR):
                os.makedirs(PLOT_DIR)
            self.plot_path = "{:s}QRS_offline_detector_plot_{:s}.png".format(PLOT_DIR,
                                                                             strftime("%Y_%m_%d_%H_%M_%S", gmtime()))
            self.plot_detection_data(show_plot=show_plot)

    def load_ecg_data(self):
        self.ecg_data_raw = np.loadtxt(self.ecg_data_path, skiprows=1, delimiter=',')

    def detect_peaks(self):
        ecg_measurements = self.ecg_data_raw[:, 1]
        
        # Use scipy's find_peaks to detect peaks
        self.detected_peaks_indices, _ = find_peaks(ecg_measurements, height=self.findpeaks_limit, distance=self.findpeaks_spacing)
        self.detected_peaks_values = ecg_measurements[self.detected_peaks_indices]

    def detect_qrs(self):
        for detected_peak_index, detected_peaks_value in zip(self.detected_peaks_indices, self.detected_peaks_values):
            try:
                last_qrs_index = self.qrs_peaks_indices[-1]
            except IndexError:
                last_qrs_index = 0
            if detected_peak_index - last_qrs_index > self.refractory_period or not self.qrs_peaks_indices.size:
                if detected_peaks_value > self.threshold_value:
                    self.qrs_peaks_indices = np.append(self.qrs_peaks_indices, detected_peak_index)
                    self.qrs_peak_value = self.qrs_peak_filtering_factor * detected_peaks_value + \
                                          (1 - self.qrs_peak_filtering_factor) * self.qrs_peak_value
                else:
                    self.noise_peaks_indices = np.append(self.noise_peaks_indices, detected_peak_index)
                    self.noise_peak_value = self.noise_peak_filtering_factor * detected_peaks_value + \
                                            (1 - self.noise_peak_filtering_factor) * self.noise_peak_value
                self.threshold_value = self.noise_peak_value + \
                                       self.qrs_noise_diff_weight * (self.qrs_peak_value - self.noise_peak_value)
        self.rr_intervals = np.diff(self.qrs_peaks_indices) / self.signal_frequency * 1000  # Convert to ms
        measurement_qrs_detection_flag = np.zeros([len(self.ecg_data_raw[:, 1]), 1])
        measurement_qrs_detection_flag[self.qrs_peaks_indices] = 1
        self.ecg_data_detected = np.append(self.ecg_data_raw, measurement_qrs_detection_flag, 1)

    def print_detection_data(self):
        print("qrs peaks indices")
        print(self.qrs_peaks_indices)
        print("noise peaks indices")
        print("RR intervals (ms)")
        print(self.rr_intervals)
        print(f"Average QRS peak value: {np.mean(self.detected_peaks_values)}")
        print(f"Average RR interval: {np.mean(self.rr_intervals)} ms")

    def log_detection_data(self):
        with open(self.log_path, "wb") as fin:
            fin.write(b"timestamp,ecg_measurement,qrs_detected\n")
            np.savetxt(fin, self.ecg_data_detected, delimiter=",")
        with open(self.log_path.replace(".csv", "_summary.txt"), "w") as fin:
            fin.write(f"Average QRS peak value: {np.mean(self.detected_peaks_values)}\n")
            fin.write(f"Average RR interval: {np.mean(self.rr_intervals)} ms\n")
            fin.write(f"RR intervals (ms):\n{self.rr_intervals}\n")

    def plot_detection_data(self, show_plot=False):
        def plot_data(axis, data, title='', fontsize=10):
            axis.set_title(title, fontsize=fontsize)
            axis.grid(which='both', axis='both', linestyle='--')
            axis.plot(data, color="salmon", zorder=1)

        def plot_points(axis, values, indices):
            axis.scatter(x=indices, y=values[indices], c="black", s=50, zorder=2)

        plt.close('all')
        fig, ax = plt.subplots(figsize=(15, 8))
        ax.set_title('Filtered ECG measurements with Detected Peaks', fontsize=15)
        ax.grid(which='both', axis='both', linestyle='--')
        ax.plot(self.ecg_data_raw[:, 1], color="salmon", zorder=1)
        ax.scatter(x=self.detected_peaks_indices, y=self.detected_peaks_values, c="black", s=50, zorder=2)
        plt.tight_layout()
        fig.savefig(self.plot_path)
        if show_plot:
            plt.show()
        plt.close()

if __name__ == "__main__":
    qrs_detector = QRSDetectorOffline(ecg_data_path="ecg_data.csv", verbose=True,
                                      log_data=True, plot_data=True, show_plot=False)