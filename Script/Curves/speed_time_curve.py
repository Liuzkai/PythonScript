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
plt.subplots_adjust(left=0.1, bottom=0.25)  # 为滑块留出空间

# 初始参数
initial_speed = 0  # 初始速度
total_distance_init = 100  # 总距离初始值
acceleration_init = 5  # 加速度初始值
max_speed_init = 9  # 最大速度初始值

# 创建滑块的位置
ax_distance = plt.axes([0.25, 0.15, 0.65, 0.03])
ax_acceleration = plt.axes([0.25, 0.10, 0.65, 0.03])
ax_max_speed = plt.axes([0.25, 0.05, 0.65, 0.03])

# 创建滑块
s_distance = Slider(ax_distance, '总距离', 50, 200, valinit=total_distance_init, valstep=10)
s_acceleration = Slider(ax_acceleration, '加速度', 1, 10, valinit=acceleration_init, valstep=0.5)
s_max_speed = Slider(ax_max_speed, '最大速度', 5, 20, valinit=max_speed_init, valstep=0.5)

# 计算和绘制函数
def compute_and_plot(total_distance, acceleration, max_speed):
    # 计算加速阶段
    acceleration_time = max_speed / acceleration  # 加速时间
    acceleration_distance = 0.5 * acceleration * acceleration_time**2  # 加速阶段距离
    
    # 计算匀速阶段
    remaining_distance = total_distance - acceleration_distance
    constant_speed_time = remaining_distance / max_speed  # 匀速阶段时间
    
    # 计算总时间
    total_time = acceleration_time + constant_speed_time
    
    # 创建时间数组（使用更多点以获得平滑的曲线）
    time_points = 1000
    time = np.linspace(0, total_time, time_points)
    
    # 计算每个时间点的速度
    speed = np.zeros_like(time)
    for i, t in enumerate(time):
        if t <= acceleration_time:
            # 加速阶段
            speed[i] = acceleration * t
        else:
            # 匀速阶段
            speed[i] = max_speed
    
    # 清除当前图形并重新绘制
    ax.clear()
    ax.plot(time, speed, 'b-', linewidth=2)
    ax.set_title('速度-时间曲线', fontproperties=font)
    ax.set_xlabel('时间', fontproperties=font)
    ax.set_ylabel('速度', fontproperties=font)
    ax.grid(True)
    ax.axhline(y=max_speed, color='r', linestyle='--', label=f'最大速度: {max_speed}')
    ax.axvline(x=acceleration_time, color='g', linestyle='--', label=f'加速时间: {acceleration_time:.2f}')
    ax.text(acceleration_time/2, max_speed/2, f'加速度: {acceleration}', fontsize=10, fontproperties=font)
    ax.text(acceleration_time + constant_speed_time/2, max_speed*0.9, f'匀速运动', fontsize=10, fontproperties=font)
    
    # 添加注释
    ax.annotate(f'总距离: {total_distance}\n总时间: {total_time:.2f}',
                xy=(total_time, 0), xytext=(total_time*0.8, max_speed*0.3),
                arrowprops=dict(arrowstyle='->'), fontproperties=font)
    
    ax.legend(prop=font)
    fig.canvas.draw_idle()
    
    # 返回计算结果
    return {
        "acceleration_time": acceleration_time,
        "acceleration_distance": acceleration_distance,
        "constant_speed_time": constant_speed_time,
        "total_time": total_time
    }

# 更新函数，当滑块值改变时调用
def update(val):
    total_distance = s_distance.val
    acceleration = s_acceleration.val
    max_speed = s_max_speed.val
    results = compute_and_plot(total_distance, acceleration, max_speed)
    
    # 打印计算结果
    print(f"加速时间: {results['acceleration_time']:.2f}")
    print(f"加速阶段距离: {results['acceleration_distance']:.2f}")
    print(f"匀速阶段时间: {results['constant_speed_time']:.2f}")
    print(f"总时间: {results['total_time']:.2f}")

# 注册更新函数到滑块
s_distance.on_changed(update)
s_acceleration.on_changed(update)
s_max_speed.on_changed(update)

# 初始绘图
results = compute_and_plot(total_distance_init, acceleration_init, max_speed_init)

# 打印初始计算结果
print(f"加速时间: {results['acceleration_time']:.2f}")
print(f"加速阶段距离: {results['acceleration_distance']:.2f}")
print(f"匀速阶段时间: {results['constant_speed_time']:.2f}")
print(f"总时间: {results['total_time']:.2f}")

# 保存初始图像
plt.savefig('speed_time_curve.png')

# 显示图形
plt.show()