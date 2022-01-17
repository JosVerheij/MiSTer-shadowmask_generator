from pathlib import PurePath, Path
from mask import Mask

# TODO: implement mask import function

PATTERN_SEPARATOR = ','
PATTERN_ROOT = "masks"


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
            self.import_mask_file(path)

    def import_mask_file(self, file_path):
        # file_path = PurePath(file_path)
        matrix = []

        loaded, v2 = False

        w, h, y = -1, -1, 0

        descr = {}

        with file_path.open() as f:

            for line in f:

                # Parsing the 'pre-amble'
                if line.rstrip().startswith('#'):

                    if m := re.match('^\s*#\s*(?P<key>\w):\s.(?P<val>\w+)\s.$', line):

                        for k, v in m.groupdict():
                            if k.upper() in ['NAME', 'AUTHOR', 'DOTS']:
                                descr[k.upper()] = v
                                continue


                if w == -1:
                    if line.upper() == "V2":
                        v2 = True
                        continue

                    if line.upper()[:11] == "RESOLUTION=":
                        continue

                    # Stop parsing if width, height is not defined
                    # NB: n, w, and h are defined here
                    w, h = (n := [int(i) for i in line.split(',')])[:2]; n = len(n)
                    if n != 2 or w <= 0 or h <= 0 or w > 16 or h > 16:
                        break

                # parsing the mask matrix
                else:
                    p = [hex(i) for i in line.split(',')]
                    # break if number of positions in line does not equal mask width
                    if len(p) != w:
                        break

                    #  do something useful with the mask line here
                    # TOOD: check if bitwise operation is necessary at this point
                    p[x] = p[x] & 0x7FF if v2 else ((p[x] & 7) << 8) | 0x2A for x in range(len(p))
                    y += 1

                    if y == h:
                        loaded = True

        if not loaded:
            # if loaded==False then mask was not fully loaded, so fail gracefully or something
            pass


        matrix = self.parse_matrix(matrix)

        directory = PurePath(file_path).parent.relative_to(PATTERN_ROOT)
        self.maskfiles.append({
            "mask": Mask(name, matrix),
            "directory": directory,
            })

    def set_br_levels(self, br_levels):
        self._br_levels = br_levels

    # TODO: rename function into sometime that is not almost the same as
    # 'self.create_pattern_file()'
    def generate_pattern_files(self, output_dir, normalised=True):
        # todo brightness directory and layout

        brightness_levels = [1.0, 1.1, 1.25, 1.5, 1.75]
        opacity_levels = {
            "dark": 0.25, "light": 0.50, "extra light": 0.75
        }

        for msk_f in self.maskfiles:
            for name, opacity in opacity_levels.items():

                for br_level in brightness_levels:
                    pattern_matrix = msk_f["mask"].get_br_desired_matrix(
                        br_level, opacity
                        )
                    output_path = (
                        output_dir /
                        msk_f["directory"] /
                        f'Brightness {round(br_level*100)}%' /
                        f'{msk_f["mask"].name} {name}.txt'
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
