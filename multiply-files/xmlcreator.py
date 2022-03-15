import os
import shutil
import re
import random
import argparse
import logging
import uuid

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG,
)

parser = argparse.ArgumentParser(description='Process file create and modify.')
parser.add_argument('-w', '--workdir', type=str, help='put all files to given directory', required=True)
parser.add_argument('-r', '--recipient', type=str, help='pass recipient regex pattern')
parser.add_argument('-nr', '--new_recipient', type=str, help='new recipient name')
parser.add_argument('-mf', '--max_files', type=int, help='max files to create')
parser.add_argument('-ms', '--max_size', type=int, help='max file size in MB')
parser.add_argument('-fn', '--file_name', type=str, help='pass file name to i.e resize size')


class XMLReportCreator:
    def __init__(self, work_dir: str):
        if not os.path.exists(work_dir):
            os.mkdir(work_dir)
        os.chdir(work_dir)
        logging.debug(f'Working directory set to: {work_dir}')
        self.wd = work_dir
        self.gen_files = self._list_dir_generator()
        self.total_files = len(list(self.gen_files))
        logging.debug(f'Total files in directory: {self.total_files}')

    def _list_dir_generator(self):
        return (_file for _file in os.listdir(self.wd) if _file.endswith('.xml') and os.path.isfile(_file))

    def _random_file_name(self):
        return random.choice(list(self.gen_files))

    def recipient(self, pattern: str, new_name: str) -> None:
        renamed = 0
        for _file in self.gen_files:
            new_name = re.sub(pattern, new_name, _file)
            if new_name:
                renamed += 1
                os.rename(os.path.join(self.wd, _file), os.path.join(self.wd, new_name))
        logging.debug(f'Renamed recipients: {renamed}/{self.total_files}')

    def max_files(self, max_files: int, max_file_size: int = None) -> None:
        uuid_pattern = r'[a-z0-9]{10}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}'
        for _ in range(max_files):
            random_name = self._random_file_name()
            new_name = re.sub(uuid_pattern, str(uuid.uuid4()), random_name)
            shutil.copy(os.path.join(self.wd, random_name), os.path.join(self.wd, new_name))
            if max_file_size:
                self.max_size(new_name, max_file_size)
        logging.debug(f'Add {max_files} files. Total: {self.total_files + max_files}')

    def max_size(self, file_name: str, max_file_size: int) -> None:
        with open(os.path.join(self.wd, file_name)) as f_read:
            content = f_read.read()
        logging.debug(f'Resize file: {file_name}')
        logging.debug(f'Current size: {round(os.stat(os.path.join(self.wd, file_name)).st_size / (1024 * 1024), 3)}MB')
        while round(os.stat(os.path.join(self.wd, file_name)).st_size / (1024 * 1024), 3) < max_file_size:
            with open(os.path.join(self.wd, file_name), 'w+') as f_read:
                f_read.write(content)
        logging.debug(f'New size: {round(os.stat(os.path.join(self.wd, file_name)).st_size / (1024 * 1024), 3)}MB')


if __name__ == '__main__':
    args = parser.parse_args()
    creator = XMLReportCreator(args.workdir)
    if args.recipient and args.new_recipient:
        creator.recipient(args.recipient, args.new_recipient)
    if args.max_files:
        if args.max_size and not args.file_name:
            creator.max_files(args.max_files, max_file_size=args.max_size)
        else:
            creator.max_files(args.max_files)
    if args.max_size and args.file_name:
        creator.max_size(args.file_name, args.max_size)
