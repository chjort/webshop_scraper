import os
import sys

import matplotlib.pyplot as plt
import numpy as np


def cast_int(x):
    try:
        return int(x)
    except ValueError:
        raise ValueError("Not an int {}".format(x))


def parse_input(input_):
    command = input_[0]
    assert command in ("d", "k")

    indices = []
    for i in input_[1:]:
        idx = cast_int(i)
        if idx >= len(img_list):
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


# class Plotter:
#     def __init__(self, imgs_per_row=4):
#         self.imgs_per_row = imgs_per_row
#
#     def new_plot(self, img_list):
#         n_imgs = len(img_list)
#         n_rows = int(np.ceil(n_imgs / self.imgs_per_row))
#         self.fig, self.axes = plt.subplots(n_rows, self.imgs_per_row)
#         self.axes = self.axes.reshape(-1)
#
#         self.draw_images(self.axes, img_list)
#         plt.box(on=None)
#         plt.ion()
#         plt.show()
#         return self.fig
#
#     def update_plot(self, img_list):
#         self.draw_images(self.axes, img_list)
#         plt.draw()
#         return self.fig
#
#     @staticmethod
#     def draw_images(axes, img_list):
#         for i in range(len(axes)):
#             try:
#                 img_path = img_list[i]
#                 img = plt.imread(img_path)
#                 axes[i].imshow(img)
#                 axes[i].set_xticks([])
#                 axes[i].set_yticks([])
#                 axes[i].set_xlabel(i)
#                 axes[i].spines["right"].set_visible(False)
#                 axes[i].spines["left"].set_visible(False)
#                 axes[i].spines["top"].set_visible(False)
#                 axes[i].spines["bottom"].set_visible(False)
#             except IndexError:
#                 axes[i].clear()
#                 axes[i].axis("off")


# def plot_imgs(img_list, imgs_per_row=4):
#     n_imgs = len(img_list)
#     n_rows = int(np.ceil(n_imgs / imgs_per_row))
#     fig, axes = plt.subplots(n_rows, imgs_per_row)
#     axes = axes.reshape(-1)
#
#     for i in range(len(axes)):
#         try:
#             img_path = img_list[i]
#             img = plt.imread(img_path)
#             axes[i].imshow(img)
#             axes[i].set_xticks([])
#             axes[i].set_yticks([])
#             axes[i].set_xlabel(i)
#             axes[i].spines["right"].set_visible(False)
#             axes[i].spines["left"].set_visible(False)
#             axes[i].spines["top"].set_visible(False)
#             axes[i].spines["bottom"].set_visible(False)
#         except IndexError:
#             axes[i].axis("off")
#     plt.box(on=None)
#     plt.show()

class Plotter:
    def __init__(self, max_imgs_per_row=4):
        self.max_imgs_per_row = max_imgs_per_row

    def new_plot(self, img_list):
        n_imgs = len(img_list)
        if n_imgs > self.max_imgs_per_row:
            n_rows = int(np.ceil(n_imgs / self.max_imgs_per_row))
            n_cols = self.max_imgs_per_row
        else:
            n_rows = 1
            n_cols = n_imgs

        # self.fig, self.axes = plt.subplots(n_rows, n_cols)
        # self.axes = self.axes.reshape(-1)
        self.fig = plt.figure()
        self.axes = []

        self.draw_images(self.axes, img_list)
        plt.box(on=None)
        plt.ion()
        plt.show()
        return self.fig

    def update_plot(self, img_list):
        self.draw_images(self.axes, img_list)
        plt.draw()
        return self.fig

    @staticmethod
    def draw_images(axes, img_list):
        for i in range(len(axes)):
            try:
                img_path = img_list[i]
                img = plt.imread(img_path)
                axes[i].imshow(img)
                axes[i].set_xticks([])
                axes[i].set_yticks([])
                axes[i].set_xlabel(i)
                axes[i].spines["right"].set_visible(False)
                axes[i].spines["left"].set_visible(False)
                axes[i].spines["top"].set_visible(False)
                axes[i].spines["bottom"].set_visible(False)
            except IndexError:
                axes[i].clear()
                axes[i].axis("off")


# %%
dupe_file = sys.argv[1]
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
    plotter.new_plot(img_list)

    stay = True
    while stay:
        plotter.update_plot(img_list)
        inp = input("Enter command: ")
        if inp == "":
            stay = False
        elif inp == "q":
            stay = False
            do = False
            break
        else:
            try:
                command, indices = parse_input(inp)
                if command == "d":
                    for idx in sorted(indices, reverse=True):
                        img_path = img_list.pop(idx)
                        os.remove(img_path)
                elif command == "k":
                    for idx in range(len(img_list) - 1, -1, -1):
                        if idx not in indices:
                            img_path = img_list.pop(idx)
                            os.remove(img_path)
                else:
                    raise ValueError("Invalid command.")

                if len(img_list) == 0:
                    stay = False
                else:
                    stay = True

            except Exception as e:
                print(e)
