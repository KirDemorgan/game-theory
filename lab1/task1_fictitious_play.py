import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

def solve_fp(A, iterations=5000):
    n, m = A.shape
    
    p1_strategy_counts = np.zeros(n)
    p2_strategy_counts = np.zeros(m)
    
    p1_sums = np.zeros(n)
    p2_sums = np.zeros(m)
    
    lower_bounds = []
    upper_bounds = []
    
    row = np.random.randint(n)
    col = np.random.randint(m)

    for t in range(1, iterations + 1):
        p1_strategy_counts[row] += 1
        p2_strategy_counts[col] += 1
        
        p1_sums += A[:, col]
        p2_sums += A[row, :]
        
        lower_bound = np.max(p1_sums) / t
        upper_bound = np.min(p2_sums) / t
        
        lower_bounds.append(lower_bound)
        upper_bounds.append(upper_bound)
        
        row = np.argmax(p1_sums)
        col = np.argmin(p2_sums)
        
    p1_prob = p1_strategy_counts / iterations
    p2_prob = p2_strategy_counts / iterations
    
    approx_value = (lower_bounds[-1] + upper_bounds[-1]) / 2.0
    
    return p1_prob, p2_prob, approx_value, lower_bounds, upper_bounds

def solve_lp(A):
    n, m = A.shape
    c_shift = A.min() - 1
    
    if c_shift <= 0:
        A_pos = A - c_shift
    else:
        A_pos = A
        c_shift = 0
        
    c_p1 = np.ones(n)
    A_ub_p1 = -A_pos.T
    b_ub_p1 = -np.ones(m)
    res_p1 = linprog(c=c_p1, A_ub=A_ub_p1, b_ub=b_ub_p1, bounds=(0, None))
    
    v_p1 = 1 / res_p1.fun
    opt_p1 = res_p1.x * v_p1
    
    c_p2 = -np.ones(m)
    res_p2 = linprog(c=c_p2, A_ub=A_pos, b_ub=np.ones(n), bounds=(0, None))
    
    v_p2 = 1 / (-res_p2.fun)
    opt_p2 = res_p2.x * v_p2
    
    return opt_p1, opt_p2, v_p1 + c_shift

def main():
    np.random.seed(42)
    n, m = 12, 15
    A = np.random.randint(-100, 101, size=(n, m))
    
    print("Матрица платежей A (12x15):")
    print(A)
    
    iters = 5000
    p1_fp, p2_fp, val_fp, lb, ub = solve_fp(A, iters)
    
    p1_lp, p2_lp, val_lp = solve_lp(A)
    
    print(f"\nМетод Брауна-Робинсона (Итераций: {iters}):")
    print(f"Приближенная цена игры: {val_fp:.4f}")
    
    print(f"\nЛинейное программирование:")
    print(f"Точная цена игры: {val_lp:.4f}")
    print(f"Разница оценок цены игры: {abs(val_fp - val_lp):.4f}")
    
    plt.figure(figsize=(10, 6))
    plt.plot(lb, label="Нижняя цена (v_min)", color='blue', alpha=0.7)
    plt.plot(ub, label="Верхняя цена (v_max)", color='red', alpha=0.7)
    plt.axhline(val_lp, color='green', linestyle='--', label="Точная цена (LP)")
    plt.title("Сходимость метода брауза-Робинсона (Fictitious Play)")
    plt.xlabel("Номер итерации")
    plt.ylabel("Оценка цены игры")
    plt.legend()
    plt.grid()
    plt.savefig('task1_plot.png')
    print("\nГрафик сохранен в task1_plot.png")

if __name__ == '__main__':
    main()
