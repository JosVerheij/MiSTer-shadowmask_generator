import shutil
from pathlib import PurePath, Path

from masks import *

# cur_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIRECTORY = (
    PurePath(__file__).parents[1] /
    "ShadowMasks_MiSTer" /
    "Shadow_Masks" /
    "Jovec Masks"
    )

BRIGHTNESS_LEVELS = {
    "strong definition": 4,
    "light definition": 8,
    "extra light definition": 10,
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

GRID = {
    "Magenta-Green": [
        [0, 0, 0, 5, 2, 0],
        [5, 2, 0, 5, 2, 0],
        [5, 2, 0, 0, 0, 0],
        [5, 2, 0, 5, 2, 0],
    ],
    "Monochrome": [
        [0, 0, 0, 7, 7, 0],
        [7, 7, 0, 7, 7, 0],
        [7, 7, 0, 0, 0, 0],
        [7, 7, 0, 7, 7, 0],
    ],
    "RGB Lean": [
        [0, 0, 0, 0, 0, 0, 4, 4, 2, 2, 1, 1],
        [4, 4, 2, 2, 1, 1, 4, 4, 2, 2, 1, 1],
        [4, 4, 2, 2, 1, 1, 4, 4, 2, 2, 1, 1],
        [4, 4, 2, 2, 1, 1, 0, 0, 0, 0, 0, 0],
        [4, 4, 2, 2, 1, 1, 4, 4, 2, 2, 1, 1],
        [4, 4, 2, 2, 1, 1, 4, 4, 2, 2, 1, 1],
    ],
    "RGB": [
        [0, 0, 0, 0, 0, 0, 0, 4, 4, 2, 2, 1, 1, 0],
        [4, 4, 2, 2, 1, 1, 0, 4, 4, 2, 2, 1, 1, 0],
        [4, 4, 2, 2, 1, 1, 0, 4, 4, 2, 2, 1, 1, 0],
        [4, 4, 2, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [4, 4, 2, 2, 1, 1, 0, 4, 4, 2, 2, 1, 1, 0],
        [4, 4, 2, 2, 1, 1, 0, 4, 4, 2, 2, 1, 1, 0],
    ],
    "RYCB Lean": [
        [0, 0, 0, 0, 4, 6, 3, 1],
        [4, 6, 3, 1, 4, 6, 3, 1],
        [4, 6, 3, 1, 0, 0, 0, 0],
        [4, 6, 3, 1, 4, 6, 3, 1],
    ],
    "RYCB": [
        [0, 0, 0, 0, 0, 4, 6, 3, 1, 0],
        [4, 6, 3, 1, 0, 4, 6, 3, 1, 0],
        [4, 6, 3, 1, 0, 0, 0, 0, 0, 0],
        [4, 6, 3, 1, 0, 4, 6, 3, 1, 0],
    ],
    "Squished VGA": [
        [4, 4, 2, 2, 1, 1],
        [2, 1, 1, 4, 4, 2],
    ],
    "Thin RGB Lean": [
        [0, 0, 0, 4, 2, 1],
        [4, 2, 1, 4, 2, 1],
        [4, 2, 1, 0, 0, 0],
        [4, 2, 1, 4, 2, 1],
    ],
    "Thin RGB": [
        [0, 0, 0, 0, 4, 2, 1, 0],
        [4, 2, 1, 0, 4, 2, 1, 0],
        [4, 2, 1, 0, 0, 0, 0, 0],
        [4, 2, 1, 0, 4, 2, 1, 0],
    ],
    "VGA": [
        [4, 4, 2, 2, 1, 1],
        [4, 4, 2, 2, 1, 1],
        [2, 1, 1, 4, 4, 2],
        [2, 1, 1, 4, 4, 2],
    ],
}


def generate_mask_files(path, name, mask_matrix, br_level):

    for i in range(STEPS):
        if i % 2 != 0:  # only execute every 2nd iteration
            continue

        f_name = f'{name}'

        _path = Path(path) if i == 0 else (
            Path(path) /
            'Brightness++' /
            f'Brightness {100 + round(FACTOR * i)}%'
            )
        _path.mkdir(parents=True, exist_ok=True)

        with open(PurePath(_path) / f'{f_name}.txt', "w") as f:
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
if Path(OUTPUT_DIRECTORY).exists():
    shutil.rmtree(OUTPUT_DIRECTORY)

# STRIPES
for br_name, br_level in BRIGHTNESS_LEVELS.items():
    for mask_name, mask_matrix in STRIPES.items():
        path = PurePath(OUTPUT_DIRECTORY) / "Stripes" / br_name.title()

        generate_mask_files(path, mask_name, mask_matrix, br_level)

# GRID
for br_name, br_level in BRIGHTNESS_LEVELS.items():
    for mask_name, mask_matrix in GRID.items():
        path = PurePath(OUTPUT_DIRECTORY) / "Grid" / br_name.title()

        generate_mask_files(path, mask_name, mask_matrix, br_level)
