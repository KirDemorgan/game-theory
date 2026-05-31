"""
Lab 3 - Optimization Methods & Dynamic Programming
Variant 1 | Drankov A.E.

Tasks:
  1. Linear Programming: microservice release planning (LP + duality + sensitivity)
  2. Nonlinear DP: load distribution over 4 stages, X=12 TB
  3. Johnson's algorithm: 7-job CI/CD pipeline scheduling
  4. Equipment replacement: microservice rotation over 5 years
  5. Resource allocation DP: budget Z=15 over 3 quarters
"""

import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import numpy as np
from scipy.optimize import linprog
from collections import deque


def solve_task1():
    c = [-8, -11, -7, -14, -9, -16]

    A_ub = [
        [3, 4, 2, 5, 2, 6],
        [2, 3, 1, 4, 1, 5],
        [15, 20, 10, 25, 8, 30],
        [-1, -1, -1, 0, 0, 0],
        [0, 0, 0, -1, -1, -1],
        [0, 1, 0, 1, 0, 0],
    ]
    b_ub = [200, 140, 900, -12, -10, 15]
    bounds = [(0, None)] * 6

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

    shadow_prices = res.ineqlin.marginals

    sensitivity = {}
    for pct in [-15, 0, 15]:
        b_s = list(b_ub)
        b_s[1] = 140 * (1 + pct / 100.0)
        r = linprog(c, A_ub=A_ub, b_ub=b_s, bounds=bounds, method="highs")
        sensitivity[pct] = round(-r.fun, 4) if r.success else None

    return res, shadow_prices, sensitivity


def print_task1(res, shadow_prices, sensitivity):
    var_names = [
        "x1 (core services)",
        "x2 (API gateway)",
        "x3 (auth microservice)",
        "x4 (analytics service)",
        "x5 (UI framework)",
        "x6 (monitoring)",
    ]
    con_names = [
        "DevOps hours (<= 200)",
        "Cloud budget (<= 140)",
        "Compute quotas (<= 900)",
        "Min critical services (x1+x2+x3 >= 12)",
        "Infra balance (x4+x5+x6 >= 10)",
        "Gateway limit (x2+x4 <= 15)",
    ]
    print("=" * 65)
    print("TASK 1: LP — Microservice Release Planning")
    print("=" * 65)
    print(f"\nOptimal margin:  F* = {-res.fun:.4f}  M RUB / quarter")
    print(f"Solver status:   {res.message}\n")
    print("Optimal release plan:")
    for name, val in zip(var_names, res.x):
        print(f"  {name}: {val:.4f}")
    print("\nShadow prices (marginals of dual variables):")
    for cname, sp in zip(con_names, shadow_prices):
        sign = "binding" if abs(sp) > 1e-6 else "slack"
        print(f"  [{sign:7s}] {cname}: {sp:.4f}")
    base = sensitivity[0]
    print("\nSensitivity -- cloud budget change (+-15%):")
    for pct, val in sensitivity.items():
        delta = val - base if val is not None else None
        print(f"  Budget {pct:+3d}%  ->  F = {val:.4f}  (delta = {delta:+.4f})")


def solve_task2():
    ALPHA = 0.3
    BETA = 0.7
    N = 4
    X_MAX = 12
    H = 1.0
    DY = 0.01

    X_grid = np.arange(0.0, X_MAX + H, H)

    def stage_cost(Y_arr, X):
        return 3.0 * Y_arr**2 + 2.0 * (X - Y_arr) ** 2

    def interp(vals, q):
        if q <= X_grid[0]:
            return vals[0]
        if q >= X_grid[-1]:
            return vals[-1]
        i = int(np.searchsorted(X_grid, q)) - 1
        x0, x1 = X_grid[i], X_grid[i + 1]
        return vals[i] + (q - x0) * (vals[i + 1] - vals[i]) / (x1 - x0)

    F_tables = []
    Y_tables = []

    F1 = np.zeros_like(X_grid)
    Y1 = np.zeros_like(X_grid)
    for i, X in enumerate(X_grid):
        if X == 0.0:
            continue
        Yc = np.arange(0.0, X + DY, DY)
        costs = stage_cost(Yc, X)
        bi = int(np.argmin(costs))
        F1[i] = costs[bi]
        Y1[i] = Yc[bi]
    F_tables.append(F1)
    Y_tables.append(Y1)

    for k in range(2, N + 1):
        Fk = np.zeros_like(X_grid)
        Yk = np.zeros_like(X_grid)
        F_prev = F_tables[-1]
        for i, X in enumerate(X_grid):
            if X == 0.0:
                continue
            Yc = np.arange(0.0, X + DY, DY)
            X_next_arr = ALPHA * Yc + BETA * (X - Yc)
            fut = np.array([interp(F_prev, xn) for xn in X_next_arr])
            totals = stage_cost(Yc, X) + fut
            bi = int(np.argmin(totals))
            Fk[i] = totals[bi]
            Yk[i] = Yc[bi]
        F_tables.append(Fk)
        Y_tables.append(Yk)

    trajectory = []
    X_states = [float(X_MAX)]
    X_cur = float(X_MAX)
    for k in range(N, 0, -1):
        Y_opt = interp(Y_tables[k - 1], X_cur)
        trajectory.append(round(Y_opt, 2))
        X_cur = ALPHA * Y_opt + BETA * (X_cur - Y_opt)
        X_states.append(round(X_cur, 4))

    return X_grid, F_tables, Y_tables, trajectory, X_states


