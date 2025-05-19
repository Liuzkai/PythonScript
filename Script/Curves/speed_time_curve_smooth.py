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
fig, ax = plt.subplots(figsize=(12, 8))
plt.subplots_adjust(left=0.1, bottom=0.35)  # 为滑块留出更多空间

# 初始参数
initial_speed = 0  # 初始速度
total_distance_init = 100  # 总距离初始值
acceleration_init = 5  # 加速度初始值
max_speed_init = 9  # 最大速度初始值
accel_smoothness_init = 0.5  # 加速平滑度初始值
decel_smoothness_init = 0.5  # 减速平滑度初始值

# 创建滑块的位置
ax_distance = plt.axes([0.25, 0.25, 0.65, 0.03])
ax_acceleration = plt.axes([0.25, 0.20, 0.65, 0.03])
ax_max_speed = plt.axes([0.25, 0.15, 0.65, 0.03])
ax_accel_smoothness = plt.axes([0.25, 0.10, 0.65, 0.03])
ax_decel_smoothness = plt.axes([0.25, 0.05, 0.65, 0.03])

# 创建滑块
s_distance = Slider(ax_distance, '总距离', 50, 200, valinit=total_distance_init, valstep=10)
s_acceleration = Slider(ax_acceleration, '加速度', 1, 10, valinit=acceleration_init, valstep=0.5)
s_max_speed = Slider(ax_max_speed, '最大速度', 5, 20, valinit=max_speed_init, valstep=0.5)
s_accel_smoothness = Slider(ax_accel_smoothness, '加速平滑度', 0.1, 1.0, valinit=accel_smoothness_init, valstep=0.1)
s_decel_smoothness = Slider(ax_decel_smoothness, '减速平滑度', 0.1, 1.0, valinit=decel_smoothness_init, valstep=0.1)

def smooth_transition(t, duration, start_value, end_value, smoothness):
    """
    使用三次多项式实现平滑过渡
    t: 当前时间
    duration: 过渡持续时间
    start_value: 起始值
    end_value: 结束值
    smoothness: 平滑度 (0.1-1.0)
    """
    if t <= 0:
        return start_value
    if t >= duration:
        return end_value
    
    # 归一化时间
    t_norm = t / duration
    
    # 调整平滑度
    s = smoothness
    
    # 使用三次多项式: y = at³ + bt² + ct + d
    # 满足边界条件：
    # y(0) = start_value, y(1) = end_value
    # y'(0) = 0, y'(1) = 0
    h = t_norm * (1 - s) + t_norm * t_norm * (3 * s - 2) + t_norm * t_norm * t_norm * (1 - s)
    return start_value + (end_value - start_value) * h

