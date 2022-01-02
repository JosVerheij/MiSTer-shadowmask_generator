import os
import shutil
from pathlib import PurePath
import sys


# cur_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIRECTORY = (
    PurePath(__file__).parents[1] /
    "ShadowMasks_MiSTer" /
    "Shadow_Masks" /
    "Jovec Masks"
    )

BRIGHTNESS_LEVELS = {
    "dark": 4,
    "medium": 8,
    "light": 10,
}

FACTOR = 6.25
STEPS = 15

# Color codes. See https://github.com/MiSTer-devel/ShadowMasks_MiSTer
# gray    0
# blue    1
# green   2
# cyan    3
# red     4
# magenta 5
# yellow  6
# white   7

# stripes
STRIPES = {
    "Magenta-Green":    [[5, 2]],
    "Monochrome":       [[7, 7, 0]],
    "RYCB":             [[4, 6, 3, 1]],
    "Thin RGB":         [[4, 2, 1]],
}


def generate_mask_files(path, name, mask_matrix, br_level):

    for i in range(STEPS):
        f_name = f'{name}_Br_{100 + round(FACTOR * i)}'

        with open(os.path.join(path, f'{f_name}.txt'), "w") as f:
            f.write("v2\n\n")
            f.write(f'{len(mask_matrix[0])},{len(mask_matrix)}')
            f.write("\n\n")
            # f.writelines(convert_matrix(mask_matrix, i + 1, br_level))

            for row in mask_matrix:
                f.write(','.join([f'{value}{i:x}{br_level:x}' for value in row]))
                f.write("\n")


def convert_matrix(matrix, on_level, off_level):
    for row in matrix:
        for value in row:
            matrix[row][value] = f'i,{hex(on_level)},{hex(off_level)}'
    return matrix


# Delete all filters and regenerate them
if os.path.exists(OUTPUT_DIRECTORY):
    shutil.rmtree(OUTPUT_DIRECTORY)
for br_name, br_level in BRIGHTNESS_LEVELS.items():
    for mask_name, mask_matrix in STRIPES.items():
        path = os.path.join(OUTPUT_DIRECTORY, "Stripes", br_name.title(), mask_name)
        os.makedirs(path, exist_ok=True)

        generate_mask_files(path, mask_name, mask_matrix, br_level)
