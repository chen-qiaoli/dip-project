from pathlib import Path
import os
import argparse
import random
import shutil

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COURSE_ROOT = PROJECT_ROOT.parent.parent
DEFAULT_SOURCE_DIR = COURSE_ROOT / "project images"
DEFAULT_OUT = PROJECT_ROOT / "data"
OUTPUT_SIZE = (512, 512)

CLASS_NAMES = ["sushi", "noodle", "rice_meal", "cake"]
CLASS_TO_ID = {name: idx for idx, name in enumerate(CLASS_NAMES)}

FILE_CLASSES = {
    "也是寿司郎的寿司.jpg": "sushi",
    "还是寿司.jpg": "sushi",
    "很多焦糖鹅肝.jpg": "sushi",
    "很多寿司.jpg": "sushi",
    "很多寿司郎的寿司.jpg": "sushi",
    "焦糖鹅肝.jpg": "sushi",
    "牛油果金枪鱼寿司.jpg": "sushi",
    "三文鱼寿司.jpg": "sushi",
    "寿司.jpg": "sushi",
    "香葱三文鱼腩.jpg": "sushi",
    "一堆寿司.jpg": "sushi",
    "柚子醋金枪鱼寿司.jpg": "sushi",
    "这也是焦糖鹅肝.jpg": "sushi",
    "这也是寿司.jpg": "sushi",

    "潮汕牛肉粿条.jpg": "noodle",
    "家里的牛肉粿条.jpg": "noodle",
    "螺蛳粉.jpg": "noodle",
    "抹茶饮料+日式豚骨拉面.jpg": "noodle",
    "牛腩面.jpg": "noodle",
    "牛肉粿条.jpg": "noodle",
    "寿司郎 温泉蛋山药泥乌冬.jpg": "noodle",
    "葱油拌面.jpg": "noodle",
    "番茄鸡蛋油泼面.jpg": "noodle",
    "自己煮的番茄鸡蛋面.jpg": "noodle",
    "芝士熟虾+温泉蛋山药泥乌冬.jpg": "noodle",

    "黯然销魂饭.jpg": "rice_meal",
    "叉烧饭.jpg": "rice_meal",
    "叉烧拼沙姜鸡.jpg": "rice_meal",
    "咖喱鸡肉饭.jpg": "rice_meal",
    "咖喱猪颈肉饭.jpg": "rice_meal",
    "卤鹅饭.jpg": "rice_meal",
    "日式烧鸟饭.jpg": "rice_meal",
    "手撕鸡饭.jpg": "rice_meal",
    "泰式打抛饭.jpg": "rice_meal",
    "西兰花芥兰牛肉饭.jpg": "rice_meal",
    "猪排饭.jpg": "rice_meal",
    "自己diy的寿司饭.jpg": "rice_meal",

    "芭乐蛋糕.jpg": "cake",
    "芭乐蛋糕2.jpg": "cake",
    "草莓蛋糕.jpg": "cake",
    "草莓蛋糕2.jpg": "cake",
    "栗子蛋糕.jpg": "cake",
    "抹茶草莓蛋糕.jpg": "cake",
    "抹茶芒果麻薯蛋糕.jpg": "cake",
    "小草莓蛋糕.jpg": "cake",
}

VARIANTS = [
    ("orig", None),
    ("gray", "gray"),
    ("bright115", ("brightness", 1.15)),
    ("sharp", "sharp"),
]


def slug_name(path):
    return path.stem.replace(" ", "_").replace("+", "_")


def load_square_image(path):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img).convert("RGB")
    return ImageOps.fit(img, OUTPUT_SIZE, method=Image.Resampling.LANCZOS)


def transform_image(img, op):
    if op is None:
        return img.copy()
    if op == "gray":
        return ImageOps.grayscale(img).convert("RGB")
    if op == "sharp":
        return img.filter(ImageFilter.SHARPEN)
    kind, value = op
    if kind == "brightness":
        return ImageEnhance.Brightness(img).enhance(value)
    raise ValueError(f"Unknown transform: {op}")


