import sys, os

import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft Yahei']
plt.rcParams['axes.unicode_minus'] = False

os.environ["KMP_DUPLICATE_LIB_OK"] = (
    "True"  # uncomment this line if omp error occurs on OSX for python 3
)
os.environ["OMP_NUM_THREADS"] = "1"  # set number of OpenMP threads to run in parallel
os.environ["MKL_NUM_THREADS"] = "1"  # set number of MKL threads to run in parallel
#

from quspin.operators import hamiltonian, exp_op
from quspin.tools.measurements import obs_vs_time
from quspin.tools.lanczos import lanczos_full
from quspin.basis import spin_basis_1d
from quspin.basis.user import user_basis
from quspin.basis.user import (
    pre_check_state_sig_32,
    op_sig_32,
    map_sig_32,
)
from numba import carray, cfunc
from numba import uint32, int32
import numpy as np
from scipy.optimize import curve_fit

N = 16

@cfunc(op_sig_32, locals=dict(s=int32, b=uint32))
def op(op_struct_ptr, op_str, ind, N, args):
    op_struct = carray(op_struct_ptr, 1)[0]
    err = 0
    ind = N - ind - 1
    s = (((op_struct.state >> ind) & 1) << 1) - 1
    b = 1 << ind
    #
    if op_str == 120:
        op_struct.state ^= b
    elif op_str == 121:
        op_struct.state ^= b
        op_struct.matrix_ele *= 1.0j * s
    elif op_str == 122:
        op_struct.matrix_ele *= s
    else:
        op_struct.matrix_ele = 0
        err = -1
    #
    return err

#
op_args = np.array([], dtype=np.uint32)

#
@cfunc(
    pre_check_state_sig_32,
    locals=dict(s_shift_left=uint32, s_shift_right=uint32),
)
def pre_check_state(s, N, args):
    mask = 0xFFFFFFFF >> (32 - N)
    s_shift_left = ((s << 1) & mask) | ((s >> (N - 1)) & mask)
    s_shift_right = ((s >> 1) & mask) | ((s << (N - 1)) & mask)
    #
    return (((s_shift_right | s_shift_left) & s)) == 0

#
pre_check_state_args = None

'''
#
@cfunc(
    map_sig_32,
    locals=dict(
        shift=uint32,
        xmax=uint32,
        x1=uint32,
        x2=uint32,
        period=int32,
        l=int32,
    ),
)
def translation(x, N, sign_ptr, args):
    shift = args[0]
    period = N
    xmax = args[1]
    #
    l = (shift + period) % period
    x1 = x >> (period - 1)
    x2 = (x << 1) & xmax
    #
    return x2 | x1
T_args = np.array([1, (1 << N) - 1], dtype=np.uint32)
#
@cfunc(
    map_sig_32,
    locals=dict(
        out=uint32,
        s=int32,
    ),
)
def parity(x, N, sign_ptr, args):
    out = 0
    s = args[0]
    #
    out ^= x & 1
    x >>= 1
    while x:
        out <<= 1
        out ^= x & 1
        x >>= 1
        s -= 1
    #
    out <<= s
    return out
P_args = np.array([N - 1], dtype=np.uint32)
#
maps = dict(
    T_block=(translation, N, 0, T_args),
    P_block=(parity, 2, 0, P_args),
)
'''
maps = dict()
op_dicts = dict(op=op, op_args=op_args)
pre_check_state = (
    pre_check_state,
    pre_check_state_args,
)

basis = user_basis(
    np.uint32,
    N,
    op_dicts,
    allowed_ops=set("xyz"),
    sps=2,
    pre_check_state=pre_check_state,
    Ns_block_est=300000,
    **maps,
)

print(basis)
#
h_list = [[1.0, i] for i in range(N)]
static = [
    ["x", h_list],
]


no_checks = dict(check_symm=False, check_pcon=False, check_herm=False)
H = hamiltonian(static, [], basis=basis, dtype=np.float64, **no_checks)


#[E_min], psi = H.eigsh(k=1, which="SA")
# construct initial state
Ns = basis.Ns
'''
def create_periodic_array(period, length):
    # 创建周期数组
    base_array = np.array(period)
    # 重复数组以确保长度足够
    repeated_array = np.tile(base_array, (length + len(base_array) - 1) // len(base_array))
    # 调整数组长度
    result_array = np.resize(repeated_array, length)
    return result_array

psi_0 = np.zeros(Ns)
psi_z2 = create_periodic_array([0,1], Ns)
psi_z3 = create_periodic_array([0,0,1], Ns)
psi_z4 = create_periodic_array([0,0,0,1], Ns)
'''
def create_state(Ns, dw_str, basis):
    i_0 = basis.index(dw_str)
    psi = np.zeros(Ns)
    psi[i_0] = 1.0
    return psi
assert N == 16
psi_0 = create_state(Ns, "0000000000000000", basis)
psi_z2 = create_state(Ns, "0101010101010101", basis)
psi_z3 = create_state(Ns, "0010010010010010", basis)
psi_z4 = create_state(Ns, "0001000100010001", basis)

