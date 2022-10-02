import os


def filter_files_in_subfolders(path, ext):
    files = []
    for root, dirs, filenames in os.walk(path):
        for f in filenames:
            if f.endswith(ext):
                files.append(f)
    return files

images_in_folder = filter_files_in_subfolders("/media/jetson/data/sony_backup/DCIM/101MSDCF/converted/processed", ".jpg")
print(images_in_folder)
with open(os.path.join("/media/jetson/data/sony_backup/DCIM/101MSDCF/converted/processed/labelized.txt"), "w") as labelized:
    labelized.write("\n".join(images_in_folder))
    # images_already_labelized = [f.split("/")[-1] for f in images_already_labelized]