import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import argparse
import matplotlib as mpl
from matplotlib.font_manager import FontProperties

# 设置中文字体支持
try:
    # 尝试使用微软雅黑字体
    font = FontProperties(fname=r"C:\Windows\Fonts\msyh.ttc")
    plt.rcParams['font.family'] = ['Microsoft YaHei']
    # 解决负号显示问题
    mpl.rcParams['axes.unicode_minus'] = False
except:
    # 如果找不到微软雅黑，使用matplotlib内置的中文字体
    print("未找到微软雅黑字体，使用matplotlib内置字体")
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    mpl.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='分析运动数据并绘制位移图表')
    parser.add_argument('-f', '--file', type=str, default='',
                        help='数据文件路径 (CSV, Excel, JSON)')
    parser.add_argument('--speed-x', type=str, default='ClampedRotateSpeed_X',
                        help='X方向速度列名')
    parser.add_argument('--speed-y', type=str, default='ClampedRotateSpeed_Y',
                        help='Y方向速度列名')
    parser.add_argument('--disp-x', type=str, default='DeltaMove_X',
                        help='X方向位移列名')
    parser.add_argument('--disp-y', type=str, default='DeltaMove_Y',
                        help='Y方向位移列名')
    parser.add_argument('--frame-rate', type=float, default=60.0,
                        help='帧率 (默认: 60 FPS)')
    parser.add_argument('--output', type=str, default='motion_analysis_results',
                        help='输出文件名前缀')
    return parser.parse_args()

