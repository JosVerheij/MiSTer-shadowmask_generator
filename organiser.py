from pathlib import PurePath, Path
from mask import Mask

# TODO: implement mask import function

PATTERN_SEPARATOR = ','
PATTERN_ROOT = "masks2"


class Organiser:

    maskfiles = [
        # {
        #     "mask": '',
        #     "directory": ''
        # }
    ]
    brightness_levels = []

    def collect_pattern_files(self, input_dir):
        for path in sorted(Path(PATTERN_ROOT).glob('**/*.txt')):
            # self.file_paths.append(path)
            self.import_pattern_file(path)

    def import_pattern_file(self, file_path):
        # file_path = PurePath(file_path)
        name = file_path.stem
        matrix = []

        with file_path.open() as f:
            nonblank_lines = filter(None, (line.rstrip() for line in f))
            for line in nonblank_lines:
                if line.strip().startswith("#"):  # allow for commented lines
                    continue

                line_array = line.strip().replace(' ', '').split(PATTERN_SEPARATOR)

                dot_row = []

                for dot_txt in line_array:
                    dotpart = {}
                    dotpart["color"] = int(dot_txt[0], 16)
                    dotpart["on"] = int(dot_txt[1], 16) if len(dot_txt) > 1 else 0
                    dotpart["off"] = int(dot_txt[2], 16) if len(dot_txt) > 2 else 0

                    dot_row.append(dotpart)

                matrix.append(dot_row)

        matrix = self.parse_matrix(matrix)

        directory = PurePath(file_path).parent.relative_to(PATTERN_ROOT)
        self.maskfiles.append({
            "mask": Mask(name, matrix),
            "directory": directory,
            })

    # TODO: rename function into sometime that is not almost the same as
    # 'self.create_pattern_file()'
    def generate_pattern_files(self, output_dir, normalised=True):
        # todo brightness directory and layout

        brightness_levels = [1.0, 1.1, 1.25, 1.5, 1.75]

        for msk_f in self.maskfiles:

            for br_level in brightness_levels:
                pattern_matrix = msk_f["mask"].get_br_desired_matrix(br_level)
                output_path = (
                    output_dir /
                    msk_f["directory"] /
                    f'Brightness {round(br_level*100)}%' /
                    f'{msk_f["mask"].name}.txt'
                    )
                self.create_pattern_file(pattern_matrix, output_path)

    def create_pattern_file(self, matrix, output_path):
        # TODO: emp hack to get around blocking on too bright matrices

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        matrix = self.convert_matrix(matrix)

        with Path(output_path).open("w") as f:
            f.write("v2\n\n")
            f.write(f'{len(matrix[0])},{len(matrix)}')
            f.write("\n\n")

            for row in matrix:
                f.write(','.join(
                    [f'{dot["color"]:x}{dot["on"]:x}{dot["off"]:x}' for dot in row])
                )
                f.write("\n")

    def parse_matrix(self, matrix):
        level_limit = 15  # TODO: properly implement max level

        factor = 6.25*0.01
        on_level_base = 100*0.01
        off_level_base = 0*0.01

        for row in matrix:
            for dot in row:
                dot["on"] = dot["on"] * factor + on_level_base
                dot["off"] = dot["off"] * factor + off_level_base

        return matrix

    # TODO: implement clipping
    def convert_matrix(self, matrix):
        level_limit = 15

        factor = 6.25
        on_level_base = 100
        off_level_base = 0

        for row in matrix:
            for dot in row:
                on = (dot["on"] * 100 - on_level_base) / factor
                off = (dot["off"] * 100 - off_level_base) / factor
                dot["on"] = round(on)
                dot["off"] = round(off)

        return matrix
