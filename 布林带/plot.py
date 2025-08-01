import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建数据
data = {
    'n': [15, 15, 15, 20, 20, 20, 25, 25, 25],
    'k': [1.8, 2.0, 2.2, 1.8, 2.0, 2.2, 1.8, 2.0, 2.2],
    'final_value': [142494.56, 125054.79, 141644.14, 129869.86, 128003.45, 123802.31, 131626.36, 137164.53, 147617.69],
    'sharpe_ratio': [1.5578, 0.9983, 1.2354, 0.7098, 1.9627, 4.4305, 0.9987, 1.3368, 1.7964],
    'max_drawdown': [19.07, 19.07, 9.50, 14.54, 14.34, 14.34, 12.95, 12.95, 7.64]
}

df = pd.DataFrame(data)

# 创建图表
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('布林带策略参数优化结果可视化', fontsize=16)

# 1. 最终资金对比
x = np.arange(len(df))
width = 0.25

axes[0, 0].bar(x - width, df['final_value']/1000, width, label='最终资金(千元)', color='skyblue')
axes[0, 0].set_xlabel('参数组合')
axes[0, 0].set_ylabel('最终资金(千元)')
axes[0, 0].set_title('不同参数组合的最终资金对比')
axes[0, 0].set_xticks(x)
axes[0, 0].set_xticklabels([f'n={row.n},k={row.k}' for row in df.itertuples()], rotation=45)
axes[0, 0].grid(axis='y', alpha=0.3)

# 2. 夏普比率对比
axes[0, 1].bar(x, df['sharpe_ratio'], width, label='夏普比率', color='lightgreen')
axes[0, 1].set_xlabel('参数组合')
axes[0, 1].set_ylabel('夏普比率')
axes[0, 1].set_title('不同参数组合的夏普比率对比')
axes[0, 1].set_xticks(x)
axes[0, 1].set_xticklabels([f'n={row.n},k={row.k}' for row in df.itertuples()], rotation=45)
axes[0, 1].grid(axis='y', alpha=0.3)

# 3. 最大回撤对比
axes[1, 0].bar(x + width, df['max_drawdown'], width, label='最大回撤(%)', color='salmon')
axes[1, 0].set_xlabel('参数组合')
axes[1, 0].set_ylabel('最大回撤(%)')
axes[1, 0].set_title('不同参数组合的最大回撤对比')
axes[1, 0].set_xticks(x)
axes[1, 0].set_xticklabels([f'n={row.n},k={row.k}' for row in df.itertuples()], rotation=45)
axes[1, 0].grid(axis='y', alpha=0.3)

# 4. 参数热力图
pivot_table = df.pivot(index='n', columns='k', values='final_value')
im = axes[1, 1].imshow(pivot_table.values, cmap='YlGnBu')

# 设置刻度
axes[1, 1].set_xticks(np.arange(len(pivot_table.columns)))
axes[1, 1].set_yticks(np.arange(len(pivot_table.index)))
axes[1, 1].set_xticklabels(pivot_table.columns)
axes[1, 1].set_yticklabels(pivot_table.index)

# 添加数值标注
for i in range(len(pivot_table.index)):
    for j in range(len(pivot_table.columns)):
        axes[1, 1].text(j, i, f'{pivot_table.iloc[i, j]/1000:.0f}k',
                       ha="center", va="center", color="black")

axes[1, 1].set_xlabel('标准差乘数(k)')
axes[1, 1].set_ylabel('周期(n)')
axes[1, 1].set_title('最终资金热力图(单位:千元)')

plt.tight_layout()
plt.savefig('opt.png')
plt.show()

# 找出最佳参数组合
best_return_idx = df['final_value'].idxmax()
best_sharpe_idx = df['sharpe_ratio'].idxmax()
best_drawdown_idx = df['max_drawdown'].idxmin()

print("最佳参数组合:")
print(f"最高收益: n={df.loc[best_return_idx, 'n']}, k={df.loc[best_return_idx, 'k']}, 最终资金={df.loc[best_return_idx, 'final_value']:.2f}")
print(f"最佳夏普比率: n={df.loc[best_sharpe_idx, 'n']}, k={df.loc[best_sharpe_idx, 'k']}, 夏普比率={df.loc[best_sharpe_idx, 'sharpe_ratio']:.4f}")
print(f"最小回撤: n={df.loc[best_drawdown_idx, 'n']}, k={df.loc[best_drawdown_idx, 'k']}, 最大回撤={df.loc[best_drawdown_idx, 'max_drawdown']:.2f}%")
