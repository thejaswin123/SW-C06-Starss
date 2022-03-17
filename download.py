

import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import tarfile


def download_hursat(years):
    best_track_data = pd.read_csv('besttrack.csv')

    for year in years:
        year_directory_url = 'https://www.ncei.noaa.gov/data/hurricane-satellite-hursat-b1/archive/v06/' + year
        year_directory_page = requests.get(year_directory_url).text
        year_directory_soup = BeautifulSoup(year_directory_page, 'html.parser')
        year_directory_file_urls = [year_directory_url + '/' + node.get('href') for node in
                                    year_directory_soup.find_all('a') if node.get('href').endswith('tar.gz')]
        print('\n' + year + ' file loaded.')

        files_processed = 0
        for storm_file_url in year_directory_file_urls:
            storm_name = storm_file_url.split('_')[-2]
            year = int(storm_file_url.split('_')[3][:4])
            file_has_match_in_best_track = not best_track_data.loc[
                (best_track_data['year'] == year) & (best_track_data['storm_name'] == storm_name)
            ].empty

            if file_has_match_in_best_track:

                file_name = storm_file_url.split('/')[-1]
                storm_file_path = 'Satellite Imagery/' + file_name

                if not os.path.exists('Satellite Imagery'):
                    os.makedirs('Satellite Imagery')

                request = requests.get(storm_file_url, allow_redirects=True)
                open(storm_file_path, 'wb').write(request.content)
                request.close()

                tar = tarfile.open(storm_file_path)
                file_prefixes_in_directory = []
                for file_name in tar.getnames():
                    fulldate = file_name.split(".")[2] + file_name.split(".")[3] + file_name.split(".")[4]
                    time = file_name.split(".")[5]
                    satellite = file_name.split(".")[7][:3]

                    
                    file_has_match_in_best_track = not best_track_data.loc[
                        (best_track_data['fulldate'] == int(fulldate)) & (best_track_data['time'] == int(time))].empty

                    is_redundant = '.'.join(file_name.split('.')[:6]) in file_prefixes_in_directory

                    if file_has_match_in_best_track and not is_redundant and satellite == "GOE":
                        f = tar.extractfile(file_name)
                        open('Satellite Imagery/' + file_name, 'wb').write(f.read())
                        file_prefixes_in_directory.append('.'.join(file_name.split('.')[:6]))

                tar.close()
                os.remove(storm_file_path)

            files_processed += 1
            print_progress('Processing Files for ' + str(year), files_processed, len(year_directory_file_urls))


def print_progress(action, progress, total):
    percent_progress = round((progress / total) * 100, 1)
    print('\r' + action + '... ' + str(percent_progress) + '% (' + str(progress) + ' of ' + str(total) + ')', end='')


if __name__ == "__main__":
    YEARS_TO_DOWNLOAD = ['2016', '2015', '2014', '2013', '2012']

    download_hursat(YEARS_TO_DOWNLOAD)
