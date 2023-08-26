import numpy as np # 用于数值计算
import matplotlib.pyplot as plt # 用于绘制图形

# 是已知的数据点，我们将使用这些数据来拟合一个线性模型。
x_data = [338., 333., 328., 207., 226., 25., 179., 60., 208., 606.]
y_data = [650., 633., 619., 393., 428., 27., 193., 66., 226., 1591.]

# x 和 y 变量分别表示偏置（bias）和权重（weight）的取值范围。这里，x 范围从 -200 到 -100，y 范围从 -5 到 5。 ydata = b + w * xdata
x = np.arange(-200, -100, 1) # bias
y = np.arange(-5, 5, 0.1) # weight

# 二位数组0填充, 有len(x)个元素, 每个元素 len(y) 个长度
# 初始化损失函数矩阵 Z，并根据偏置 b 和权重 w 的组合计算损失值。损失函数使用平方误差和（Sum of Squared Errors, SSE）。
Z = np.zeros((len(x), len(y)))
X, Y = np.meshgrid(x,  y)
for i in range(len(x)):
    for j in range(len(y)):
        b = x[i]
        w = y[j]
        Z[j][i] = 0
        for n in range(len(x_data)):
            Z[j][i] = Z[j][i] + (y_data[n] - b - w * x_data[n])**2
        Z[j][i] = Z[j][i] / len(x_data)


# 保存初始参数值：b_history 和 w_history 分别用于保存偏置 b 和权重 w 的更新历史。
b = -120 # initial b
w = -4 # initial w
lr = 0.0000001 # learning rate
iteration = 100000

# Store initial values for plotting.
b_history = [b]
w_history = [w]

# 梯度下降循环
# 求导法则; 函数f(x)倒数用f'(x)表示; 或者df/dx
    # 常数函数：对于一个常数 c，其导数为零。即 d(c)/dx = 0。
    # 幂函数：对于一个幂函数 f(x) = x^n，其中 n 是一个实数，其导数为：f'(x) = n * x^(n-1)。
    # 和法则：对于两个函数的和 f(x) = g(x) + h(x)，其导数为：f'(x) = g'(x) + h'(x)。
    # 乘法法则：对于两个函数的乘积 f(x) = g(x) * h(x)，其导数为：f'(x) = g'(x) * h(x) + g(x) * h'(x)。
    # 链式法则：对于复合函数 f(x) = g(h(x))，其导数为：f'(x) = g'(h(x)) * h'(x)。
    #  对b求导(即将b看成是变量, 其他看成常数):
    #    1.u = y(b) - b - w*x(b)
    #       y和x都是b的函数, du/db = dy(b)/db - 1 - w * dx(b)/db
    #    2.u = (y * b^2) - b - (w * x * b)
    #       在这个例子中，y 和 x 是常数，但它们与 b 相乘。我们需要分别对每一项求导。du/db = 2 * y * b - 1 - (w * x)
for i in range(iteration):
    # b_grad 和 w_grad 分别表示偏置（b）和权重（w）的梯度。初始化它们为 0。即b和w的偏微分
    b_grad = 0.0
    w_grad = 0.0
    # 损失函数关于b和w求导; 遍历所有数据点
    for n in range(len(x_data)):
        # 损失函数: L(b, w) = Σ(y - (b + w * x))^2;  使用的是"平方误差和"的计算方式, y 是实际值，b 是偏置，w 是权重，x 是输入特征
        # 此时计算预测值(偏置 + 权重*x值), 即 b + w * x_data[n]
        # 对于每个数据点，计算预测值与实际值之间的误差（y_data[n] - b - w * x_data[n]）
        # 然后计算关于偏置（b）和权重（w）的梯度, **也就是对b和w求导**。**损失函数**是所有点的误差平方的和, 当前点的平方是(y_data[n] - b - w * x_data[n])^2, 对它求导是2(y_data[n] - b - w * x_data[n]), 然后每一项累加
        # 乘以 -2 是因为损失函数是平方误差和, 求导后需要乘以 2。我们用负号表示梯度下降，因为我们希望朝着梯度的反方向更新参数以最小化损失函数。
        b_grad = b_grad - 2.0 * (y_data[n] - b - w * x_data[n]) * 1.0
        # 这里计算的是损失函数关于权重 w 的梯度。同样，乘以 -2 是因为损失函数是平方误差和，求导后需要乘以 2。注意，这里的梯度还需要乘以 x_data[n]，因为这是权重 w 对应的输入特征。
        w_grad = w_grad - 2.0 * (y_data[n] - b - w * x_data[n]) * x_data[n]
    
    # Update parameters.
    # 用学习率乘以偏置的梯度，然后从当前偏置值中减去它，得到新的偏置值。
    b = b - lr * b_grad
    # 用学习率乘以权重的梯度，然后从当前权重值中减去它，得到新的权重值
    w = w - lr * w_grad

    # Store parameters for plotting
    b_history.append(b)
    w_history.append(w)


# plot the figure; 使用 plt.contourf() 函数绘制损失函数的等高线图，显示不同参数组合下的损失值。横轴表示偏置，纵轴表示权重。
plt.contourf(x, y, Z, 50, alpha=0.5, cmap=plt.get_cmap('jet'))

# 使用 plt.plot() 函数绘制最优解（-188.4，2.67）的位置，以橙色的 'x' 标记
plt.plot([-188.4], [2.67], 'x', ms=12, markeredgewidth=3, color='orange')
# 使用 plt.plot() 函数绘制 b_history 和 w_history 中记录的参数更新路径
plt.plot(b_history, w_history, 'o-', ms=3, lw=1.5, color='black')

# 使用 plt.xlim() 和 plt.ylim() 设置坐标轴范围；
plt.xlim(-200, -100)
plt.ylim(-5, 5)
# 使用 plt.xlabel() 和 plt.ylabel() 设置坐标轴标签
plt.xlabel(r'$b$', fontsize=16)
plt.xlabel(r'$w$', fontsize=16)
# 使用 plt.show() 显示图形
plt.show()