def print_task2(X_grid, F_tables, Y_tables, trajectory, X_states):
    print("\n" + "=" * 65)
    print("TASK 2: Nonlinear DP — Load Distribution (N=4, X_init=12 TB)")
    print("Cost: 3Y² + 2(X−Y)²,  transition: X' = 0.3Y + 0.7(X−Y)")
    print("=" * 65)
    header = f"{'X':>3} | {'F1':>8} {'Y1':>6} | {'F2':>8} {'Y2':>6} | {'F3':>8} {'Y3':>6} | {'F4':>8} {'Y4':>6}"
    print("\n" + header)
    print("-" * len(header))
    for xi in range(1, int(X_grid[-1]) + 1):
        row = f"{xi:>3} |"
        for k in range(4):
            f = F_tables[k][xi]
            y = Y_tables[k][xi]
            row += f" {f:8.2f} {y:6.2f} |"
        print(row)
    print(f"\nOptimal trajectory for X=12, N=4:")
    for step, (y, x_next) in enumerate(zip(trajectory, X_states[1:]), 1):
        print(f"  Stage {step}: Y*={y:.2f}  ->  X_next = {x_next:.4f}")
    print(f"\nMinimum total cost: F4(12) = {F_tables[3][12]:.4f}")


def solve_task3():
    A = [3, 5, 2, 8, 4, 6, 1]
    B = [4, 2, 6, 3, 5, 1, 7]
    n = 7

    def johnson_schedule(A, B):
        processed = [False] * n
        seq = deque()
        for _ in range(n):
            min_val, min_j, min_m = np.inf, -1, -1
            for j in range(n):
                if not processed[j]:
                    if A[j] < min_val:
                        min_val, min_j, min_m = A[j], j, 0
                    if B[j] < min_val:
                        min_val, min_j, min_m = B[j], j, 1
            processed[min_j] = True
            if min_m == 0:
                seq.appendleft(min_j)
            else:
                seq.append(min_j)
        return list(seq)

    def compute_schedule(order, A, B):
        comp_A, comp_B, idle_B = 0, 0, 0
        schedule = []
        for j in order:
            s_A = comp_A
            comp_A += A[j]
            s_B = max(comp_A, comp_B)
            idle_B += s_B - comp_B
            comp_B = s_B + B[j]
            schedule.append((j + 1, s_A, comp_A, s_B, comp_B))
        return comp_B, idle_B, schedule

    original_order = list(range(n))
    optimal_order = johnson_schedule(A, B)

    ms_orig, idle_orig, sched_orig = compute_schedule(original_order, A, B)
    ms_opt, idle_opt, sched_opt = compute_schedule(optimal_order, A, B)

    return optimal_order, ms_orig, idle_orig, sched_orig, ms_opt, idle_opt, sched_opt


