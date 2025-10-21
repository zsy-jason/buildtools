import argparse
import os
import shutil
import subprocess
import tarfile

def read_ensure_file(ensure_file_path: str):
    name_url_map = {}
    current_name = None

    with open(ensure_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # matching "@name" line (e.g. "@name dsymutil-darwin-arm64")
            if line.startswith('@name '):
                # extract filename after "@name " (e.g. "dsymutil-darwin-arm64")
                current_name = line[len('@name '):]
            # matching download url line (e.g. "https://example.com/file.tar.gz")
            elif line.startswith('https://') and current_name:
                name_url_map[current_name] = line
                # reset current_name to None to avoid binding subsequent urls to the same name
                current_name = None

    return name_url_map


def download_and_make_archive(name_url_map: dict[str, str]):
    for name, url in name_url_map.items():
        print(f'downloading {name} from {url}')
        subprocess.check_output(['curl', '-o', f'{name}', url], stderr=subprocess.STDOUT)
        print(f'compressing {name}.tar.gz')
        if os.path.isdir(name):
            shutil.make_archive(name, "gztar", name)
        else:
            if name.endswith('.tar.xz') or name.endswith('.tar.gz'):
                continue
            with tarfile.open(f"{name}.tar.gz", "w:gz") as tf:
                tf.add(name, arcname=name)
            os.remove(name)


def process_gcs_packages(ensure_files: str):
    _ensure_files = ensure_files.split(",")

    for ensure_file in _ensure_files:
        name_url_map = read_ensure_file(ensure_file)
        download_and_make_archive(name_url_map)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ensure-files", default="")
    args = parser.parse_args()

    if args.ensure_files:
        process_gcs_packages(args.ensure_files)


main()