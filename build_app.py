import subprocess
import shutil
import os


def main():
    root_path = os.getcwd()
    srcs_path = os.path.join(root_path, 'srcs')
    panels_path = os.path.join(root_path, 'panels')

    for panel_name in os.listdir(srcs_path):
        panel_path = os.path.join(srcs_path, panel_name)
        if not os.path.isfile(os.path.join(panel_path, 'package.json')):
            continue
        print(f'Building panel name: {panel_name}')
        os.chdir(panel_path)
        subprocess.check_call(f'npm i', shell=True)
        subprocess.check_call(f'npm run build', shell=True)
        os.chdir(root_path)

        print(f'Copying dist to panels/{panel_name}')
        src_dir = os.path.join(panel_path, 'dist')
        dst_dir = os.path.join(panels_path, panel_name)
        # clean destination
        if os.path.isdir(dst_dir):
            shutil.rmtree(dst_dir)
        # move dist folder
        shutil.move(src=src_dir, dst=os.path.dirname(dst_dir))
        # rename to panel name
        os.rename(os.path.join(panels_path, 'dist'), os.path.join(panels_path, panel_name))
        #
        # lines = list()
        # panel_index_filepath = os.path.join(panels_path, panel_name, 'index.html')
        # with open(panel_index_filepath, 'r') as f:
        #     for line in f.readlines():
        #         if "/assets/" in line:
        #             line = line.replace('/assets/', 'assets/')
        #         lines.append(line)
        #
        # with open(panel_index_filepath, 'w') as f:
        #     f.writelines(lines)
