from pathlib import Path
import re

ON_LEVElS, OFF_LEVELS = [], []

# fb_width, fb_height = 0, 0
# i_on, i_off = 0, 0


def get_mask_file(file_path):
    # SM_NAME = Path(file_path.stem)

    with file_path.open() as f:
        get_mask(f)


def get_mask(text):
    global SM_AUTHOR, SM_NAME, SM_TYPE, SM_DOTS_H, SM_DOTS_V, SM_MATRIX

    # file_path = PurePath(file_path)

    SM_DOTS_H, SM_DOTS_V = 1.0, 1.0
    SM_AUTHOR, SM_NAME, SM_TYPE = None, None, None
    SM_MATRIX = []

    loaded, v2 = False, False

    w, h, y = -1, -1, 0

    for line in [line.strip() for line in text]:
        # skip empty lines
        if not line.strip():
            continue

        if w == -1:
            # Parsing the 'pre-amble'
            if line.strip().startswith('#'):

                if m := re.match(r'^\s*#\s*(?P<k>\w+)\s*:\s*(?P<v>.+)\s*$', line):
                    if m.group('k').upper() == "AUTHOR":
                        SM_AUTHOR = str(m.group('v').strip())
                    elif m.group('k').upper() == "NAME":
                        SM_NAME = str(m.group('v').strip())
                    elif m.group('k').upper() == "TYPE":
                        SM_TYPE = str(m.group('v').strip())
                    elif m.group('k').upper() == "DOTS_HORIZONTAL":
                        SM_DOTS_H = float(m.group('v').strip())
                    elif m.group('k').upper() == "DOTS_VERTICAL":
                        SM_DOTS_V = float(m.group('v').strip())
                continue

            if line.upper() == "V2":
                v2 = True
                continue

            if line.upper()[:11] == "RESOLUTION=":
                continue

            # Stop parsing if width, height is not defined
            # NB: n, w, and h are defined here
            w, h = (n := [int(i) for i in re.sub(r'\s+', '', line).split(',')])[:2]
            n = len(n)
            if n != 2 or w <= 0 or h <= 0 or w > 16 or h > 16:
                break

        # parsing the mask matrix
        else:
            if line.lstrip().startswith('#'):
                continue

            p = [int(i, 16) for i in re.sub(r'\s+', '', line).split(',')]
            # break if number of positions in line does not equal mask width
            if len(p) != w:
                break

            #  do something useful with the mask line here
            # TOOD: check if bitwise operation is necessary at this point
            SM_MATRIX.append(
                [p[x] & 0x7FF if v2 else ((p[x] & 7) << 8) | 0x2A for x in range(len(p))]
                )
            y += 1

            if y == h:
                loaded = True

    if not loaded:
        # if loaded==False then mask was not fully loaded, so fail gracefully or something
        pass


# TODO: currently is simple replacement of existing on and off levels
#       in future will make it so that brightness ratio is taken into
#       account.
def get_sm_matrix(pct_on, pct_off):
    v_on = intensity_b(pct_on)
    v_off = intensity_b(pct_off)

    m = []

    # w, h = len(SM_MATRIX), len(SM_MATRIX[0])

    for j in range(len(SM_MATRIX)):
        m.append([
            (
                (SM_MATRIX[j][i] & 0x700) +
                ((v_on & 0xF) << 4) +
                (v_off & 0xF)
                ) for i in range(len(SM_MATRIX[0]))
            ])

    return m


def new_mask_file(p, v_res, sort_by="SHAPE"):
    p = Path(p) / f'{v_res}p'  # output path

    h, w = len(SM_MATRIX), len(SM_MATRIX[0])

    shape = 'stripe' if h == 1 else 'grid'
    # max res. of the shadow mask on target output resolution
    maxres_v = (v_res/h)*SM_DOTS_V if h > 1 else (v_res/w)*SM_DOTS_H

    # TODO: figure out how (masks like) Squished-VGA can be included as well
    sm_type = 'accurate' if ((w/SM_DOTS_H) == (h/SM_DOTS_V)) or h == 1 else 'stylised'

    paths = []

    # TODO: maybe work with naming the directories depending on shape, tech, etc.
    # dirs = []

    if sort_by == "SHAPE":
        pass

    if sort_by == "TECH":
        pass

    if sort_by == "BRIGHTNESS":
        pass

    paths.append(Path(p) / f'2 {sm_type.title()}' / f'{shape.title()}s')
    if is_recommended_mask(maxres_v):
        paths.append(Path(p) / '1 Recommended' / f'{sm_type.title()}')

    for off in OFF_LEVELS:
        for on in ON_LEVElS:
            m = get_sm_matrix(on, off)

            on = on if on >= 100 else on + 100

            f_name = f'{int(maxres_v)}p_{SM_NAME}_{shape}_br{int(off):02d}'

            for p in paths:
                if not on == 100:
                    p = p / 'Brighter' / f'Brightness {round(on)}pct'
                write_mask_file(m, p / f'{f_name}.txt')


def is_recommended_mask(res, hor=False):
    return res >= 480 if not hor else 640


def write_mask_file(msk, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w") as f:
        if SM_AUTHOR:
            f.write(f'# MiSTer Shadowmask File\n')
            f.write(f'# Author: {SM_AUTHOR}\n') if not SM_AUTHOR is None else None
            f.write(f'# Name: {SM_NAME}\n') if not SM_NAME is None else None
            f.write('#\n')
            f.write(f'# dots_horizontal: {SM_DOTS_H:f}\n')
            f.write(f'# dots_vertical: {SM_DOTS_V:f}\n')
            f.write('\n')
            f.write('v2\n')
            f.write('\n')
            f.write(f'{len(msk[0])},{len(msk)}\n')
            f.write('\n')

            for row in msk:
                f.write(','.join([f'{p:0{3}x}' for p in row]))
                f.write('\n')


def set_intensity_levels(ons, offs):
    global ON_LEVElS, OFF_LEVELS

    ON_LEVElS = ons
    OFF_LEVELS = offs


def intensity_b(v):
    # TODO: optimise maybe with bitwise operation
    v = round(v if v < 100 else v)
    return round((v << 4) / 100)


def intensity_h(v):
    # TODO: optimise maybe by substituting division by bitwise op
    return (v & 0xF) * ((100 >> 4) + 1/(100 & ~(~0 << 4)))
