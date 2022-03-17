
import pandas as pd
import numpy as np
import os
import netCDF4


best_track_data = pd.read_csv('besttrack.csv')


side_length = 50


images = []
labels = []


files = os.listdir('Satellite Imagery')
num_files = len(files)

for i in range(len(files)):

    raw_data = netCDF4.Dataset('Satellite Imagery/' + files[i])
    ir_data = raw_data.variables['IRWIN'][0]

    south_bound = (ir_data.shape[0] - side_length) // 2
    north_bound = south_bound + side_length
    cropped_ir_data = ir_data[south_bound:north_bound]
    west_bound = (ir_data.shape[1] - side_length) // 2
    east_bound = side_length
    cropped_ir_data = np.delete(cropped_ir_data, np.s_[:west_bound], axis=1)
    cropped_ir_data = np.delete(cropped_ir_data, np.s_[east_bound:], axis=1)

    file_name = files[i]
    file_name = file_name.split('.')
    storm_name = file_name[1]
    date = int(file_name[2] + file_name[3] + file_name[4])
    time = int(file_name[5])

    matching_best_track_data = best_track_data.loc[
        (best_track_data.storm_name == storm_name) &
        (best_track_data.fulldate == date) &
        (best_track_data.time == time)
    ]

    try:
        wind_speed = matching_best_track_data.max_sus_wind_speed.reset_index(drop=True)[
            0]
    except Exception:
        print('\rCould not find label for image of ' + storm_name +
              ' at date ' + str(date) + ' and time ' + str(time), end='\n')
        continue

    images.append(cropped_ir_data)
    labels.append(wind_speed)

    raw_data.close()

    print('\rProcessing Samples... ' + str(round(((i + 1) / num_files) * 100, 1)) + '% (' + str(i + 1) + ' of ' + str(
        num_files) + ')', end='')

print('\nSaving NumPy arrays...')


images = np.array(images)
labels = np.array(labels)


images = images.reshape((images.shape[0], side_length, side_length, 1))


np.save('images.npy', images)
np.save('labels.npy', labels)

print("\nNumPy files saved. Processing complete.")
