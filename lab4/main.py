"""
CallCenterOpt - Оптимизатор штата колл-центра
Дранков А.Е. | Курс "Теория игр" | Итоговый проект

Использует теорию массового обслуживания M/M/c и критерии принятия решений
для рекомендации оптимального количества операторов при неопределенной нагрузке.
"""

import sys
import argparse
from pathlib import Path

import yaml
import numpy as np

from core.queue_math import calculate_mm_c_metrics
from core.game_solver import build_cost_matrix, apply_wald, apply_hurwicz, apply_bayes


def load_config(path: str) -> dict:
    """Загрузка и валидация YAML конфигурации."""
    cfg_path = Path(path)
    if not cfg_path.exists():
        raise FileNotFoundError(f"Файл конфигурации не найден: {path}")

    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    required = ["lambda_scenarios", "mu", "salary_per_operator", "penalty_factor"]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise KeyError(f"Отсутствуют обязательные поля: {missing}")
    if cfg["mu"] <= 0:
        raise ValueError("mu должно быть > 0")
    if any(lam < 0 for lam in cfg["lambda_scenarios"]):
        raise ValueError("Все значения lambda должны быть неотрицательными")

    return cfg


def print_cost_table(strategies, lambdas, matrix, best_idx):
    """Вывод матрицы затрат в виде таблицы."""
    col_w = 10
    header = f"{'c':>4} |" + "".join(f" lam={int(l):>4} |" for l in lambdas)
    print("\n" + header)
    print("-" * len(header))
    for i, c in enumerate(strategies):
        row = f"{c:>4} |" + "".join(
            f" {matrix[i, j]:>8.1f} |" for j in range(len(lambdas))
        )
        marker = " <-- оптимально" if i == best_idx else ""
        print(row + marker)


def print_sla_check(lambda_val: float, mu: float, c: int, sla_threshold: float):
    """Проверка соблюдения SLA для заданных параметров."""
    m = calculate_mm_c_metrics(lambda_val, mu, c)
    status = "OK" if m.p_wait <= sla_threshold else "НАРУШЕНО"
    print(f"\n  Проверка SLA при lambda={lambda_val:.1f}, c={c}:")
    print(f"    Загрузка     rho    = {m.rho:.3f}")
    print(f"    Вер. ожидания P_wait = {m.p_wait:.3f}  (порог: {sla_threshold})")
    print(f"    Длина очереди L_q    = {m.l_q:.3f}")
    print(f"    Время ожидания W     = {m.w * 60:.1f} мин")
    print(f"    Статус SLA          = {status}")


def run(cfg: dict, criterion: str = None, show_all: bool = False) -> None:
    """Основной анализ."""
    lambdas = cfg["lambda_scenarios"]
    strategies = cfg.get("strategies", [3, 5, 7, 9, 11])
    mu = cfg["mu"]
    salary = cfg["salary_per_operator"]
    penalty = cfg["penalty_factor"]
    alpha = cfg.get("alpha", 0.6)
    probs = cfg.get("probabilities", [1.0 / len(lambdas)] * len(lambdas))
    sla = cfg.get("sla_p_wait", 0.15)
    criterion = criterion or cfg.get("criterion", "hurwicz")

    print("=" * 60)
    print("  CallCenterOpt - Оптимизатор штата колл-центра")
    print("  Дранков А.Е. | Итоговый проект по теории игр")
    print("=" * 60)

    matrix = build_cost_matrix(lambdas, strategies, mu, salary, penalty)

    if show_all:
        criteria_to_run = ["wald", "hurwicz", "bayes"]
    else:
        criteria_to_run = [criterion]

    for crit in criteria_to_run:
        print(f"\n{'='*50}")
        if crit == "wald":
            idx, val = apply_wald(matrix)
            label = "Вальд (минимакс / пессимистический)"
        elif crit == "hurwicz":
            idx, val = apply_hurwicz(matrix, alpha)
            label = f"Гурвиц (alpha={alpha})"
        elif crit == "bayes":
            idx, val = apply_bayes(matrix, probs)
            label = f"Байес (E[затраты], вероятности={probs})"
        else:
            print(f"Неизвестный критерий: {crit}")
            continue

        best_c = strategies[idx]
        print(f"\nКритерий: {label}")
        print(f"Матрица затрат (тыс. руб./месяц):")
        print_cost_table(strategies, lambdas, matrix, idx)
        print(f"\nРекомендация: c = {best_c} операторов")
        print(f"Ожидаемые затраты: {val:.2f} тыс. руб./месяц")

        avg_lambda = float(np.mean(lambdas))
        print_sla_check(avg_lambda, mu, best_c, sla)

    if show_all:
        print(f"\n{'='*50}")
        print("\nПолная картина соблюдения SLA (P_wait <= {:.2f}):".format(sla))
        header = f"  {'c':>3} |" + "".join(f" lam={int(l):>3} |" for l in lambdas)
        print(header)
        print("  " + "-" * (len(header) - 2))
        for i, c in enumerate(strategies):
            row = f"  {c:>3} |"
            for lam in lambdas:
                m = calculate_mm_c_metrics(lam, mu, c)
                ok = "OK " if (m.p_wait <= sla and m.stable) else "FAIL"
                row += f"  {ok}  |"
            print(row)


def main():
    parser = argparse.ArgumentParser(description="CallCenterOpt - оптимизатор штата")
    parser.add_argument(
        "--config", default="config/scenario.yaml", help="Путь к YAML конфигурации"
    )
    parser.add_argument(
        "--criterion", choices=["wald", "hurwicz", "bayes"], help="Переопределить критерий"
    )
    parser.add_argument("--all", action="store_true", help="Сравнить все три критерия")
    args = parser.parse_args()

    try:
        cfg = load_config(args.config)
        run(cfg, criterion=args.criterion, show_all=args.all)
    except Exception as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
