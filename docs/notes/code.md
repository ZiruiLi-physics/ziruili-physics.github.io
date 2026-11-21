---
description: PXP 模型的精确对角化与 DMRG 时间演化代码，附依赖与运行说明。
---

# 代码与工具

这里放我自己在用的脚本。它们不是软件包，也没有完整测试；改之前请先读源码。

PXP 模型是 Rydberg 原子阵列里常见的有效模型：

\[
    H = \sum_i P_{i-1} X_i P_{i+1}, \qquad P = |0\rangle\langle 0|
\]

下面两个脚本分别用精确对角化和张量网络来研究它的动力学。

<div class="zl-code-card">
<h3>ed_PXP.py — 精确对角化</h3>

<dl class="zl-code-meta">
  <dt>用途</dt><dd>用 QuSpin 构建 PXP 哈密顿量，配合 numba 自定义 basis 做精确对角化，计算小系统的动力学与观测量。</dd>
  <dt>依赖</dt><dd>Python 3、QuSpin、numba、numpy、scipy、matplotlib</dd>
  <dt>规模</dt><dd>默认 <code>N = 16</code>，请按内存与时间预算调整。</dd>
  <dt>运行</dt><dd>直接 <code>python ed_PXP.py</code>，输出与图像在脚本末尾调整。</dd>
</dl>

```python
from quspin.operators import hamiltonian, exp_op
from quspin.basis import spin_basis_1d
from quspin.basis.user import user_basis
from numba import cfunc, carray
```

<div class="zl-code-actions">
  <a class="zl-btn" href="/notes/downloads/ed_PXP.py">下载 ed_PXP.py</a>
</div>
</div>

<div class="zl-code-card">
<h3>PXP_tvdp.py — DMRG / 时间演化</h3>

<dl class="zl-code-meta">
  <dt>用途</dt><dd>用 TeNPy 的 MPS 做 iTEBD 与 TDVP 时间演化，跟踪纠缠熵、关联函数与截断误差。</dd>
  <dt>依赖</dt><dd>Python 3、TeNPy、numpy、scipy、matplotlib</dd>
  <dt>参数</dt><dd>默认 <code>chi_max = 400</code>、<code>dt = 0.1</code>、四阶分解。</dd>
  <dt>运行</dt><dd>直接 <code>python PXP_tvdp.py</code>；不同 <code>chi_max</code> 的收敛性需要自己检查。</dd>
</dl>

```python
from tenpy.algorithms import tebd, tdvp
from tenpy.networks.mps import MPS
from tenpy.models.pxp import PXPChain
```

<div class="zl-code-actions">
  <a class="zl-btn" href="/notes/downloads/PXP_tvdp.py">下载 PXP_tvdp.py</a>
</div>
</div>

!!! warning "关于可复现性"
    脚本里的参数是我当时做项目用的，不保证对所有人都合适。遇到 <code>omp</code> 报错时，可以看 <code>ed_PXP.py</code> 开头设置线程数的几行。
