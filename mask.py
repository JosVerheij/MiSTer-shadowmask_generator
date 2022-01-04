class Cell:
    def __init__(self, color, on=0, off=0):
        self.color = color
        self.on = on
        self.off = off
        self.ratio = 1


class Mask:
    steps = 15
    factor = 6.25

    def __init__(self, matrix, name, directory, fixed_off_state=True):
        self.name = name
        self.matrix = matrix
        self.fixed_off_state = fixed_off_state
        self.dimension = (len(self.matrix[0]), len(self.matrix))
        self.size = (self.dimension[0] + 1) * (self.dimension[1] + 1)
        self.directory = directory

        # get brightness range in base matrix
        max_on_state = 0
        self.min_on_state = self.steps
        for row in self.matrix:
            for cell in row:
                # skip checking brightness for 'gray' color since it has
                # no functional 'on' state
                if cell.color == 0:
                    continue

                if cell.on < self.min_on_state:
                    self.min_on_state = cell.on
                if cell.on > max_on_state:
                    max_on_state = cell.on

        self.on_state_max_ratio = (
            self.br_pct(max_on_state) / self.br_pct(self.min_on_state)
        )

        self.normalised_brightness = self.get_normalised_brightness()
        self.max_brightness_steps = self.get_max_brightness_steps()

        for row in self.matrix:
            for cell in row:
                cell.ratio = self.get_br_ratio(cell.off, self.min_on_state)

    def get_br_ratio(self, numerator, denominator):
        return (
            (numerator * self.factor + 100) /
            (denominator * self.factor + 100)
        )

    def get_max_brightness_steps(self):
        steps = 0
        new_on_state = round((self.min_on_state + 1) * self.on_state_max_ratio)

        while new_on_state <= self.steps:
            steps += 1
            # calc neccesary max_on_state for next step
            new_on_state = round((self.min_on_state + steps) * self.on_state_max_ratio)

        return steps

    def get_normalised_brightness(self):
        msk_dark = 0
        for row in self.matrix:
            for cell in row:
                if cell.color == 0:
                    msk_dark += 1

        # eg. msk_dark = 4, self.size = 10:
        # ratio = 4/10 = 0.4
        #
        return round(1 / (1 - msk_dark / self.size) * 100)

    def get_brighter_matrix(self, desired_min_on_pct, clipping=False):

        required_steps = (round(
            (desired_min_on_pct - self.br_pct(self.min_on_state)) /
            self.factor
        ))
        # required_steps = desired_min_on_pct - self.min_on_state

        # fail if clipping will occur
        if not clipping and required_steps > self.max_brightness_steps:
            # raise
            return

        matrix = self.matrix
        for row in matrix:
            for cell in row:
                cell.on = round((cell.on + required_steps) * cell.ratio)

        return matrix

    def br_pct(self, state):
        return round(state * self.factor + 100)
