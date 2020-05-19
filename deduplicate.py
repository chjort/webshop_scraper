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


def get_dupe_dirs(dupe_list):
    return set([dupe.split("/")[1] for dupe in dupe_list])


def find_contaminated_dirs(dupes):
    contaminated_dirs = []
    for dupe_list in dupes:
        dupe_dirs = get_dupe_dirs(dupe_list)
        if len(dupe_dirs) > 1:
            contaminated_dirs.append(dupe_dirs)

    return contaminated_dirs


def delete_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)


class Plotter:
    def __init__(self, max_imgs_per_row=4):
        self.max_imgs_per_row = max_imgs_per_row
        self.fig = plt.figure()
        self.axes = []
        plt.box(on=None)
        plt.ion()
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

    def draw_images(self, img_list):
        n_imgs = len(img_list)
        if n_imgs > self.max_imgs_per_row:
            n_rows = int(np.ceil(n_imgs / self.max_imgs_per_row))
            n_cols = self.max_imgs_per_row
        else:
            n_rows = 1
            n_cols = n_imgs

        for i in range(n_imgs):
            img_path = img_list[i]
            img = plt.imread(img_path)
            ax = self.fig.add_subplot(n_rows, n_cols, i + 1)

            ax.imshow(img)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel(i)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_visible(False)
            ax.spines["top"].set_visible(False)
            ax.spines["bottom"].set_visible(False)
            self.axes.append(ax)
        plt.draw()


# %%
dupe_file = sys.argv[1]
# dupe_file = "data/clean/dupes_exact_phash1.txt"
PATH, filename = os.path.split(dupe_file)

with open(dupe_file) as f:
    data = f.read()
    dupes = data.split("\n\n")
    dupes = list(filter(None, dupes))
    dupes = [dupe.split("\n") for dupe in dupes]
    print("N dupes:", len(dupes))

# %%
dupe_iter = iter(dupes)
plotter = Plotter()
do = True
while do:
    try:
        dupe_list = next(dupe_iter)
    except StopIteration:
        break

    img_list = [os.path.join(PATH, dupe) for dupe in dupe_list]
    plotter.clear_figure()
    plotter.draw_images(img_list)

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
                        delete_file(img_path)
                        plotter.delete_subplot(idx)
                elif command == "k":
                    for idx in range(len(img_list)):
                        if idx not in indices:
                            img_path = img_list[idx]
                            delete_file(img_path)
                            plotter.delete_subplot(idx)
                else:
                    raise ValueError("Invalid command.")

                if len(img_list) == 0:
                    stay = False
                else:
                    stay = True

            except Exception as e:
                print(e)
