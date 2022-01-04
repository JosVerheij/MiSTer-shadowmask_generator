import shutil
from pathlib import PurePath, Path


# cur_dir = os.path.dirname(os.path.abspath(__file__))
MASK_ROOT = "masks"
MASK_SEPARATOR = ","

OUTPUT_DIRECTORY = (
    PurePath(__file__).parents[1] /
    "ShadowMasks_MiSTer" /
    "Shadow_Masks" /
    "Jovec Masks"
    )

BRIGHTNESS_LEVELS = {
    "distinct visibility": 4,
    "subtle visibility": 8,
    "extra subtle visibility": 10,
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


class Mask:
    def __init__(self, mask_path):
        self.path = Path(mask_path)
        # self.name = self.path.stem
        self.directory = PurePath(self.path).parent.relative_to(MASK_ROOT)
        self.matrix = []

        with self.path.open() as f:
            nonblank_lines = filter(None, (line.rstrip() for line in f))
            for line in nonblank_lines:
                if line.strip().startswith("#"):  # allow for commented lines
                    continue
                line_array = line.strip().replace(' ', '').split(MASK_SEPARATOR)
                self.matrix.append(line_array)

    def generate_mask_files(self):
        for on_level in range(STEPS):
            if on_level % 2 != 0:  # only execute every 2nd iteration
                continue

            for br_name, off_level in BRIGHTNESS_LEVELS.items():
                matrix = self.convert_matrix(on_level, off_level)

                # output directory
                path = (
                    Path(OUTPUT_DIRECTORY) /
                    self.directory.name.title() /
                    br_name.title()
                    )
                # create brightness folders when off_state > 100%
                if on_level != 0:
                    path = (
                        path /
                        'Brightness++' /
                        f'Brightness {100 + round(FACTOR * on_level)}%'
                        )

                path.mkdir(parents=True, exist_ok=True)

                self.create_mask_file(
                    matrix,
                    path / self.path.name  # final output path
                    )

    def convert_matrix(self, on_level, off_level):
        matrix = self.matrix

        for j in range(len(matrix)):
            for i in range(len(matrix[0])):
                print(matrix[j][i])
                matrix[j][i] = [int(matrix[j][i][0]), on_level, off_level]

        return matrix

    @classmethod
    def create_mask_file(cls, matrix, output_path):

        with Path(output_path).open("w") as f:
            f.write("v2\n\n")
            f.write(f'{len(matrix[0])},{len(matrix)}')
            f.write("\n\n")

            for row in matrix:
                f.write(','.join([f'{val[0]:x}{val[1]:x}{val[2]:x}' for val in row]))
                f.write("\n")


def load_masks():
    msk_all = sorted(Path('.').glob('**/*.txt'))

    for msk_path in msk_all:
        Mask(msk_path).generate_mask_files()


# Delete all filters and regenerate them
if Path(OUTPUT_DIRECTORY).exists():
    shutil.rmtree(OUTPUT_DIRECTORY)

load_masks()
