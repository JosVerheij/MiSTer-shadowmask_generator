import shutil
from pathlib import Path

import mask as msk


OUTPUT_DIRECTORY = (
    Path(__file__).parents[1] /
    "ShadowMasks_MiSTer" /
    "Shadow_Masks" /
    "Jovec Masks"
    )

if Path(OUTPUT_DIRECTORY).exists():
    shutil.rmtree(OUTPUT_DIRECTORY)

msk.set_intensity_levels(
    [100, 110, 125, 137.5, 150],
    [25, 37.5, 50]
    )
for path in sorted(Path('masks').glob('**/*.txt')):
    msk.get_mask_file(path)
    msk.new_mask_file(OUTPUT_DIRECTORY, 1440)
    msk.new_mask_file(OUTPUT_DIRECTORY, 1080)
    msk.new_mask_file(OUTPUT_DIRECTORY, 720)
