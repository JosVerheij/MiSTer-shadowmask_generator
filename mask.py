

# class DotPart:
#     ratio = 1

#     def __init__(self, color, on=0, off=0):
#         self.color = color
#         self.on = on
#         self.off = off


# Pattern class
class Pattern:
    # Note: format of the 'dot part':
    # {
    #     "color":  int with range(0,7)
    #     "on":     float of pct of brightness (e.g. "1.25")
    #     "off":    float of pct of opacity (e.g. "0.75")
    # }

    def __init__(self, matrix, compute=False):
        self.matrix = matrix
        self.width = len(self.matrix[0])
        self.height = len(self.matrix)

        if compute:
            self.__compute_ratios()

    def get_size(self):
        return self.width * self.height

    def get_color_count(self, color, weighted=False, on_weighted=True):
        count = 0
        for row in self.matrix:
            for part in row:
                if part["color"] != color:
                    continue
                if weighted:
                    count += 1 * part["ratio"]  # if on_weighted else 1 * part.off_ratio
                else:
                    count += 1
        return count

    def get_min_on_state(self):
        min_values = []

        for row in self.matrix:
            for part in row:
                if part["color"] != 0:
                    min_values.append(part["on"])

        return (min(min_values))

    def get_min_off_state(self):
        # TODO:
        pass

    def get_max_ratio(self, on_state=True):
        ratios = []

        if on_state:
            for row in self.matrix:
                for part in row:
                    ratios.append(part["ratio"])

        return max(ratios)

    # TODO: also compute ratios for off_state maybe
    def __compute_ratios(self):
        min_state = self.get_min_on_state()
        min_state = min_state

        for row in self.matrix:
            for part in row:
                part["ratio"] = part["on"] / min_state if (
                    part["color"] != 0) else 1


class Mask:
    # Properties to be added:
    # - type

    # TODO:
    # calculated brightness levels, such as normalised (maybe)
    brightness_levels = {}

    def __init__(self, name, matrix, n_dots=1, resolution=0, limit=193.75):
        self.name = name
        self.pattern = Pattern(matrix, compute=True)
        self.resolution = resolution
        self.limit = limit

        dotparts_per_dot = self.pattern.get_size() / n_dots
        aspect_ratio = self.pattern.width / self.pattern.height

        self.dots_h = aspect_ratio * dotparts_per_dot
        self.dots_v = (1 / aspect_ratio) * dotparts_per_dot

        # "brightness" for on state, "opacity" for off_state
        # max brightness of lowes on_state (without clipping)
        # self.max_brightness = self.__get_max_br_range()
        # self.min_opacity = None

        self.br_base = self.pattern.get_min_on_state()
        self.br_normalised = self.__get_br_normalised()

    # Return the maximum vertical source resolution that can be
    # displayed, based on the resolution of the display (output_res_v)
    def get_max_res_v(self, output_res_v):
        return output_res_v / self.dots_v

    def get_max_res_h(self, output_res_h):
        pass

    def get_br_desired_matrix(self, br_desired):
        # convert percentage from 1xx to 1.xx
        br_desired *= 0.01 if br_desired >= 100 else 1

        # matrix = Pattern(self.pattern.matrix).matrix
        matrix = []

        gap = br_desired - self.br_base

        for j in range(len(self.pattern.matrix)):
            row = []
            for i in range(len(self.pattern.matrix[0])):
                dot = {}
                src_dot = self.pattern.matrix[j][i]

                dot["color"] = src_dot["color"]
                dot["on"] = (
                    src_dot["on"] + src_dot["ratio"] * gap
                    )
                dot["off"] = src_dot["off"]  # * src_dot["ratio_off"] * self.opacity_base

                row.append(dot)
            matrix.append(row)

        return matrix

    # TODO: bug when all colors are gray (division by zero)
    # TODO: add opacity calculations as well
    def __get_br_normalised(self):
        colors = [
            {
                "color": "blue",
                "value": 1,
                "hex": 0x0000FF,
            },
            {
                "color": "green",
                "value": 2,
                "hex": 0x00FF00,
            },
            {
                "color": "cyan",
                "value": 3,
                "hex": 0x00FFFF,
            },
            {
                "color": "red",
                "value": 4,
                "hex": 0xFF0000,
            },
            {
                "color": "magenta",
                "value": 5,
                "hex": 0xFF00FF,
            },
            {
                "color": "yellow",
                "value": 6,
                "hex": 0xFFFF00,
            },
            {
                "color": "white",
                "value": 7,
                "hex": 0xFFFFFF,
            },
        ]

        dist = 0

        # all except gray because it does not have a relevant on state
        for color in colors:
            count = self.pattern.get_color_count(color["value"], weighted=True)
            share = 1 / count if count != 0 else 0

            # calc relative brightness necessary for 'even' distribution
            share /= calculate_luminance(color["hex"])

            dist += share

        # returns percentage points, e.g. '122'
        return self.pattern.get_size() / dist * 100

    def get_max_br_range(self, limit):
        max_ratio = self.pattern.get_max_ratio()

        br_range = limit - max_ratio * self.br_base

        return br_range


# see: https://stackoverflow.com/a/69520354
def calculate_luminance(hex_color):
    imgPixel = hex_color

    R = (imgPixel & 0xFF0000) >> 16
    G = (imgPixel & 0x00FF00) >> 8
    B = (imgPixel & 0x0000FF)

    Y = 0.2126*(R/255.0)**2.2 + 0.7152*(G/255.0)**2.2 + 0.0722*(B/255.0)**2.2

    return Y
