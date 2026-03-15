"""
Voice to Text App - Icon Generator
Modern mikrofon ikonu olusturur.
"""

from PIL import Image, ImageDraw

def create_icon():
    """Modern mikrofon ikonu olustur."""

    # 256x256 boyutunda ikon
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Arka plan - gradient efekti icin daire
    # Mor-mavi gradient tonu
    center = size // 2

    # Dis daire - koyu mor
    draw.ellipse([10, 10, size-10, size-10], fill='#6B46C1')

    # Ic daire - acik mor (gradient efekti)
    draw.ellipse([30, 30, size-30, size-30], fill='#805AD5')

    # Mikrofon govdesi (beyaz)
    mic_width = 50
    mic_height = 80
    mic_left = center - mic_width // 2
    mic_top = 60

    # Mikrofon ust kismi (yuvarlak)
    draw.rounded_rectangle(
        [mic_left, mic_top, mic_left + mic_width, mic_top + mic_height],
        radius=25,
        fill='white'
    )

    # Mikrofon ic kismi (koyu cizgiler)
    line_color = '#805AD5'
    for i in range(3):
        y = mic_top + 25 + i * 18
        draw.line(
            [mic_left + 12, y, mic_left + mic_width - 12, y],
            fill=line_color,
            width=4
        )

    # Mikrofon standı - U sekli
    stand_top = mic_top + mic_height - 10
    stand_width = 80
    stand_left = center - stand_width // 2

    # U sekli icin arc
    draw.arc(
        [stand_left, stand_top, stand_left + stand_width, stand_top + 60],
        start=0, end=180,
        fill='white',
        width=8
    )

    # Dikey cizgi (stand)
    draw.line(
        [center, stand_top + 55, center, stand_top + 85],
        fill='white',
        width=8
    )

    # Taban
    draw.rounded_rectangle(
        [center - 30, stand_top + 80, center + 30, stand_top + 95],
        radius=5,
        fill='white'
    )

    # Ses dalgalari (sag ve sol)
    wave_color = 'white'

    # Sol dalga
    draw.arc([30, 70, 70, 150], start=120, end=240, fill=wave_color, width=5)
    draw.arc([15, 55, 55, 165], start=120, end=240, fill=wave_color, width=4)

    # Sag dalga
    draw.arc([size-70, 70, size-30, 150], start=-60, end=60, fill=wave_color, width=5)
    draw.arc([size-55, 55, size-15, 165], start=-60, end=60, fill=wave_color, width=4)

    # ICO formatinda kaydet (birden fazla boyut)
    img_256 = img.copy()
    img_128 = img.resize((128, 128), Image.Resampling.LANCZOS)
    img_64 = img.resize((64, 64), Image.Resampling.LANCZOS)
    img_48 = img.resize((48, 48), Image.Resampling.LANCZOS)
    img_32 = img.resize((32, 32), Image.Resampling.LANCZOS)
    img_16 = img.resize((16, 16), Image.Resampling.LANCZOS)

    # ICO olarak kaydet
    img_256.save(
        'icon.ico',
        format='ICO',
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    )

    print("icon.ico olusturuldu!")
    return 'icon.ico'

if __name__ == "__main__":
    create_icon()
