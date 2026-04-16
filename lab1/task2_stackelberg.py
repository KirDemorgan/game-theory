import numpy as np
import scipy.optimize as opt

def solve_stackelberg():
    np.random.seed(42)
    V = np.array([100, 150, 200, 120, 80])
    C = np.array([20, 30, 40, 25, 10])
    
    P_def = np.array([0.1, 0.15, 0.05, 0.2, 0.1])
    P_nodef = np.array([0.8, 0.9, 0.95, 0.7, 0.6])
    
    B = 70
    
    N = len(V)
    c = np.zeros(N + 1)
    c[0] = 1
    
    A_ub = np.zeros((N, N + 1))
    b_ub = np.zeros(N)
    for i in range(N):
        A_ub[i, 0] = -1
        A_ub[i, i+1] = V[i] * (P_def[i] - P_nodef[i])
        b_ub[i] = -V[i] * P_nodef[i]
        
    A_budget = np.zeros(N + 1)
    for i in range(N):
        A_budget[i+1] = C[i]
    
    A_ub = np.vstack((A_ub, A_budget))
    b_ub = np.append(b_ub, B)
    
    bounds = [(0, None)] + [(0, 1) for _ in range(N)]
    
    res = opt.linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds)
    
    print("--- Задача 2: Моделирование атаки как игра Штакельберга ---")
    if res.success:
        Z_opt = res.x[0]
        x_opt = res.x[1:]
        print(f"Оптимальный ожидаемый ущерб (Z, минимакс): {Z_opt:.2f}")
        for i in range(N):
            print(f"Узел {i}: Вероятность защиты = {x_opt[i]:.4f}")
            
        att_damages = V * (x_opt * P_def + (1 - x_opt) * P_nodef)
        attack_node = np.argmax(att_damages)
        
        print("\nОжидаемый ущерб для Атакующего по каждому узлу:")
        for i, val in enumerate(att_damages):
            print(f" Узел {i}: {val:.2f}")
        
        print(f"\nВывод Атакующего:")
        print(f"Атакующий выберет узел {attack_node} (Ценность={V[attack_node]}), так как ожидаемый ущерб максимален ({att_damages[attack_node]:.2f})")
    else:
        print("Оптимизация не удалась:", res.message)

if __name__ == '__main__':
    solve_stackelberg()
