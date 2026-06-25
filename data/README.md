# 餐饮食物目标检测数据集

本数据集用于数字图像处理课程 YOLOv5s 大作业。
原始图片来自 `D:/SYSU/数字图像处理/project images` 中的个人食物照片。
类别包括 `sushi`、`noodle`、`rice_meal`、`cake`。
所有图片先裁剪/缩放为 `512x512`，再生成灰度化、亮度增强和锐化版本。
标签为 YOLO 格式，每张图片标注一个主要食物区域。

各数据集图片数量：
- train: 128 张，{'sushi': 40, 'noodle': 32, 'rice_meal': 32, 'cake': 24}
- val: 28 张，{'sushi': 8, 'noodle': 8, 'rice_meal': 8, 'cake': 4}
- test: 24 张，{'sushi': 8, 'noodle': 4, 'rice_meal': 8, 'cake': 4}

未纳入训练的照片：
- 北京烤鸭.jpg
- 南瓜天妇罗.jpg
- 木姜子水煮牛肉.jpg
- 肠粉.jpg
- 鸡丝干包榴莲.jpg
