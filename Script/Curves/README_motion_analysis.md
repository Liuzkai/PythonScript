# 运动数据分析工具

这个项目包含两个Python脚本，用于分析和可视化运动数据，特别是处理ClampedRotateSpeed（速度）和DeltaMove（位移）数据。

## 文件说明

1. `displacement_plot.py` - 基本的位移数据可视化脚本
2. `motion_analysis.py` - 高级运动分析和可视化脚本，提供更多功能和选项

## 功能特点

### displacement_plot.py

- 加载CSV、Excel或JSON格式的数据
- 计算累积位移
- 绘制XY方向上的总位移图表
- 支持从速度数据计算位移

### motion_analysis.py

- 命令行参数支持，便于灵活使用
- 自动创建示例数据用于演示
- 计算并可视化累积位移
- 绘制运动轨迹图
- 从速度数据计算位移
- 比较直接位移和基于速度计算的位移
- 提供详细的运动统计分析

## 安装依赖

这些脚本需要以下Python库：

```bash
pip install numpy matplotlib pandas
```

## 使用方法

### 基本用法

1. 使用示例数据运行分析：

```bash
python motion_analysis.py
```

2. 分析自己的数据文件：

```bash
python motion_analysis.py --file your_data_file.csv
```

### 高级用法

指定列名和其他参数：

```bash
python motion_analysis.py --file your_data_file.csv --speed-x "SpeedX" --speed-y "SpeedY" --disp-x "DisplacementX" --disp-y "DisplacementY" --frame-rate 30 --output "my_analysis"
```

## 参数说明

`motion_analysis.py` 支持以下命令行参数：

- `-f, --file`: 数据文件路径 (CSV, Excel, JSON)
- `--speed-x`: X方向速度列名 (默认: ClampedRotateSpeed_X)
- `--speed-y`: Y方向速度列名 (默认: ClampedRotateSpeed_Y)
- `--disp-x`: X方向位移列名 (默认: DeltaMove_X)
- `--disp-y`: Y方向位移列名 (默认: DeltaMove_Y)
- `--frame-rate`: 帧率 (默认: 60 FPS)
- `--output`: 输出文件名前缀 (默认: motion_analysis_results)

## 输出说明

脚本会生成以下输出：

1. 控制台输出：
   - 数据加载信息
   - 数据前5行预览
   - 列名列表
   - 运动分析统计结果

2. 图表输出：
   - 位移-帧数图表
   - 运动轨迹图
   - 基于速度计算的位移图表
   - 位移差异比较图表（如果同时有速度和位移数据）

## 示例数据格式

脚本期望的数据格式示例：

| Frame | ClampedRotateSpeed_X | ClampedRotateSpeed_Y | DeltaMove_X | DeltaMove_Y |
|-------|----------------------|----------------------|-------------|-------------|
| 0     | 0.0                  | 0.0                  | 0.0         | 0.0         |
| 1     | 0.1                  | 0.05                 | 0.00167     | 0.00083     |
| 2     | 0.15                 | 0.08                 | 0.00250     | 0.00133     |
| ...   | ...                  | ...                  | ...         | ...         |

## 注意事项

- 如果数据文件不存在或未指定，脚本会自动创建示例数据用于演示
- 如果指定的列名在数据中不存在，脚本会发出警告并尝试使用可用的列
- 帧率参数影响从速度计算位移的结果，请确保设置正确的值

## 示例输出

运行脚本后，您将获得类似以下的分析结果：

```
===== 运动分析结果 =====
总帧数: 600
总时间: 10.00 秒
最终X位移: 1.2345
最终Y位移: 0.5678
总位移: 1.3579
平均X速度: 0.1234
平均Y速度: 0.0567
最大X速度: 0.2345
最大Y速度: 0.1234
```

以及多个可视化图表，帮助您理解运动数据。