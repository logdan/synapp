from scipy import signal as sps
import pandas as pd


def butter_bandpass(lowcut, highcut, fs, order=2):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = sps.butter(order, [low, high], btype="band")
    return b, a


def butter_bandpass_filter(data, lowcut=0.01, highcut=30, fs=256, order=2):
    b, a = butter_bandpass(lowcut, highcut, fs, order)
    y = sps.lfilter(b, a, data)
    return y


def notch_filter(data, q=100, w0=60, delta=0.5, fs=256):
    nyq = 0.5 * fs
    low = (w0 - delta) / nyq
    high = (w0 + delta) / nyq
    b, a = sps.butter(q, [low, high], btype="bandstop")
    y = sps.lfilter(b, a, data)
    return y


def bandpass_notch_filter_dataframe(
    dataframe: pd.DataFrame,
    lowcut=0.1,
    highcut=30,
    notch_frequency=60,
    filter_order=2,
    sample_rate=256,
):
    """Essential filter for EEG data. Bandpass filter between 0.1-30Hz,
    and a notch filter at 60/50 Hz for power line noise.
    """

    out_dataframe = pd.DataFrame(index=dataframe.index, columns=dataframe.keys())

    for col_name, col in dataframe.items():
        out_dataframe[col_name] = butter_bandpass_filter(
            notch_filter(col, q=6, w0=notch_frequency, fs=sample_rate),
            lowcut=lowcut,
            highcut=highcut,
            order=filter_order,
            fs=sample_rate,
        )

    return out_dataframe