def compute_and_plot(total_distance, acceleration, max_speed, accel_smoothness, decel_smoothness):
    # 估计加速和减速时间
    base_accel_time = max_speed / acceleration
    accel_time = base_accel_time * 1.5  # 考虑平滑过渡需要更长时间
    decel_time = base_accel_time * 1.5
    
    # 创建时间数组
    time_points = 1000
    
    # 首先计算加速阶段，找到实际达到的距离
    accel_times = np.linspace(0, accel_time, time_points // 3)
    accel_speeds = [smooth_transition(t, accel_time, 0, max_speed, accel_smoothness) for t in accel_times]
    accel_distance = np.trapz(accel_speeds, accel_times)
    
    # 计算减速阶段
    decel_times = np.linspace(0, decel_time, time_points // 3)
    decel_speeds = [smooth_transition(t, decel_time, max_speed, 0, decel_smoothness) for t in decel_times]
    decel_distance = np.trapz(decel_speeds, decel_times)
    
    # 计算需要的匀速距离
    constant_distance = total_distance - accel_distance - decel_distance
    if constant_distance < 0:
        constant_distance = 0
    constant_time = constant_distance / max_speed if max_speed > 0 else 0
    
    # 合并所有阶段
    total_time = accel_time + constant_time + decel_time
    time = np.linspace(0, total_time, time_points)
    speed = np.zeros_like(time)
    
    for i, t in enumerate(time):
        if t <= accel_time:
            # 加速阶段
            speed[i] = smooth_transition(t, accel_time, 0, max_speed, accel_smoothness)
        elif t <= accel_time + constant_time:
            # 匀速阶段
            speed[i] = max_speed
        else:
            # 减速阶段
            t_decel = t - (accel_time + constant_time)
            speed[i] = smooth_transition(t_decel, decel_time, max_speed, 0, decel_smoothness)
    
    # 计算实际距离
    distance = np.cumsum(speed) * (total_time / time_points)
    
    # 清除当前图形并重新绘制
    ax.clear()
    ax.plot(time, speed, 'b-', linewidth=2)
    ax.set_title('速度-时间曲线 (平滑加减速)', fontproperties=font)
    ax.set_xlabel('时间', fontproperties=font)
    ax.set_ylabel('速度', fontproperties=font)
    ax.grid(True)
    
    # 标记各阶段
    ax.axhline(y=max_speed, color='r', linestyle='--', label=f'最大速度: {max_speed}')
    ax.axvline(x=accel_time, color='g', linestyle='--', label=f'加速结束: {accel_time:.2f}')
    ax.axvline(x=accel_time + constant_time, color='m', linestyle='--', label=f'减速开始: {(accel_time + constant_time):.2f}')
    
    # 添加阶段标签
    ax.text(accel_time/2, max_speed/2, f'平滑加速\n加速度: {acceleration}', fontsize=10, fontproperties=font)
    if constant_time > 0:
        ax.text(accel_time + constant_time/2, max_speed*0.9, f'匀速运动', fontsize=10, fontproperties=font)
    ax.text(accel_time + constant_time + decel_time/2, max_speed/2, f'平滑减速', fontsize=10, fontproperties=font)
    
    # 添加注释
    ax.annotate(f'总距离: {total_distance}\n总时间: {total_time:.2f}',
                xy=(total_time, 0), xytext=(total_time*0.8, max_speed*0.3),
                arrowprops=dict(arrowstyle='->'), fontproperties=font)
    
    ax.legend(prop=font)
    fig.canvas.draw_idle()
    
    return {
        "accel_time": accel_time,
        "accel_distance": accel_distance,
        "constant_time": constant_time,
        "constant_distance": constant_distance,
        "decel_time": decel_time,
        "decel_distance": decel_distance,
        "total_time": total_time,
        "final_distance": distance[-1]
    }

# 更新函数，当滑块值改变时调用
def update(val):
    total_distance = s_distance.val
    acceleration = s_acceleration.val
    max_speed = s_max_speed.val
    accel_smoothness = s_accel_smoothness.val
    decel_smoothness = s_decel_smoothness.val
    
    results = compute_and_plot(total_distance, acceleration, max_speed, 
                             accel_smoothness, decel_smoothness)
    
    # 打印计算结果
    print("\n--- 运动过程详细信息 ---")
    print(f"加速时间: {results['accel_time']:.2f}")
    print(f"加速阶段距离: {results['accel_distance']:.2f}")
    print(f"匀速时间: {results['constant_time']:.2f}")
    print(f"匀速阶段距离: {results['constant_distance']:.2f}")
    print(f"减速时间: {results['decel_time']:.2f}")
    print(f"减速阶段距离: {results['decel_distance']:.2f}")
    print(f"总时间: {results['total_time']:.2f}")
    print(f"实际总距离: {results['final_distance']:.2f}")

# 注册更新函数到滑块
s_distance.on_changed(update)
s_acceleration.on_changed(update)
s_max_speed.on_changed(update)
s_accel_smoothness.on_changed(update)
s_decel_smoothness.on_changed(update)

# 初始绘图
results = compute_and_plot(total_distance_init, acceleration_init, max_speed_init, 
                          accel_smoothness_init, decel_smoothness_init)

# 打印初始计算结果
print("\n--- 初始运动过程详细信息 ---")
print(f"加速时间: {results['accel_time']:.2f}")
print(f"加速阶段距离: {results['accel_distance']:.2f}")
print(f"匀速时间: {results['constant_time']:.2f}")
print(f"匀速阶段距离: {results['constant_distance']:.2f}")
print(f"减速时间: {results['decel_time']:.2f}")
print(f"减速阶段距离: {results['decel_distance']:.2f}")
print(f"总时间: {results['total_time']:.2f}")
print(f"实际总距离: {results['final_distance']:.2f}")

# 保存初始图像
plt.savefig('speed_time_curve_smooth.png')

# 显示图形
plt.show()