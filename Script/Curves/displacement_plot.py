import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
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

def calculate_cumulative_displacement(data, speed_cols=None, displacement_cols=None):
    """
    计算累积位移
    
    参数:
    data: DataFrame，包含速度和位移数据
    speed_cols: 元组，(x速度列名, y速度列名)
    displacement_cols: 元组，(x位移列名, y位移列名)
    
    返回:
    DataFrame，包含帧数和累积位移
    """
    result = pd.DataFrame({'Frame': range(len(data))})
    
    # 如果提供了位移列，直接计算累积位移
    if displacement_cols:
        x_disp_col, y_disp_col = displacement_cols
        result['X_Cumulative'] = data[x_disp_col].cumsum()
        result['Y_Cumulative'] = data[y_disp_col].cumsum()
    
    # 如果提供了速度列，通过积分计算位移
    elif speed_cols:
        x_speed_col, y_speed_col = speed_cols
        # 假设帧率为1，可以根据实际情况调整
        frame_rate = 1.0
        result['X_Cumulative'] = data[x_speed_col].cumsum() / frame_rate
        result['Y_Cumulative'] = data[y_speed_col].cumsum() / frame_rate
    
    return result

def plot_displacement(data, title="XY方向上的总位移", save_path=None):
    """
    绘制位移-帧数图表
    
    参数:
    data: DataFrame，包含帧数和累积位移
    title: 图表标题
    save_path: 保存图表的路径，如果为None则不保存
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    ax.plot(data['Frame'], data['X_Cumulative'], 'b-', linewidth=2, label='X方向位移')
    ax.plot(data['Frame'], data['Y_Cumulative'], 'r-', linewidth=2, label='Y方向位移')
    
    ax.set_title(title, fontproperties=font, fontsize=16)
    ax.set_xlabel('帧数', fontproperties=font, fontsize=14)
    ax.set_ylabel('总位移', fontproperties=font, fontsize=14)
    ax.grid(True)
    ax.legend(prop=font, fontsize=12)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        print(f"图表已保存至: {save_path}")
    
    plt.show()

def main():
    """
    主函数
    """
    # 数据文件路径
    # 请替换为实际的数据文件路径
    data_file = "your_data_file.csv"
    
    try:
        # 尝试加载数据
        print(f"尝试加载数据文件: {data_file}")
        print("如果这不是您的数据文件，请修改脚本中的data_file变量")
        
        # 如果文件不存在，创建示例数据用于演示
        if not os.path.exists(data_file):
            print(f"文件 {data_file} 不存在，创建示例数据用于演示")
            
            # 创建示例数据
            frames = 100
            np.random.seed(42)  # 设置随机种子以获得可重复的结果
            
            # 创建示例速度数据
            clamp_rotate_speed_x = np.random.normal(0, 0.5, frames)
            clamp_rotate_speed_y = np.random.normal(0, 0.5, frames)
            
            # 创建示例位移数据
            delta_move_x = np.random.normal(0, 0.2, frames)
            delta_move_y = np.random.normal(0, 0.2, frames)
            
            # 创建DataFrame
            data = pd.DataFrame({
                'ClampedRotateSpeed_X': clamp_rotate_speed_x,
                'ClampedRotateSpeed_Y': clamp_rotate_speed_y,
                'DeltaMove_X': delta_move_x,
                'DeltaMove_Y': delta_move_y
            })
            
            print("已创建示例数据")
        else:
            # 加载实际数据
            data = load_data(data_file)
        
        # 显示数据前几行，帮助用户确认数据格式
        print("\n数据前5行:")
        print(data.head())
        
        # 列出所有列名，帮助用户确认列名
        print("\n数据列名:")
        print(data.columns.tolist())
        
        # 根据实际数据列名设置
        # 请根据实际数据修改这些列名
        speed_cols = ('ClampedRotateSpeed_X', 'ClampedRotateSpeed_Y')
        displacement_cols = ('DeltaMove_X', 'DeltaMove_Y')
        
        # 计算累积位移
        print("\n计算累积位移...")
        
        # 使用位移数据计算累积位移
        cumulative_data = calculate_cumulative_displacement(data, 
                                                          displacement_cols=displacement_cols)
        
        # 绘制位移图表
        print("\n绘制位移图表...")
        plot_displacement(cumulative_data, save_path="displacement_plot.png")
        
        # 也可以使用速度数据计算累积位移
        print("\n使用速度数据计算累积位移...")
        cumulative_data_from_speed = calculate_cumulative_displacement(data, 
                                                                     speed_cols=speed_cols)
        
        # 绘制基于速度的位移图表
        print("\n绘制基于速度的位移图表...")
        plot_displacement(cumulative_data_from_speed, 
                         title="基于速度计算的XY方向总位移",
                         save_path="displacement_from_speed_plot.png")
        
    except Exception as e:
        print(f"发生错误: {e}")
        print("\n请检查数据文件路径和格式，并根据实际数据修改脚本中的列名")

if __name__ == "__main__":
    main()