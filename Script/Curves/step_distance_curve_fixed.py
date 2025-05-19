import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
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

# 创建图形和子图
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[3, 1])
plt.subplots_adjust(left=0.1, bottom=0.2, hspace=0.3)  # 为滑块留出空间

# 初始参数
initial_speed = 0  # 初始速度
total_distance_init = 100  # 总距离初始值
acceleration_init = 5  # 加速度初始值
max_speed_init = 9  # 最大速度初始值
steps_per_second = 60  # 每秒的步数

# 创建滑块的位置
ax_distance = plt.axes([0.25, 0.1, 0.65, 0.03])
ax_acceleration = plt.axes([0.25, 0.06, 0.65, 0.03])
ax_max_speed = plt.axes([0.25, 0.02, 0.65, 0.03])

# 创建滑块
s_distance = Slider(ax_distance, '总距离', 50, 200, valinit=total_distance_init, valstep=10)
s_acceleration = Slider(ax_acceleration, '加速度', 1, 10, valinit=acceleration_init, valstep=0.5)
s_max_speed = Slider(ax_max_speed, '最大速度', 5, 20, valinit=max_speed_init, valstep=0.5)

def compute_motion_profile(total_distance, acceleration, max_speed):
    # 计算加速阶段
    acceleration_time = max_speed / acceleration  # 加速时间
    acceleration_distance = 0.5 * acceleration * acceleration_time**2  # 加速阶段距离
    
    # 计算减速阶段（与加速阶段对称）
    deceleration_time = acceleration_time
    deceleration_distance = acceleration_distance
    
    # 检查加速和减速阶段的总距离是否超过总距离
    total_accel_decel_distance = acceleration_distance + deceleration_distance
    
    # 如果加速和减速阶段总距离超过总距离，需要调整
    if total_accel_decel_distance > total_distance:
        # 计算能够达到的最大速度（确保有足够的距离减速到0）
        # 解方程：total_distance = 2 * (0.5 * a * t^2)，其中v_max = a * t
        max_speed_adjusted = np.sqrt(acceleration * total_distance / 2)
        acceleration_time = max_speed_adjusted / acceleration
        acceleration_distance = 0.5 * acceleration * acceleration_time**2
        deceleration_time = acceleration_time
        deceleration_distance = acceleration_distance
        constant_speed_time = 0  # 没有匀速阶段
        max_speed = max_speed_adjusted  # 更新最大速度
    else:
        # 计算匀速阶段
        remaining_distance = total_distance - total_accel_decel_distance
        constant_speed_time = remaining_distance / max_speed  # 匀速阶段时间
    
    # 计算总时间
    total_time = acceleration_time + constant_speed_time + deceleration_time
    
    # 计算总步数
    total_steps = int(np.ceil(total_time * steps_per_second))
    
    # 创建步数数组
    steps = np.arange(total_steps + 1)  # +1 确保包含最后一步
    times = steps / steps_per_second
    
    # 计算每一步的距离和速度
    distances = np.zeros_like(steps, dtype=float)
    speeds = np.zeros_like(steps, dtype=float)
    
    for i, t in enumerate(times):
        if t <= acceleration_time:
            # 加速阶段
            speeds[i] = acceleration * t
            distances[i] = 0.5 * acceleration * t**2
        elif t <= acceleration_time + constant_speed_time:
            # 匀速阶段
            speeds[i] = max_speed
            t_const = t - acceleration_time
            distances[i] = acceleration_distance + max_speed * t_const
        else:
            # 减速阶段
            t_decel = t - (acceleration_time + constant_speed_time)
            speeds[i] = max_speed - acceleration * t_decel
            if speeds[i] < 0:
                speeds[i] = 0
            
            # 计算减速阶段的距离
            const_phase_dist = acceleration_distance + max_speed * constant_speed_time
            decel_dist = max_speed * t_decel - 0.5 * acceleration * t_decel**2
            distances[i] = const_phase_dist + decel_dist
            
            # 确保不超过总距离
            if distances[i] > total_distance:
                distances[i] = total_distance
                
    return steps, distances, speeds, {
        "acceleration_time": acceleration_time,
        "acceleration_distance": acceleration_distance,
        "constant_speed_time": constant_speed_time,
        "deceleration_time": deceleration_time,
        "deceleration_distance": deceleration_distance,
        "total_time": total_time,
        "total_steps": total_steps,
        "max_speed": max_speed  # 返回可能调整后的最大速度
    }

