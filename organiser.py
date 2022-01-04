from pathlib import PurePath, Path
from mask import Cell, Mask


MASK_SEPARATOR = ','
MASK_ROOT = "masks"


class Organiser:
    # file_paths = []
    masks = []
    brightness_levels = []

    def collect_mask_files(self, input_dir):
        for path in sorted(Path('.').glob('**/*.txt')):
            # self.file_paths.append(path)
            self.import_mask_file(path)

    def import_mask_file(self, file_path):
        # file_path = PurePath(file_path)
        name = file_path.stem
        matrix = []

        with file_path.open() as f:
            nonblank_lines = filter(None, (line.rstrip() for line in f))
            for line in nonblank_lines:
                if line.strip().startswith("#"):  # allow for commented lines
                    continue

                line_array = line.strip().replace(' ', '').split(MASK_SEPARATOR)

                cell_row = []
                color, on, off = 0, 0, 0
                for cell_txt in line_array:
                    color = int(cell_txt[0], 16)
                    if len(cell_txt) > 1:
                        on = int(cell_txt[1], 16)
                    if len(cell_txt) > 2:
                        off = int(cell_txt[2], 16)

                    cell_row.append(Cell(color, on, off))

                matrix.append(cell_row)

        directory = PurePath(file_path).parent.relative_to(MASK_ROOT)
        mask = Mask(matrix, name, directory)
        self.masks.append(mask)

    def generate_mask_files(self, output_dir, normalised=True):
        # todo brightness directory and layout

        brightness_levels = [100, 110, 125, 150, 175,]

        for mask in self.masks:
            output_base = Path(output_dir) / mask.directory

            # base
            output_path = output_base / f'{mask.name}.txt'
            self.create_mask_file(mask.matrix, output_path)

            # normalised
            if normalised:
                matrix = mask.get_brighter_matrix(mask.normalised_brightness)
                output_path = output_base / "normalised" / f'{mask.name}.txt'
                self.create_mask_file(matrix, output_path)



    def create_mask_file(self, matrix, output_path):
        # TODO: emp hack to get around blocking on too bright matrices
        if matrix == None:
            return

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with Path(output_path).open("w") as f:
            f.write("v2\n\n")
            f.write(f'{len(matrix[0])},{len(matrix)}')
            f.write("\n\n")

            for row in matrix:
                f.write(','.join(
                    [f'{cell.color:x}{cell.on:x}{cell.off:x}' for cell in row])
                )
                for cell in row:
                f.write("\n")
