import sys
import numpy as np

def calculate_ahp_vector_and_consistency(matrix):
    n = matrix.shape[0]
    geom_mean = np.prod(matrix, axis=1) ** (1 / n)
    weights = geom_mean / np.sum(geom_mean)
    
    Aw = np.dot(matrix, weights)
    lambda_max = np.mean(Aw / weights)
    
    CI = (lambda_max - n) / (n - 1)
    
    RC_dict = {1:0.0, 2:0.0, 3:0.58, 4:0.90, 5:1.12, 6:1.24, 7:1.32, 8:1.41, 9:1.45}
    RC = RC_dict.get(n, 1.49)
    
    if RC == 0:
        CR = 0.0
    else:
        CR = CI / RC
        
    return weights, CI, CR

def get_matrix_from_input(size, default_matrix, name):
    print(f"\n--- Ввод матрицы парных сравнений: {name} ({size}x{size}) ---")
    print("Нажмите Enter без ввода данных, чтобы использовать матрицу по умолчанию.")
    
    while True:
        try:
            line = input(f"Введите элементы матрицы через пробел построчно, или пусто для default:\n")
            if not line.strip():
                print("Используется матрица по умолчанию.")
                return default_matrix.copy()
            else:
                elements = list(map(float, line.strip().split()))
                if len(elements) != size * size:
                    print(f"Ошибка: нужно ввести {size*size} чисел.")
                    continue
                mat = np.array(elements).reshape((size, size))
                
                is_valid = True
                for i in range(size):
                    for j in range(size):
                        if abs(mat[i, j] * mat[j, i] - 1.0) > 1e-5 and i != j:
                            print("Матрица должна быть обратно симметричной! a_ij = 1 / a_ji")
                            is_valid = False
                            break
                    if not is_valid: break
                
                if not is_valid: continue
                
                _, _, CR = calculate_ahp_vector_and_consistency(mat)
                if CR > 0.1:
                    print(f"Внимание: Индекс CR={CR:.3f} > 0.1. Суждения несогласованы. Повторите ввод.")
                    continue
                return mat
                
        except EOFError:
            print("Ввод перенаправлен, используется матрица по умолчанию.")
            return default_matrix.copy()
        except ValueError:
            print("Ошибка парсинга чисел. Попробуйте еще раз.")

def run_ahp():
    criteria = ["Производительность", "Надежность", "Масштабируемость", "Простота интеграции"]
    alternatives = ["Kafka", "RabbitMQ", "Redis", "NATS", "Pulsar", "ActiveMQ"]
    
    k = len(criteria)
    n = len(alternatives)
    
    default_criteria_mat = np.array([
        [1, 1/3, 1/5, 3],
        [3, 1, 1/2, 5],
        [5, 2, 1, 7],
        [1/3, 1/5, 1/7, 1]
    ])
    
    def_alt_mats = []
    m1 = np.ones((n, n)); m1[0,1] = 3; m1[1,0] = 1/3; m1[0,2] = 2; m1[2,0] = 1/2; m1[3,4] = 2; m1[4,3] = 1/2
    w_perf = [0.35, 0.15, 0.05, 0.20, 0.20, 0.05]
    w_rel = [0.30, 0.40, 0.05, 0.10, 0.10, 0.05]
    w_scal = [0.45, 0.10, 0.05, 0.10, 0.25, 0.05]
    w_ease = [0.10, 0.30, 0.40, 0.10, 0.05, 0.05]
    
    def_weights = [w_perf, w_rel, w_scal, w_ease]
    for w in def_weights:
        mat = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                mat[i, j] = w[i] / w[j]
        def_alt_mats.append(mat)
        
    print("=== Метод AHP: Выбор Брокера Сообщений ===")
    
    crit_mat = get_matrix_from_input(k, default_criteria_mat, "Сравнение критериев")
    crit_weights, ci, cr = calculate_ahp_vector_and_consistency(crit_mat)
    
    print(f"\nВеса критериев:")
    for c, w in zip(criteria, crit_weights):
        print(f"  {c}: {w:.4f}")
    print(f"CR критериев: {cr:.3f}")
    
    alt_weights_matrix = np.zeros((n, k))
    
    for i, crit in enumerate(criteria):
        alt_mat = get_matrix_from_input(n, def_alt_mats[i], f"Сравнение альтернатив по {crit}")
        loc_weights, _, loc_cr = calculate_ahp_vector_and_consistency(alt_mat)
        alt_weights_matrix[:, i] = loc_weights
        print(f"\nЛокальные веса по '{crit}' (CR={loc_cr:.3f}):")
        for alt, aw in zip(alternatives, loc_weights):
            print(f"  {alt}: {aw:.4f}")
            
    global_weights = np.dot(alt_weights_matrix, crit_weights)
    
    print("\n=== Итоговый рейтинг альтернатив ===")
    scores = [(alternatives[i], global_weights[i]) for i in range(n)]
    scores.sort(key=lambda x: x[1], reverse=True)
    
    for rank, (alt, score) in enumerate(scores, 1):
        print(f"{rank}. {alt}: {score:.4f}")
        
    print(f"\nЛучшая технология по результатам AHP: {scores[0][0]}")

if __name__ == '__main__':
    run_ahp()
