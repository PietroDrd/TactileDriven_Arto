import os
import pandas as pd
import numpy  as np

import sys
sys.path.append('/home/rluser/thesis_ws/src/ML/UTILITIES')
from PreProcessingFunctions import myfilter, num_transient, sliding_sum_window, select_index, add_padding, do_wavelet, pad_signal_with_noise
from PreProcessingFunctions import WS, WS_B
from PreProcessingFunctions import rename_and_convert_to_txt

from sklearn.preprocessing import StandardScaler

data_folder = '/home/rluser/thesis_ws/src/ML_Levers_Knobs/DATA/1D_KNOB_allFT_ScalNorm/'
folder_path = "/home/rluser/thesis_ws/src/ROBOT_ACTIONS_DATA/KNOB_OPEN/"


def preprocess_signal(signal, cutoff_freq=30, target_length=2000):
    filtered_signal = myfilter(signal, cutoff_freq)
    flag = 0
    if len(signal) < target_length:
        padding_length = target_length - len(signal)
        last_value = signal.iloc[-1]
        # Pad the signal
        padded_signal = np.pad(signal, (0, padding_length), mode='constant', constant_values=last_value)
        flag = 1
        noise_mean = 0
        noise_std = np.std(signal - filtered_signal)
        noise = np.random.normal(noise_mean, noise_std, padding_length)
        padded_signal[-padding_length:] += noise
    elif len(signal) > target_length:
        padded_signal = signal[-target_length:]
    else:
        padded_signal = signal

    # Apply filtering
    filt_signal = myfilter(padded_signal, cutoff_freq)
    #print(f"Original: {len(signal)}, Padded: {len(filt_signal)}, FLAG={flag}")

    # # MEAN NORMALIZATION
    mean = np.mean(filt_signal)
    #normalized_signal = filt_signal #/mean

    # NORMALIZATION using StandardScaler
    signal_scaler = StandardScaler()
    normalized_signal = signal_scaler.fit_transform(filt_signal.reshape(-1, 1)).flatten()

    return normalized_signal

def preprocess_data(csv_path):
    try:
        df = pd.read_csv(csv_path)
        if all(col in df.columns for col in ['Force_X', 'Force_Y', 'Force_Z', 'Torque_X', 'Torque_Y', 'Torque_Z', 'Y']):
            # Preprocess each force and torque signal
            signals = []
            for col in ['Force_X', 'Force_Y', 'Force_Z', 'Torque_X', 'Torque_Y', 'Torque_Z']:
                signal = preprocess_signal(df[col])
                signals.append(signal)
            
            # Stack the signals along the third axis
            X = np.dstack(signals)
            
            y = df.loc[0, "Y"]
            return X, y
        else:
            print(f"Skipping file {csv_path}: Required columns are missing.")
            rename_and_convert_to_txt(csv_path)
            return None, None
    except Exception as e:
        print(f"Error processing file {csv_path}: {e}")
        return None, None


def preprocess_folder_data(folder_path, data_folder):
    # Create the data folder if it doesn't exist
    os.makedirs(data_folder, exist_ok=True)
    c=0
    
    # Traverse the folder structure
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                X_data, y_data = preprocess_data(file_path)
                if X_data is not None and y_data is not None:
                    # Save preprocessed data into a file in the data folder
                    file_name = os.path.splitext(file)[0] + f"#{c}_preprocessed.npy"
                    save_path = os.path.join(data_folder, file_name)
                    np.savez(save_path, X=X_data, y=y_data)
                    print(f"Preprocessed data saved to {save_path}")
                    c +=1
                    #print("num --> ", c)

# Call the preprocess_folder_data function
preprocess_folder_data(folder_path, data_folder)

# # Function to navigate through directory and preprocess data from CSV files
# def preprocess_folder_data(folder_path):
#     X_data = []
#     y_data = []
#     # Traverse the folder structure
#     for root, _, files in os.walk(folder_path):
#         for file in files:
#             if file.endswith(".csv"):
#                 file_path = os.path.join(root, file)
#                 X, y = preprocess_data(file_path)
#                 if X is not None and y is not None and len(X) >= 10 and X.ndim != 0:
#                     print(f"{file_path[len(folder_path)+1:]} adding, its len: {X.shape}, Y is: {y}")
#                     X_data.append(X)
#                     y_data.append(y)
#                     print("current X_data: ", len(X_data), len(X_data[len(X_data)-1]))
#     X_data = np.array(X_data)
    
#     return X_data, np.array(y_data)