def split_by_class(files_by_class, seed):
    random.seed(seed)
    split = {"train": [], "val": [], "test": []}
    for class_name, files in sorted(files_by_class.items()):
        files = list(files)
        random.shuffle(files)
        n = len(files)
        train_n = max(1, round(n * 0.7))
        val_n = max(1, round(n * 0.15))
        if train_n + val_n >= n:
            val_n = 1
            train_n = max(1, n - 2)
        split["train"].extend(files[:train_n])
        split["val"].extend(files[train_n:train_n + val_n])
        split["test"].extend(files[train_n + val_n:])
    return split


def write_label(path, class_name):
    cls = CLASS_TO_ID[class_name]
    # 主体食物区域基本都位于画面中央。这里用一个较大的中心框近似主目标区域。
    path.write_text(f"{cls} 0.500000 0.500000 0.860000 0.860000\n", encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="将原始食物照片整理为 YOLO 格式数据集。")
    parser.add_argument(
        "--source-dir",
        default=os.environ.get("DIP_PROJECT_SOURCE_DIR", str(DEFAULT_SOURCE_DIR)),
        help="原始食物照片所在文件夹。",
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT),
        help="输出数据集文件夹；若已存在会被重新生成。",
    )
    parser.add_argument("--seed", type=int, default=25215102, help="训练集、验证集、测试集划分随机种子。")
    return parser.parse_args()


def main():
    args = parse_args()
    source_dir = Path(args.source_dir)
    out = Path(args.out_dir)

    if not source_dir.exists():
        raise FileNotFoundError(f"找不到原始图片文件夹：{source_dir}")

    if out.exists():
        shutil.rmtree(out)

    for split in ("train", "val", "test"):
        (out / "images" / split).mkdir(parents=True, exist_ok=True)
        (out / "labels" / split).mkdir(parents=True, exist_ok=True)

    files_by_class = {name: [] for name in CLASS_NAMES}
    skipped = []
    for path in sorted(source_dir.glob("*.jpg"), key=lambda p: p.name):
        class_name = FILE_CLASSES.get(path.name)
        if class_name is None:
            skipped.append(path.name)
            continue
        files_by_class[class_name].append(path)

    split_files = split_by_class(files_by_class, args.seed)
    summary = []
    for split, paths in split_files.items():
        for path in paths:
            class_name = FILE_CLASSES[path.name]
            base_img = load_square_image(path)
            for suffix, op in VARIANTS:
                out_name = f"{slug_name(path)}_{suffix}"
                out_img = transform_image(base_img, op)
                out_img.save(out / "images" / split / f"{out_name}.jpg", quality=92)
                write_label(out / "labels" / split / f"{out_name}.txt", class_name)
                summary.append((split, class_name, out_name))

    classes_text = "\n".join(CLASS_NAMES) + "\n"
    (out / "classes.txt").write_text(classes_text, encoding="utf-8")
    for split in ("train", "val", "test"):
        (out / "labels" / split / "classes.txt").write_text(classes_text, encoding="utf-8")

    counts = {split: {name: 0 for name in CLASS_NAMES} for split in ("train", "val", "test")}
    for split, class_name, _ in summary:
        counts[split][class_name] += 1

    readme = [
        "# 餐饮食物目标检测数据集",
        "",
        "本数据集用于数字图像处理课程 YOLOv5s 大作业。",
        "原始图片来自 `D:/SYSU/数字图像处理/project images` 中的个人食物照片。",
        "类别包括 `sushi`、`noodle`、`rice_meal`、`cake`。",
        "所有图片先裁剪/缩放为 `512x512`，再生成灰度化、亮度增强和锐化版本。",
        "标签为 YOLO 格式，每张图片标注一个主要食物区域。",
        "",
        "各数据集图片数量：",
    ]
    for split in ("train", "val", "test"):
        total = sum(counts[split].values())
        readme.append(f"- {split}: {total} 张，{counts[split]}")
    readme.append("")
    readme.append("未纳入训练的照片：")
    for name in skipped:
        readme.append(f"- {name}")
    (out / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")

    print(f"原始图片数量：{len(list(source_dir.glob('*.jpg')))}")
    print(f"纳入数据集的原始图片数量：{sum(len(v) for v in files_by_class.values())}")
    print(f"跳过图片数量：{len(skipped)}")
    for split in ("train", "val", "test"):
        print(split, counts[split], "合计", sum(counts[split].values()))
    print(f"数据集输出位置：{out}")


if __name__ == "__main__":
    main()
