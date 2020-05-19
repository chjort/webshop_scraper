import os
import sys

import matplotlib.pyplot as plt
import numpy as np


def cast_int(x):
    try:
        return int(x)
    except ValueError:
        raise ValueError("Not an int {}".format(x))


def parse_input(input_, n_imgs):
    command = input_[0]
    assert command in ("d", "k"), "Invalid command."

    indices = []
    for i in input_[1:]:
        idx = cast_int(i)
        if idx >= n_imgs:
            raise ValueError("Index out of range {}".format(idx))
        indices.append(idx)

    return command, indices


def get_subdir(file):
    return file.split(os.sep)[-2]


def get_subdirs(file_list):
    return set([get_subdir(dupe) for dupe in file_list])


def find_contaminated_dirs(dupes):
    contaminated_dirs = []
    for dupe_list in dupes:
        dupe_dirs = get_subdirs(dupe_list)
        if len(dupe_dirs) > 1:
            contaminated_dirs.append(dupe_dirs)

    return contaminated_dirs


def delete_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)


def move_file(filepath, dst):
    if os.path.exists(filepath):
        dst_path = os.path.split(dst)[0]
        os.makedirs(dst_path, exist_ok=True)
        os.rename(filepath, dst)


def move_file_old(filepath):
    if os.path.exists(filepath):
        root = filepath.split(os.sep)[0]
        rel_path = os.sep.join(filepath.split(os.sep)[1:])

        dst_root = root + "_dupes"
        dst = os.path.join(dst_root, rel_path)

        dst_path = os.path.split(dst)[0]
        os.makedirs(dst_path, exist_ok=True)

        os.rename(filepath, dst)


class Plotter:
    def __init__(self, max_imgs_per_row=4):
        self.max_imgs_per_row = max_imgs_per_row
        self.fig = plt.figure(figsize=(16, 12))
        self.axes = []
        plt.box(on=None)
        plt.ion()
        plt.axis("off")
        plt.tight_layout(rect=[0, 0.03, 1, 0.92])
        plt.show()

    def delete_subplot(self, idx):
        ax = self.axes[idx]
        try:
            ax.remove()
        except KeyError:
            pass

        plt.draw()

    def clear_figure(self):
        for i in range(len(self.axes)):
            self.delete_subplot(i)
        self.axes = []
        plt.draw()

    def draw_images(self, img_list, title=None):
        n_imgs = len(img_list)
        if n_imgs > self.max_imgs_per_row:
            n_rows = int(np.ceil(n_imgs / self.max_imgs_per_row))
            n_cols = self.max_imgs_per_row
        else:
            n_rows = 1
            n_cols = n_imgs

        spine_colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        img_subdirs = [get_subdir(img_path) for img_path in img_list]
        unique_subdirs = set(img_subdirs)
        if len(unique_subdirs) > len(spine_colors):
            title = title + "\nMore subdirectories than colors!"

        subdir_colors = {subdir: spine_colors[i] for i, subdir in enumerate(unique_subdirs)}
        for i in range(n_imgs):
            img_path = img_list[i]
            img = plt.imread(img_path)
            img_res = "{}x{}".format(img.shape[0], img.shape[1])
            ax = self.fig.add_subplot(n_rows, n_cols, i + 1)

            ax.imshow(img)
            ax.set_title(img_res)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel(i)

            subdir = img_subdirs[i]
            c = subdir_colors[subdir]
            for pos in ("right", "left", "top", "bottom"):
                # ax.spines[pos].set_visible(False)
                ax.spines[pos].set_color(c)
                ax.spines[pos].set_linewidth(4)

            self.axes.append(ax)
        plt.suptitle(title + "\n{}".format(unique_subdirs))
        plt.draw()


# %%
dupe_file = sys.argv[1]  # "data/clean/dupes_exact_phash1.txt"
PATH, filename = os.path.split(dupe_file)

with open(dupe_file) as f:
    data = f.read()
    dupe_lists = data.split("\n\n")
    dupe_lists = list(filter(None, dupe_lists))
    dupe_lists = [dupe.split("\n") for dupe in dupe_lists]
    n_dupe_lists = len(dupe_lists)
    print("N dupes:", len(dupe_lists))

# %%
dupe_iter = iter(dupe_lists)
plotter = Plotter()
i = 0
do = True
while do:
    try:
        dupe_list = next(dupe_iter)
        dupe_dirs = get_subdirs(dupe_list)
        i = i + 1
    except StopIteration:
        break

    # Compute output path to move duplicates to
    dupe_move_dst = []
    for dupe in dupe_list:
        dupe_split = dupe.split(os.sep)
        dupe_split[0] = dupe_split[0] + "_dupes"
        dupe_dst = os.sep.join(dupe_split)
        dupe_dst = os.path.join(PATH, dupe_dst)
        dupe_move_dst.append(dupe_dst)

    img_list = [os.path.join(PATH, dupe) for dupe in dupe_list]
    plotter.clear_figure()
    plotter.draw_images(img_list, title="{}/{}".format(i, n_dupe_lists))

    stay = True
    while stay:
        inp = input("Enter command: ")
        if inp == "":
            stay = False
        elif inp == "q":
            stay = False
            do = False
            break
        else:
            try:
                command, indices = parse_input(inp, len(img_list))
                if command == "d":
                    for idx in indices:
                        img_path = img_list[idx]
                        dupe_dst = dupe_move_dst[idx]
                        move_file(img_path, dupe_dst)
                        plotter.delete_subplot(idx)
                elif command == "k":
                    for idx in range(len(img_list)):
                        if idx not in indices:
                            img_path = img_list[idx]
                            dupe_dst = dupe_move_dst[idx]
                            move_file(img_path, dupe_dst)
                            plotter.delete_subplot(idx)
                else:
                    raise ValueError("Invalid command.")

                if len(img_list) == 0:
                    stay = False
                else:
                    stay = True

            except Exception as e:
                print(e)
