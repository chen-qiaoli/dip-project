# 数字图像处理期中项目：餐饮食物目标检测

本仓库用于提交数字图像处理课程期中 project 的代码和可运行数据。项目基于 YOLOv5s 完成四类餐饮食物目标检测。

## 仓库内容

```text
.
├── README.md
├── requirements.txt
├── scripts
│   ├── prepare_food_dataset.py
│   └── run_project.ps1
├── data
│   ├── classes.txt
│   ├── images/train|val|test
│   └── labels/train|val|test
└── yolov5
    ├── train.py
    ├── detect.py
    ├── val.py
    ├── data/MyDataSpec.yaml
    ├── models/MyModelSpec.yaml
    ├── pretrained/yolov5s.pt
    ├── models/
    └── utils/
```

仓库中已经包含生成后的 YOLO 格式数据集和 YOLOv5s 预训练权重，可以直接运行训练、检测和测试集评估。

## 类别

本项目检测 4 类食物：

```text
0 sushi
1 noodle
2 rice_meal
3 cake
```

## 环境安装

建议使用 Python 3.9 或 3.10。安装依赖：

```powershell
python -m pip install -r requirements.txt
```

如果机器没有 GPU，也可以用 CPU 运行，只是训练会比较慢。

## 直接运行

仓库内已经有 `data/` 数据集，直接运行：

```powershell
.\scripts\run_project.ps1
```

默认会执行：

1. 使用 `yolov5/pretrained/yolov5s.pt` 作为预训练权重；
2. 训练 20 个 epoch；
3. 使用最佳权重对测试集做检测；
4. 使用最佳权重对测试集做评估。

## 重新生成数据集后运行

如果要从原始照片重新生成数据集，可以指定原始图片目录：

```powershell
.\scripts\run_project.ps1 -SourceDir "D:\SYSU\数字图像处理\project images"
```

也可以只生成数据集：

```powershell
python scripts\prepare_food_dataset.py --source-dir "D:\SYSU\数字图像处理\project images" --out-dir data
```

## 手动运行命令

```powershell
cd yolov5
python train.py --data data/MyDataSpec.yaml --cfg models/MyModelSpec.yaml --weights pretrained/yolov5s.pt --epochs 20 --batch-size 8 --img 320 --workers 0 --project ..\runs_train --name food_512_e20 --freeze 10 --exist-ok
python detect.py --weights ..\runs_train\food_512_e20\weights\best.pt --source ..\data\images\test --img 320 --conf-thres 0.05 --project ..\runs_detect --name food_512_test_e20 --exist-ok --save-txt
python val.py --weights ..\runs_train\food_512_e20\weights\best.pt --data data\MyDataSpec.yaml --task test --img 320 --project ..\runs_val --name food_512_test_e20 --exist-ok
```

运行后会重新生成 `runs_train/`、`runs_detect/` 和 `runs_val/`。

