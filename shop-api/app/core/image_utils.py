import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps


def process_image(
    file_bytes: bytes,
    destination_folder: Path,
    dimension: int,
) -> str:

    with Image.open(BytesIO(file_bytes)) as original:
        img = ImageOps.exif_transpose(original)

        img = ImageOps.fit(
            image=img,
            size=(dimension, dimension),
            method=Image.Resampling.LANCZOS
        )

        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        filename = f"{uuid.uuid4().hex}.jpg"
        filepath = destination_folder / filename

        destination_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        img.save(
            fp=filepath,
            format="JPEG",
            quality=85,
            optimize=True
        )

        return filename


def delete_image(
        filename: str | None,
        folder: Path
) -> None:

    if filename is None:
        return

    filepath = folder / filename
    if filepath.exists():
        filepath.unlink()
