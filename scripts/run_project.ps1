param(
    [string]$SourceDir = "",
    [int]$Epochs = 20,
    [int]$BatchSize = 8,
    [int]$ImageSize = 320
)

$ErrorActionPreference = "Stop"

# 仓库根目录
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$DataDir = Join-Path $RepoRoot "data"
$TrainImages = Join-Path $DataDir "images\train"

# 如果指定了原始图片目录，则先重新生成数据集；
# 如果没有指定，但仓库内已经有 data/images/train，则直接使用现有数据集训练。
if ($SourceDir) {
    python (Join-Path $RepoRoot "scripts\prepare_food_dataset.py") `
        --source-dir $SourceDir `
        --out-dir $DataDir
} elseif ($env:DIP_PROJECT_SOURCE_DIR) {
    python (Join-Path $RepoRoot "scripts\prepare_food_dataset.py") `
        --source-dir $env:DIP_PROJECT_SOURCE_DIR `
        --out-dir $DataDir
} elseif (-not (Test-Path -LiteralPath $TrainImages)) {
    throw "仓库内没有可用数据集；请使用 -SourceDir 指定原始图片目录。"
} else {
    Write-Host "检测到仓库内已有 data 数据集，跳过数据生成步骤。"
}

Push-Location (Join-Path $RepoRoot "yolov5")
try {
    # 训练 YOLOv5s
    python train.py `
        --data data/MyDataSpec.yaml `
        --cfg models/MyModelSpec.yaml `
        --weights pretrained/yolov5s.pt `
        --epochs $Epochs `
        --batch-size $BatchSize `
        --img $ImageSize `
        --workers 0 `
        --project ..\runs_train `
        --name food_512_e20 `
        --freeze 10 `
        --exist-ok

    # 使用最佳权重对测试集做检测
    python detect.py `
        --weights ..\runs_train\food_512_e20\weights\best.pt `
        --source ..\data\images\test `
        --img $ImageSize `
        --conf-thres 0.05 `
        --project ..\runs_detect `
        --name food_512_test_e20 `
        --exist-ok `
        --save-txt

    # 使用最佳权重对测试集做评估
    python val.py `
        --weights ..\runs_train\food_512_e20\weights\best.pt `
        --data data\MyDataSpec.yaml `
        --task test `
        --img $ImageSize `
        --project ..\runs_val `
        --name food_512_test_e20 `
        --exist-ok
} finally {
    Pop-Location
}