# evolve states
start = 0.0
stop = 25.0
step = 0.1
num = round((stop-start)//step)
U = exp_op(H, a=-1j, start=start, stop=stop, num=num)
'''
def evolve(psi0, U):
    yield psi0
    psi0 = U.dot(psi0)
    yield psi0
psi_0_t = evolve(psi_0, U)
psi_z2_t = evolve(psi_z2, U)
psi_z3_t = evolve(psi_z3, U)
psi_z4_t = evolve(psi_z4, U)
'''
psi_0_t = U.dot(psi_0)
psi_z2_t = U.dot(psi_z2)
psi_z3_t = U.dot(psi_z3)
psi_z4_t = U.dot(psi_z4)

# entropy
t_array = np.linspace(start, stop, num)
def entropy(psi_t, H, basis, t_array):
    obs_t = obs_vs_time(psi_t, t_array, dict(E=H), return_state=True)
    Sent_t = basis.ent_entropy(obs_t["psi_t"], sub_sys_A=range(N//2))["Sent_A"]
    return Sent_t
Sent_0 = entropy(psi_0_t, H, basis, t_array)
Sent_z2 = entropy(psi_z2_t, H, basis, t_array)
Sent_z3 = entropy(psi_z3_t, H, basis, t_array)
Sent_z4 = entropy(psi_z4_t, H, basis, t_array)
def f(x, k, b):
    y = k*x + b
    return y
para, cov = curve_fit(f, t_array, Sent_z2)
delta_Sent_z2 = Sent_z2 - f(t_array, *para)
# Z_i*Z_{i+1}
Z_list = [[1.0, i, (i + 1) % N] for i in range(N)]
static_z2 = [["zz", Z_list]]
no_checks = dict(check_symm=False, check_pcon=False, check_herm=False)
correlation = hamiltonian(static_z2, [], basis=basis, dtype=np.float64, **no_checks)
obs_t = obs_vs_time(psi_z2_t, t_array, dict(E=H, O=correlation), return_state=True)
zz_t = obs_t["O"]/N

# overlap with eigen/FSA
(E_eigen, eigenstate) = H.eigh()
E_SA, eig_SA = H.eigsh(k=1, which='SA')
measurement1 = np.log(np.abs(np.dot(eigenstate, psi_z2))**2)
(E, V, Q_T) = lanczos_full(H, psi_z2, N)
eig_lanczos = np.transpose(np.dot(np.linalg.pinv(np.conj(Q_T)), V))
measurement_1_FSA = np.log(np.abs(np.dot(eig_lanczos, psi_z2))**2)
measurement2 = N*np.abs(np.dot(Q_T, eig_SA.ravel()))**2
measurement_2_FSA = N*np.abs(np.dot(Q_T, eig_lanczos[np.argmin(E)]))**2
measurement3 = N*np.abs(np.dot(Q_T, eigenstate[np.argsort(E_eigen)[3]]))**2
measurement_3_FSA = N*np.abs(np.dot(Q_T, eig_lanczos[np.argsort(E)[3]]))**2

# plot
plt.figure()
plt.xlabel(r'时间$t$/s')
plt.ylabel(r'半链纠缠熵$S$')
plt.plot(t_array, Sent_0, label=r"$|0\rangle$")
plt.plot(t_array, Sent_z2, label=r"$|Z_2\rangle$")
plt.plot(t_array, Sent_z3, label=r"$|Z_3\rangle$")
plt.plot(t_array, Sent_z4, label=r"$|Z_4\rangle$")
plt.grid(True)
plt.legend()
plt.savefig("entropy.png", dpi=500)
fig1, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 6))
plt.xlabel(r'时间$t$/s')
ax1.set_ylabel(r'半链纠缠熵的振荡$\Delta S$')
ax1.plot(t_array, delta_Sent_z2, label="delta_Sent_z2")
ax1.legend()
ax1.grid(True)
ax2.set_ylabel(r'关联$\langle Z_iZ_{i+1}\rangle$')
ax2.plot(t_array, zz_t, label="zz_t")
ax2.legend()
ax2.grid(True)
plt.tight_layout()
plt.savefig("z2_t.png", dpi=500)

plt.figure()
plt.ylim((-11,0))
plt.xlabel(r'能量特征值$E$')
plt.ylabel(r'$\ln{|\langle Z_2|\psi\rangle |^2}$')
plt.scatter(E_eigen, measurement1, label="ed")
plt.scatter(E, measurement_1_FSA, label="FSA")
plt.legend()
plt.savefig("measurement1.png", dpi=500)
fig2, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 6))
plt.xlabel(r'格点位置$n$')
ax1.set_ylabel(r'$|\langle n|\psi\rangle|^2 L$')
ax1.plot(np.arange(0, N), measurement2, label="ed")
ax1.plot(np.arange(0, N), measurement_2_FSA, label="FSA")
ax1.legend()
ax1.grid(True)
ax2.set_ylabel(r'$|\langle n|\psi\rangle|^2 L$')
ax2.plot(np.arange(0, N), measurement3, label="ed")
ax2.plot(np.arange(0, N), measurement_3_FSA, label="FSA")
ax2.legend()
ax2.grid(True)
plt.tight_layout()
plt.savefig("measurement2&3.png", dpi=500)