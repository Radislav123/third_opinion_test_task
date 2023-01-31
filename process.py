import json
import os
from pathlib import Path

import pydicom


SOURCE_FOLDER_PATH = "src"
RESULT_FOLDER_PATH = "results"
JSON_MAPPING_FILENAME = "result.json"


def process(source_folder_path: str, result_folder_path: str) -> dict[str, str]:
    # соответствие старых путей, новым
    # {old_filepath: new_filepath}
    filename_mapping = {}
    for filename in os.listdir(source_folder_path):
        filepath = f"{source_folder_path}/{filename}"
        dataset = pydicom.dcmread(filepath)

        # информация анонимизируется
        try:
            del dataset["PatientName"]
        except KeyError:
            # файл не содержит имени пациента (тега PatientName)
            pass

        # создается папка для соответствия требуемой структуре, если еще не создана
        new_folder_path = f"{result_folder_path}/" \
                          f"{dataset['StudyInstanceUID'].value}/{dataset['SeriesInstanceUID'].value}"
        Path(new_folder_path).mkdir(parents = True, exist_ok = True)

        # сохраняется файл
        new_filepath = f"{new_folder_path}/{dataset['SOPInstanceUID'].value}.dcm"
        dataset.save_as(new_filepath)

        # добавляется соответствие старого и нового путей
        filename_mapping[filepath] = new_filepath

    return filename_mapping


def save_results(json_mapping_filename: str, filename_mapping: dict[str, str]):
    with open(json_mapping_filename, 'w') as file:
        json_results = {"mapping": filename_mapping}
        json.dump(json_results, file, indent = 2)


if __name__ == "__main__":
    mapping = process(SOURCE_FOLDER_PATH, RESULT_FOLDER_PATH)
    save_results(JSON_MAPPING_FILENAME, mapping)