def print_task3(opt_order, ms_orig, idle_orig, sched_orig, ms_opt, idle_opt, sched_opt):
    print("\n" + "=" * 65)
    print("TASK 3: Johnson's Algorithm — CI/CD Pipeline (7 jobs)")
    print("A (compile): [3,5,2,8,4,6,1]   B (test): [4,2,6,3,5,1,7]")
    print("=" * 65)
    print(f"\nJohnson sequence: {[j + 1 for j in opt_order]}")

    def print_gantt(schedule, label):
        print(f"\n{label}")
        print(f"  {'Job':>4}  {'A_start':>8} {'A_end':>6}  {'B_start':>8} {'B_end':>6}")
        for j, sa, ea, sb, eb in schedule:
            print(f"  Job {j}:  A [{sa:3d} → {ea:3d}]    B [{sb:3d} → {eb:3d}]")

    print_gantt(sched_orig, "--- Original order (1, 2, 3, 4, 5, 6, 7) ---")
    print(f"  Makespan = {ms_orig} min  |  Machine-B idle = {idle_orig} min")

    print_gantt(
        sched_opt, f"--- Johnson optimal order {[j + 1 for j in opt_order]} ---"
    )
    print(f"  Makespan = {ms_opt} min  |  Machine-B idle = {idle_opt} min")

    reduction = (ms_orig - ms_opt) / ms_orig * 100
    print(f"\nMakespan reduction: {ms_orig} → {ms_opt} min  ({reduction:.1f}%)")
    print(f"Machine-B idle reduction: {idle_orig} → {idle_opt} min")


def solve_task4():
    N = 5
    T_MAX = 5

    def R(t):
        return max(0, 25 - 2 * t) if t <= T_MAX else 0

    def C(t):
        return 4 + 3 * t

    F = {}
    policy = {}

    F[1] = {}
    policy[1] = {}
    for t in range(T_MAX + 2):
        keep_val = R(t)
        replace_val = R(0) - C(t)
        if keep_val >= replace_val:
            F[1][t], policy[1][t] = keep_val, "K"
        else:
            F[1][t], policy[1][t] = replace_val, "R"

    for k in range(2, N + 1):
        F[k] = {}
        policy[k] = {}
        for t in range(T_MAX + 2):
            # Keep: earn R(t) now, next period at age t+1
            keep_val = R(t) + F[k - 1].get(t + 1, 0)
            # Replace: pay C(t), earn R(0), next period at age 1
            replace_val = R(0) - C(t) + F[k - 1].get(1, 0)
            if keep_val >= replace_val:
                F[k][t], policy[k][t] = keep_val, "K"
            else:
                F[k][t], policy[k][t] = replace_val, "R"

    t_cur = 2
    path = []
    for step in range(1, N + 1):
        k_rem = N - step + 1
        act = policy[k_rem][t_cur]
        profit = R(t_cur) if act == "K" else R(0) - C(t_cur)
        path.append({"step": step, "age": t_cur, "action": act, "profit": profit})
        t_cur = t_cur + 1 if act == "K" else 1

    return F, policy, path


def print_task4(F, policy, path):
    print("\n" + "=" * 65)
    print("TASK 4: Equipment Replacement — Microservice Rotation")
    print("R(t)=25−2t,  C(t)=4+3t,  N=5,  Tmax=5,  t0=2")
    print("=" * 65)

    T_MAX = 5
    t_show = list(range(T_MAX + 1))

    print("\nBellman value table  Fk(t):")
    header = f"{'t':>3} |" + "".join(f"  F{k}(t) |" for k in range(1, 6))
    print(header)
    print("-" * 55)
    for t in t_show:
        row = f"{t:>3} |"
        for k in range(1, 6):
            val = F[k].get(t, 0)
            row += f"  {val:5.1f}  |"
        print(row)

    print("\nDecision policy table  πk(t)  (K=keep, R=replace):")
    header2 = f"{'t':>3} |" + "".join(f"   π{k}   |" for k in range(1, 6))
    print(header2)
    print("-" * 55)
    for t in t_show:
        row = f"{t:>3} |"
        for k in range(1, 6):
            act = policy[k].get(t, "?")
            row += f"    {act}    |"
        print(row)

    print("\nOptimal trajectory  (t0 = 2):")
    total = 0
    for info in path:
        s, t, act, p = info["step"], info["age"], info["action"], info["profit"]
        label = "Keep" if act == "K" else "Replace"
        print(f"  Year {s}: age={t}, decision={label}, profit={p}")
        total += p
    print(f"\n  Total profit over {len(path)} years: {total}")


