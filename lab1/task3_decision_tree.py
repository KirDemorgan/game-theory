import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def build_and_evaluate_tree():
    decisions = {
        "Быстрый релиз": {"cost": 100},
        "Тестирование":  {"cost": 300},
        "Отмена":        {"cost": 0}
    }
    
    env_states = {
        "Стабильная нагрузка": 0.6,
        "Пиковая нагрузка": 0.3,
        "Сбой зависимости": 0.1
    }
    
    outcomes_payoff = {
        "Успех": 1000,
        "Частичный успех": 400,
        "Провал": -800
    }
    
    probs = {
        "Быстрый релиз": {
            "Стабильная нагрузка": {"Успех": 0.7, "Частичный успех": 0.2, "Провал": 0.1},
            "Пиковая нагрузка":    {"Успех": 0.3, "Частичный успех": 0.4, "Провал": 0.3},
            "Сбой зависимости":    {"Успех": 0.0, "Частичный успех": 0.2, "Провал": 0.8}
        },
        "Тестирование": {
            "Стабильная нагрузка": {"Успех": 0.9, "Частичный успех": 0.1, "Провал": 0.0},
            "Пиковая нагрузка":    {"Успех": 0.6, "Частичный успех": 0.3, "Провал": 0.1},
            "Сбой зависимости":    {"Успех": 0.1, "Частичный успех": 0.5, "Провал": 0.4}
        }
    }
    
    results = {}
    
    for dec, dec_info in decisions.items():
        if dec == "Отмена":
            results[dec] = {"EMV": 0, "Sigma": 0}
            continue
            
        cost = dec_info["cost"]
        expected_value = 0
        paths = []
        
        for env, p_env in env_states.items():
            for out, p_out in probs[dec][env].items():
                prob_path = p_env * p_out
                payoff_path = outcomes_payoff[out] - cost
                expected_value += prob_path * payoff_path
                if prob_path > 0:
                    paths.append((prob_path, payoff_path))
                    
        variance = 0
        for p_path, p_payoff in paths:
            variance += p_path * ((p_payoff - expected_value) ** 2)
        sigma = np.sqrt(variance)
        
        results[dec] = {"EMV": expected_value, "Sigma": sigma}
        
    print("--- Задание 3: Позиционная игра с вычислением риска ---")
    for dec, res in results.items():
        print(f"Стратегия: {dec:20s} | EMV: {res['EMV']:7.2f} | Риск (σ): {res['Sigma']:7.2f}")
        
    print("\nАнализ компромисса:")
    print("Быстрый релиз имеет более высокий ожидаемый доход, но очень высокий риск.")
    print("Тестирование требует затрат, что снижает пиковую прибыль, однако резко снижает дисперсию (риск) при сбоях.")
    print("Оптимальный выбор зависит от склонности к риску. Для риск-нейтрального субъекта - выбирается максимальный EMV.")

    G = nx.DiGraph()
    root = "Решение"
    G.add_node(root)
    
    node_labels = {root: root}
    pos_idx = 0
    
    labels = {}
    
    layer0 = [root]
    layer1 = list(decisions.keys())
    for d in layer1:
        G.add_edge(root, d)
        
    rep_dec = "Быстрый релиз"
    for e in env_states.keys():
        e_node = f"{rep_dec}\n{e}"
        G.add_edge(rep_dec, e_node)
        for o in outcomes_payoff.keys():
            if probs[rep_dec][e][o] > 0:
                o_node = f"{e_node}\n{o}"
                G.add_edge(e_node, o_node)

    plt.figure(figsize=(14, 8))
    pos = nx.spring_layout(G, k=0.9, iterations=50)
    
    try:
        from networkx.drawing.nx_agraph import graphviz_layout
        pos = graphviz_layout(G, prog='dot')
    except ImportError:
        pass
        
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=8, font_weight='bold', font_family='sans-serif', arrowsize=20)
    plt.title("Фрагмент дерева решений (ветвь 'Быстрый релиз')")
    plt.savefig('task3_tree.png')
    print("График фрагмента дерева сохранен в task3_tree.png")

if __name__ == '__main__':
    build_and_evaluate_tree()
