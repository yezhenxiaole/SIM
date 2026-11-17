# -*- coding: utf-8 -*-
"""
生成"0 / 1 交替条纹"的 1bit 图像（共 6 张）

  A. 1920 x 1     一维条纹（单行），周期 2 / 4 / 8   -> 3 张
  B. 1920 x 1080  二维条纹（按列方向周期，每行相同），周期 2 / 4 / 8 -> 3 张

周期含义（像素值 0=黑, 1=白）：
    period = 2 : 0,1,0,1,0,1 ...
    period = 4 : 0,0,1,1,0,0,1,1 ...
    period = 8 : 0,0,0,0,1,1,1,1 ...

运行环境：conda 环境 SIM（Python 3.11 + numpy + pillow）
运行方式（二选一）：
    D:\\miniconda\\envs\\SIM\\python.exe gen_period_images.py
    conda activate SIM  然后  python gen_period_images.py
"""

from pathlib import Path

import numpy as np
from PIL import Image

# ==================== 只需修改下面两个配置 ====================
OUTPUT_DIR = Path(r"G:\实验室文档\SIM\output")      # 保存目录，改成你自己的路径
FILE_NAME_TEMPLATE = "pattern_{kind}_{h}x{w}_period_{period}.bmp"   # 命名规则，自己改
# 可用占位符：{kind} 类型(1d/2d)  {w} 宽  {h} 高  {period} 周期
INVERT = False        # True 则黑白反转（0/1 互换）
# ==============================================================

WIDTH = 1920
HEIGHT_1D = 1
HEIGHT_2D = 1080
PERIODS = (2, 4, 8)


def stripe_row(width: int, period: int, invert: bool = False) -> np.ndarray:
    """生成一行 0/1 交替数据，长度 = width，返回 bool 数组（True 视为 1）。"""
    if period <= 0 or period % 2 != 0:
        raise ValueError("周期必须是正偶数")
    half = period // 2
    x = np.arange(width)
    row = ((x // half) % 2).astype(bool)      # period=4 -> 0,0,1,1 ...
    if invert:
        row = ~row
    return row


def make_image(width: int, height: int, period: int, invert: bool = False) -> Image.Image:
    """按列方向做周期条纹，所有行内容一致，输出 mode='1'（1bit）图像。"""
    row = stripe_row(width, period, invert)
    arr = np.tile(row, (height, 1))           # height x width 的 bool 数组
    return Image.fromarray(arr)               # bool 数组直接得到 1bit 图像


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tasks = [("1d", WIDTH, HEIGHT_1D, p) for p in PERIODS] + \
            [("2d", WIDTH, HEIGHT_2D, p) for p in PERIODS]

    for kind, w, h, period in tasks:
        img = make_image(w, h, period, INVERT)
        name = FILE_NAME_TEMPLATE.format(kind=kind, w=w, h=h, period=period)
        path = OUTPUT_DIR / name
        img.save(path, format="BMP")

        # 回读校验，确认是真正的 1bit 图
        with Image.open(path) as chk:
            size, mode = chk.size, chk.mode
            first_px = [chk.getpixel((i, 0)) for i in range(min(w, 8))]
        print(f"{path}\n    尺寸={size}  模式={mode}  "
              f"文件大小={path.stat().st_size} 字节  前8像素={first_px}")

    print("\n全部生成完成。")


if __name__ == "__main__":
    main()