def compute_and_plot(total_distance, acceleration, max_speed):
    # 计算运动参数
    steps, distances, speeds, results = compute_motion_profile(
        total_distance, acceleration, max_speed)
    
    # 清除当前图形并重新绘制
    ax1.clear()
    ax2.clear()
    
    # 绘制距离-步数曲线
    ax1.plot(steps, distances, 'b-', linewidth=2, label='距离')
    ax1.set_title('步数-距离曲线（含减速阶段）', fontproperties=font)
    ax1.set_xlabel('步数', fontproperties=font)
    ax1.set_ylabel('距离', fontproperties=font)
    ax1.grid(True)
    
    # 绘制速度-步数曲线
    ax2.plot(steps, speeds, 'r-', linewidth=2, label='速度')
    ax2.set_xlabel('步数', fontproperties=font)
    ax2.set_ylabel('速度', fontproperties=font)
    ax2.grid(True)
    
    # 标记关键点
    accel_steps = int(results["acceleration_time"] * steps_per_second)
    const_end_steps = int((results["acceleration_time"] + results["constant_speed_time"]) * steps_per_second)
    
    # 在距离图上标记阶段
    ax1.axvline(x=accel_steps, color='g', linestyle='--', label=f'加速结束: {accel_steps}步')
    if results["constant_speed_time"] > 0:
        ax1.axvline(x=const_end_steps, color='m', linestyle='--', label=f'减速开始: {const_end_steps}步')
    
    # 在速度图上标记阶段
    ax2.axvline(x=accel_steps, color='g', linestyle='--')
    if results["constant_speed_time"] > 0:
        ax2.axvline(x=const_end_steps, color='m', linestyle='--')
    ax2.axhline(y=results["max_speed"], color='k', linestyle=':', label=f'最大速度: {results["max_speed"]:.2f}')
    
    # 添加阶段标签
    ax1.text(accel_steps/2, total_distance/4, 
             f'加速阶段\n加速度: {acceleration}', 
             fontsize=9, fontproperties=font)
    
    if results["constant_speed_time"] > 0:
        ax1.text(accel_steps + (const_end_steps-accel_steps)/2, total_distance*0.9, 
                f'匀速阶段\n速度: {results["max_speed"]:.2f}', 
                fontsize=9, fontproperties=font)
        
        ax1.text(const_end_steps + (results["total_steps"]-const_end_steps)/2, total_distance/2, 
                f'减速阶段\n减速度: {acceleration}', 
                fontsize=9, fontproperties=font)
    else:
        # 如果没有匀速阶段，直接标注减速阶段
        ax1.text(accel_steps + (results["total_steps"]-accel_steps)/2, total_distance/2, 
                f'减速阶段\n减速度: {acceleration}', 
                fontsize=9, fontproperties=font)
    
    # 添加注释
    note_text = (
        f'总距离: {total_distance}\n'
        f'总步数: {results["total_steps"]}\n'
        f'总时间: {results["total_time"]:.2f}秒\n'
    )
    
    if results["max_speed"] != max_speed:
        note_text += f'调整后最大速度: {results["max_speed"]:.2f}\n(原设定: {max_speed})'
    
    ax1.annotate(
        note_text,
        xy=(results["total_steps"], total_distance), 
        xytext=(results["total_steps"]*0.7, total_distance*0.3),
        arrowprops=dict(arrowstyle='->'), 
        fontproperties=font
    )
    
    ax1.legend(prop=font, loc='upper left')
    ax2.legend(prop=font, loc='upper right')
    
    fig.canvas.draw_idle()
    return results

# 更新函数，当滑块值改变时调用
def update(val):
    total_distance = s_distance.val
    acceleration = s_acceleration.val
    max_speed = s_max_speed.val
    results = compute_and_plot(total_distance, acceleration, max_speed)
    
    # 打印计算结果
    print("\n--- 运动过程详细信息 ---")
    print(f"加速时间: {results['acceleration_time']:.2f}秒")
    print(f"加速阶段距离: {results['acceleration_distance']:.2f}")
    print(f"匀速时间: {results['constant_speed_time']:.2f}秒")
    print(f"减速时间: {results['deceleration_time']:.2f}秒")
    print(f"减速阶段距离: {results['deceleration_distance']:.2f}")
    print(f"总时间: {results['total_time']:.2f}秒")
    print(f"总步数: {results['total_steps']}")
    if results["max_speed"] != max_speed:
        print(f"调整后最大速度: {results['max_speed']:.2f} (原设定: {max_speed})")

# 注册更新函数到滑块
s_distance.on_changed(update)
s_acceleration.on_changed(update)
s_max_speed.on_changed(update)

# 初始绘图
results = compute_and_plot(total_distance_init, acceleration_init, max_speed_init)

# 打印初始计算结果
print("\n--- 初始运动过程详细信息 ---")
print(f"加速时间: {results['acceleration_time']:.2f}秒")
print(f"加速阶段距离: {results['acceleration_distance']:.2f}")
print(f"匀速时间: {results['constant_speed_time']:.2f}秒")
print(f"减速时间: {results['deceleration_time']:.2f}秒")
print(f"减速阶段距离: {results['deceleration_distance']:.2f}")
print(f"总时间: {results['total_time']:.2f}秒")
print(f"总步数: {results['total_steps']}")

# 保存初始图像
plt.savefig('step_distance_curve_fixed.png')

# 显示图形
plt.show()