def solve_task5():
    ALPHA = 0.6
    BETA = 0.7
    N = 3
    X_GRID = np.array([0.0, 5.0, 10.0, 15.0])
    DELTA_Y = 2

    def g(Y):
        return 4.0 * Y + 0.05 * Y**2

    def h(v):
        return 3.0 * v + 0.1 * v**2

    def interp(vals, q):
        if q <= X_GRID[0]:
            return vals[0]
        if q >= X_GRID[-1]:
            return vals[-1]
        i = int(np.searchsorted(X_GRID, q)) - 1
        x0, x1 = X_GRID[i], X_GRID[i + 1]
        return vals[i] + (q - x0) * (vals[i + 1] - vals[i]) / (x1 - x0)

    F_tables = []
    Y_tables = []

    def y_candidates(X):
        return np.arange(0, X + 1e-9, DELTA_Y)

    F1 = np.zeros(len(X_GRID))
    Y1 = np.zeros(len(X_GRID))
    for i, X in enumerate(X_GRID):
        best_val, best_Y = -np.inf, 0.0
        for Y in y_candidates(X):
            val = g(Y) + h(X - Y)
            if val > best_val:
                best_val, best_Y = val, Y
        F1[i] = max(0.0, best_val)
        Y1[i] = best_Y
    F_tables.append(F1)
    Y_tables.append(Y1)

    for k in range(2, N + 1):
        Fk = np.zeros(len(X_GRID))
        Yk = np.zeros(len(X_GRID))
        F_prev = F_tables[-1]
        for i, X in enumerate(X_GRID):
            best_val, best_Y = -np.inf, 0.0
            for Y in y_candidates(X):
                X_next = ALPHA * Y + BETA * (X - Y)
                val = g(Y) + h(X - Y) + interp(F_prev, X_next)
                if val > best_val:
                    best_val, best_Y = val, Y
            Fk[i] = max(0.0, best_val)
            Yk[i] = best_Y
        F_tables.append(Fk)
        Y_tables.append(Yk)

    trajectory = []
    X_states = [15.0]
    X_cur = 15.0
    for k in range(N, 0, -1):
        Y_interp = interp(Y_tables[k - 1], X_cur)
        Y_cands = y_candidates(X_cur)
        Y_opt = Y_cands[int(np.argmin(np.abs(Y_cands - Y_interp)))]
        trajectory.append(Y_opt)
        X_cur = ALPHA * Y_opt + BETA * (X_cur - Y_opt)
        X_states.append(round(X_cur, 4))

    return X_GRID, F_tables, Y_tables, trajectory, X_states


def print_task5(X_GRID, F_tables, Y_tables, trajectory, X_states):
    print("\n" + "=" * 65)
    print("TASK 5: Resource Allocation DP")
    print("Z=15, N=3, g=4Y+0.05Y², h=3v+0.1v², α=0.6, β=0.7, ΔY=2")
    print("=" * 65)

    print(
        f"\n{'X':>5} | {'F1':>9} {'Y1':>6} | {'F2':>9} {'Y2':>6} | {'F3':>9} {'Y3':>6}"
    )
    print("-" * 68)
    for i, X in enumerate(X_GRID):
        row = f"{int(X):>5} |"
        for k in range(3):
            f = F_tables[k][i]
            y = Y_tables[k][i]
            row += f" {f:9.2f} {y:6.1f} |"
        print(row)

    print(f"\nOptimal trajectory from Z = 15:")
    total_income = 0.0
    for step, (y, x_prev, x_next) in enumerate(
        zip(trajectory, X_states[:-1], X_states[1:]), 1
    ):
        income = (4.0 * y + 0.05 * y**2) + (
            3.0 * (x_prev - y) + 0.1 * (x_prev - y) ** 2
        )
        total_income += income
        print(
            f"  Quarter {step}: X={x_prev:.2f}, Y*={y:.1f}, "
            f"income={income:.2f},  X_next={x_next:.4f}"
        )
    print(f"\n  Maximum total income:  F3(15) = {F_tables[2][-1]:.4f}")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  Lab 3 — Optimization Methods & Dynamic Programming")
    print("  Variant 1   |   Drankov A.E.")
    print("=" * 65)

    res1, sp1, sens1 = solve_task1()
    print_task1(res1, sp1, sens1)

    Xg2, F2, Y2, traj2, Xst2 = solve_task2()
    print_task2(Xg2, F2, Y2, traj2, Xst2)

    opt3, ms3o, idle3o, sch3o, ms3p, idle3p, sch3p = solve_task3()
    print_task3(opt3, ms3o, idle3o, sch3o, ms3p, idle3p, sch3p)

    F4, pol4, path4 = solve_task4()
    print_task4(F4, pol4, path4)

    Xg5, F5, Y5, traj5, Xst5 = solve_task5()
    print_task5(Xg5, F5, Y5, traj5, Xst5)