def load_data(file_path):
    """
    加载数据文件
    根据文件扩展名自动选择加载方法
    """
    _, ext = os.path.splitext(file_path)
    
    if ext.lower() == '.csv':
        return pd.read_csv(file_path)
    elif ext.lower() == '.xlsx' or ext.lower() == '.xls':
        return pd.read_excel(file_path)
    elif ext.lower() == '.json':
        return pd.read_json(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {ext}")

def create_sample_data(frames=600, frame_rate=60.0):
    """创建示例数据用于演示"""
    np.random.seed(42)  # 设置随机种子以获得可重复的结果
    
    # 时间序列（秒）
    time = np.arange(frames) / frame_rate
    
    # 创建更真实的运动模式
    # X方向：先加速，然后减速，最后保持恒定速度
    # Y方向：正弦波模式
    
    # 速度数据
    speed_x = np.zeros(frames)
    for i in range(frames):
        if i < frames/3:
            speed_x[i] = 0.05 * i / frame_rate  # 加速
        elif i < 2*frames/3:
            speed_x[i] = 0.05 * (frames/3) / frame_rate - 0.05 * (i - frames/3) / frame_rate  # 减速
        else:
            speed_x[i] = 0.01  # 恒定速度
    
    speed_y = 0.03 * np.sin(2 * np.pi * time / 5)  # 5秒周期的正弦波
    
    # 添加一些随机噪声
    speed_x += np.random.normal(0, 0.005, frames)
    speed_y += np.random.normal(0, 0.005, frames)
    
    # 位移数据（基于速度积分）
    disp_x = np.zeros(frames)
    disp_y = np.zeros(frames)
    
    for i in range(1, frames):
        disp_x[i] = speed_x[i] / frame_rate
        disp_y[i] = speed_y[i] / frame_rate
    
    # 创建DataFrame
    data = pd.DataFrame({
        'Frame': np.arange(frames),
        'Time': time,
        'ClampedRotateSpeed_X': speed_x,
        'ClampedRotateSpeed_Y': speed_y,
        'DeltaMove_X': disp_x,
        'DeltaMove_Y': disp_y
    })
    
    return data

def calculate_cumulative_displacement(data, disp_x_col, disp_y_col):
    """
    计算累积位移
    
    参数:
    data: DataFrame，包含位移数据
    disp_x_col: X方向位移列名
    disp_y_col: Y方向位移列名
    
    返回:
    DataFrame，包含帧数和累积位移
    """
    result = data.copy()
    
    # 计算累积位移
    result['X_Cumulative'] = data[disp_x_col].cumsum()
    result['Y_Cumulative'] = data[disp_y_col].cumsum()
    
    # 计算合成位移（欧几里得距离）
    result['Total_Displacement'] = np.sqrt(result['X_Cumulative']**2 + result['Y_Cumulative']**2)
    
    return result

def calculate_displacement_from_speed(data, speed_x_col, speed_y_col, frame_rate):
    """
    从速度数据计算位移
    
    参数:
    data: DataFrame，包含速度数据
    speed_x_col: X方向速度列名
    speed_y_col: Y方向速度列名
    frame_rate: 帧率
    
    返回:
    DataFrame，包含帧数和累积位移
    """
    result = data.copy()
    
    # 计算每帧的位移
    result['DeltaMove_X_Calculated'] = data[speed_x_col] / frame_rate
    result['DeltaMove_Y_Calculated'] = data[speed_y_col] / frame_rate
    
    # 计算累积位移
    result['X_Cumulative_From_Speed'] = result['DeltaMove_X_Calculated'].cumsum()
    result['Y_Cumulative_From_Speed'] = result['DeltaMove_Y_Calculated'].cumsum()
    
    # 计算合成位移（欧几里得距离）
    result['Total_Displacement_From_Speed'] = np.sqrt(
        result['X_Cumulative_From_Speed']**2 + result['Y_Cumulative_From_Speed']**2)
    
    return result

def plot_displacement(data, x_col, y_col, title, xlabel='帧数', ylabel='总位移', save_path=None):
    """
    绘制位移图表
    
    参数:
    data: DataFrame，包含帧数和累积位移
    x_col: X轴数据列名
    y_col: 要绘制的Y轴数据列名（可以是列表）
    title: 图表标题
    xlabel: X轴标签
    ylabel: Y轴标签
    save_path: 保存图表的路径，如果为None则不保存
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    if isinstance(y_col, list):
        for col, color, label in zip(y_col, ['b', 'r', 'g', 'm'], ['X方向位移', 'Y方向位移', '合成位移', '其他']):
            if col in data.columns:
                ax.plot(data[x_col], data[col], f'{color}-', linewidth=2, label=label)
    else:
        ax.plot(data[x_col], data[y_col], 'b-', linewidth=2)
    
    ax.set_title(title, fontproperties=font, fontsize=16)
    ax.set_xlabel(xlabel, fontproperties=font, fontsize=14)
    ax.set_ylabel(ylabel, fontproperties=font, fontsize=14)
    ax.grid(True)
    ax.legend(prop=font, fontsize=12)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        print(f"图表已保存至: {save_path}")
    
    plt.show()

def plot_trajectory(data, x_col, y_col, title="运动轨迹", save_path=None):
    """
    绘制运动轨迹图
    
    参数:
    data: DataFrame，包含位移数据
    x_col: X位移列名
    y_col: Y位移列名
    title: 图表标题
    save_path: 保存图表的路径，如果为None则不保存
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # 绘制轨迹
    ax.plot(data[x_col], data[y_col], 'b-', linewidth=1.5)
    
    # 标记起点和终点
    ax.plot(data[x_col].iloc[0], data[y_col].iloc[0], 'go', markersize=10, label='起点')
    ax.plot(data[x_col].iloc[-1], data[y_col].iloc[-1], 'ro', markersize=10, label='终点')
    
    # 添加箭头指示方向
    n = len(data)
    arrow_indices = [int(n*0.25), int(n*0.5), int(n*0.75)]
    for i in arrow_indices:
        if i < n - 1:
            ax.annotate('', 
                       xy=(data[x_col].iloc[i+1], data[y_col].iloc[i+1]),
                       xytext=(data[x_col].iloc[i], data[y_col].iloc[i]),
                       arrowprops=dict(arrowstyle='->', lw=1.5, color='r'))
    
    ax.set_title(title, fontproperties=font, fontsize=16)
    ax.set_xlabel('X位移', fontproperties=font, fontsize=14)
    ax.set_ylabel('Y位移', fontproperties=font, fontsize=14)
    ax.grid(True)
    ax.axis('equal')  # 确保X和Y轴比例相同
    ax.legend(prop=font, fontsize=12)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        print(f"轨迹图已保存至: {save_path}")
    
    plt.show()

def analyze_motion(data, results, frame_rate):
    """
    分析运动数据并打印统计信息
    
    参数:
    data: 原始数据DataFrame
    results: 计算结果DataFrame
    frame_rate: 帧率
    
    返回:
    统计信息字典
    """
    stats = {}
    
    # 总帧数和时间
    total_frames = len(data)
    total_time = total_frames / frame_rate
    stats['total_frames'] = total_frames
    stats['total_time'] = total_time
    
    # 位移统计
    final_x = results['X_Cumulative'].iloc[-1]
    final_y = results['Y_Cumulative'].iloc[-1]
    total_displacement = results['Total_Displacement'].iloc[-1]
    
    stats['final_x'] = final_x
    stats['final_y'] = final_y
    stats['total_displacement'] = total_displacement
    
    # 速度统计
    if 'ClampedRotateSpeed_X' in data.columns and 'ClampedRotateSpeed_Y' in data.columns:
        avg_speed_x = data['ClampedRotateSpeed_X'].mean()
        avg_speed_y = data['ClampedRotateSpeed_Y'].mean()
        max_speed_x = data['ClampedRotateSpeed_X'].abs().max()
        max_speed_y = data['ClampedRotateSpeed_Y'].abs().max()
        
        stats['avg_speed_x'] = avg_speed_x
        stats['avg_speed_y'] = avg_speed_y
        stats['max_speed_x'] = max_speed_x
        stats['max_speed_y'] = max_speed_y
    
    # 打印统计信息
    print("\n===== 运动分析结果 =====")
    print(f"总帧数: {total_frames}")
    print(f"总时间: {total_time:.2f} 秒")
    print(f"最终X位移: {final_x:.4f}")
    print(f"最终Y位移: {final_y:.4f}")
    print(f"总位移: {total_displacement:.4f}")
    
    if 'avg_speed_x' in stats:
        print(f"平均X速度: {avg_speed_x:.4f}")
        print(f"平均Y速度: {avg_speed_y:.4f}")
        print(f"最大X速度: {max_speed_x:.4f}")
        print(f"最大Y速度: {max_speed_y:.4f}")
    
    return stats

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 数据文件路径
    data_file = args.file
    
    try:
        # 如果文件不存在或未指定，创建示例数据
        if not data_file or not os.path.exists(data_file):
            if data_file:
                print(f"文件 {data_file} 不存在，创建示例数据用于演示")
            else:
                print("未指定数据文件，创建示例数据用于演示")
            
            # 创建示例数据
            data = create_sample_data(frames=600, frame_rate=args.frame_rate)
            print("已创建示例数据")
        else:
            # 加载实际数据
            print(f"加载数据文件: {data_file}")
            data = load_data(data_file)
        
        # 显示数据前几行
        print("\n数据前5行:")
        print(data.head())
        
        # 列出所有列名
        print("\n数据列名:")
        print(data.columns.tolist())
        
        # 获取列名
        speed_x_col = args.speed_x
        speed_y_col = args.speed_y
        disp_x_col = args.disp_x
        disp_y_col = args.disp_y
        
        # 检查列是否存在
        missing_cols = []
        for col, name in [(speed_x_col, "X方向速度"), 
                          (speed_y_col, "Y方向速度"),
                          (disp_x_col, "X方向位移"), 
                          (disp_y_col, "Y方向位移")]:
            if col not in data.columns:
                missing_cols.append(f"{name} ({col})")
        
        if missing_cols:
            print(f"\n警告: 以下列在数据中不存在: {', '.join(missing_cols)}")
            print("请检查列名或使用--speed-x, --speed-y, --disp-x, --disp-y参数指定正确的列名")
            print("继续使用可用的列...")
        
        # 计算累积位移
        print("\n计算累积位移...")
        
        # 检查位移列是否存在
        if disp_x_col in data.columns and disp_y_col in data.columns:
            results = calculate_cumulative_displacement(data, disp_x_col, disp_y_col)
            
            # 绘制位移图表
            print("\n绘制位移图表...")
            
            # 绘制X和Y方向的累积位移
            plot_displacement(results, 'Frame', ['X_Cumulative', 'Y_Cumulative', 'Total_Displacement'], 
                             "XY方向上的总位移", 
                             save_path=f"{args.output}_displacement.png")
            
            # 绘制运动轨迹
            plot_trajectory(results, 'X_Cumulative', 'Y_Cumulative', 
                           "运动轨迹图", 
                           save_path=f"{args.output}_trajectory.png")
            
            # 分析运动
            stats = analyze_motion(data, results, args.frame_rate)
        else:
            print(f"位移列 {disp_x_col} 或 {disp_y_col} 不存在，跳过位移分析")
        
        # 检查速度列是否存在
        if speed_x_col in data.columns and speed_y_col in data.columns:
            # 从速度计算位移
            print("\n从速度数据计算位移...")
            speed_results = calculate_displacement_from_speed(
                data, speed_x_col, speed_y_col, args.frame_rate)
            
            # 绘制基于速度的位移图表
            print("\n绘制基于速度的位移图表...")
            plot_displacement(speed_results, 'Frame', 
                             ['X_Cumulative_From_Speed', 'Y_Cumulative_From_Speed', 'Total_Displacement_From_Speed'], 
                             "基于速度计算的XY方向总位移", 
                             save_path=f"{args.output}_displacement_from_speed.png")
            
            # 绘制基于速度的运动轨迹
            plot_trajectory(speed_results, 'X_Cumulative_From_Speed', 'Y_Cumulative_From_Speed', 
                           "基于速度计算的运动轨迹图", 
                           save_path=f"{args.output}_trajectory_from_speed.png")
            
            # 如果同时有位移和速度数据，比较两者
            if 'X_Cumulative' in results.columns and 'Y_Cumulative' in results.columns:
                print("\n比较直接位移和基于速度计算的位移...")
                
                # 计算差异
                comparison = results.copy()
                comparison['X_Diff'] = results['X_Cumulative'] - speed_results['X_Cumulative_From_Speed']
                comparison['Y_Diff'] = results['Y_Cumulative'] - speed_results['Y_Cumulative_From_Speed']
                
                # 绘制差异图表
                plot_displacement(comparison, 'Frame', ['X_Diff', 'Y_Diff'], 
                                 "位移差异 (直接位移 - 基于速度计算的位移)", 
                                 ylabel='位移差异', 
                                 save_path=f"{args.output}_displacement_diff.png")
        else:
            print(f"速度列 {speed_x_col} 或 {speed_y_col} 不存在，跳过速度分析")
        
        print("\n分析完成！")
        
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        print("\n请检查数据文件路径和格式，并根据实际数据修改参数")

if __name__ == "__main__":
    main()