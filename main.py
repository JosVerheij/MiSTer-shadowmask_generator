import shutil
from pathlib import PurePath, Path

from organiser import Organiser


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


# Delete all filters and regenerate them
if Path(OUTPUT_DIRECTORY).exists():
    shutil.rmtree(OUTPUT_DIRECTORY)

o = Organiser()
o.collect_mask_files(MASK_ROOT)
o.generate_mask_files(OUTPUT_DIRECTORY)
