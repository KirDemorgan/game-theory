import math
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib import colors


def create_report_document():

    pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", "arialbd.ttf"))

    filename = "Отчет_СМО.pdf"
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )
    story = []

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontName="Arial-Bold",
        fontSize=18,
        textColor=colors.HexColor("#1F4E78"),
        spaceAfter=12,
        alignment=1,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontName="Arial-Bold",
        fontSize=14,
        textColor=colors.HexColor("#2E5C8A"),
        spaceAfter=10,
        spaceBefore=10,
    )

    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=11,
        spaceAfter=6,
    )

    story.append(Paragraph("ОТЧЕТ ПО ЛАБОРАТОРНОЙ РАБОТЕ", title_style))
    story.append(Paragraph("Теория массового обслуживания (СМО)", heading_style))
    story.append(Spacer(1, 0.1 * inch))
    story.append(
        Paragraph(
            f"<i>Дата выполнения: 14.05.2026 </i>",
            normal_style,
        )
    )
    story.append(Paragraph("Выполнил: Дранков А. Е.", normal_style))
    story.append(Spacer(1, 0.2 * inch))

    return doc, story, heading_style, normal_style


def task_one_output(data):
    heading_style = data["heading_style"]
    normal_style = data["normal_style"]

    content = []
    content.append(Paragraph("ЗАДАЧА 1: Многоканальная СМО с отказами", heading_style))

    table_data = [
        ["Параметр", "Значение"],
        ["Минимальное число каналов (Q ≥ 95%)", f"{data['k_min']} каналов"],
        ["Вероятность простоя (P0)", f"{data['p0']:.5f}"],
        ["Вероятность отказа (P_отк)", f"{data['p_refusal']:.5f}"],
        ["Относительная пропускная способность (Q)", f"{data['Q']:.5f}"],
        ["Абсолютная пропускная способность (A)", f"{data['A']:.5f} зав/ч"],
        ["Среднее число занятых каналов", f"{data['k_busy']:.5f}"],
        ["Коэффициент загрузки каналов", f"{data['k_util']:.5f}"],
    ]

    t = Table(table_data, colWidths=[3 * inch, 2.5 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Arial"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    content.append(t)
    content.append(Spacer(1, 0.15 * inch))
    return content


def task_two_output(data):
    heading_style = data["heading_style"]
    normal_style = data["normal_style"]

    content = []
    content.append(
        Paragraph(
            "ЗАДАЧА 2: Многоканальная СМО с неограниченной очередью", heading_style
        )
    )

    table_data = [
        ["Параметр", "При k_min", "При k_opt"],
        ["Нагрузка (ρ)", f"{data['rho']:.5f}", f"{data['rho']:.5f}"],
        ["Число каналов", f"{data['k_min']}", f"{data['k_opt']}"],
        ["P0", f"{data['p0_min']:.5f}", "-"],
        ["Длина очереди (Lq)", f"{data['Lq_min']:.5f}", "-"],
        ["Заявок в системе (Ls)", f"{data['Ls_min']:.5f}", "-"],
        ["Ожидание в очереди (Wq)", f"{data['Wq_min']:.5f} ч.", "-"],
        ["Пребывание в системе (Ws)", f"{data['Ws_min']:.5f} ч.", "-"],
        ["Затраты (C)", f"{data['cost_min']:.5f}", f"{data['cost_opt']:.5f}"],
    ]

    t = Table(table_data, colWidths=[2.2 * inch, 1.9 * inch, 1.9 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Arial"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    content.append(t)
    content.append(Spacer(1, 0.05 * inch))

    note_style = ParagraphStyle(
        "Note",
        parent=getSampleStyleSheet()["Normal"],
        fontName="Arial",
        fontSize=9,
        textColor=colors.HexColor("#404040"),
    )
    content.append(
        Paragraph(
            f"<i>Вероятность очереди ≤ {data['n_queue']} заявок: {data['p_queue']:.5f}</i>",
            note_style,
        )
    )
    content.append(Spacer(1, 0.15 * inch))

    return content


def task_three_output(data):
    heading_style = data["heading_style"]

    content = []
    content.append(
        Paragraph("ЗАДАЧА 3: Многоканальная СМО с ограниченной очередью", heading_style)
    )

    table_data = [
        ["Параметр", "Значение"],
        ["P0 (система пуста)", f"{data['p0']:.5f}"],
        ["Вероятность отказа (P_отк)", f"{data['p_refusal']:.5f}"],
        ["Относительная пропускная способность (Q)", f"{data['Q']:.5f}"],
        ["Абсолютная пропускная способность (A)", f"{data['A']:.5f} зав/ч"],
        ["В очереди (Lq)", f"{data['Lq']:.5f}"],
        ["Под обслуживанием (L_об)", f"{data['k_busy']:.5f}"],
        ["В системе (Ls)", f"{data['Ls']:.5f}"],
        ["Время ожидания (Wq)", f"{data['Wq']:.5f} мин."],
        ["Время обслуживания", f"{data['W_obs']:.5f} мин."],
        ["Время в системе (Ws)", f"{data['Ws']:.5f} мин."],
        ["Потеря выручки за период", f"{data['loss']:.5f} у.е."],
    ]

    t = Table(table_data, colWidths=[3 * inch, 2.5 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Arial"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    content.append(t)
    content.append(Spacer(1, 0.15 * inch))

    return content


def task_four_output(data):
    heading_style = data["heading_style"]

    content = []
    content.append(Paragraph("ЗАДАЧА 4: СМО с «нетерпеливыми» заявками", heading_style))

    table_data = [
        ["Параметр", "Значение"],
        ["P0 (система пуста)", f"{data['p0']:.5f}"],
        ["Вероятность обслуживания (P_обсл)", f"{data['P_obs']:.5f}"],
        ["Вероятность ухода заявки (P_уход)", f"{data['P_leave']:.5f}"],
        ["Среднее число в очереди (Lq)", f"{data['Lq']:.5f}"],
        ["Среднее число в системе (Ls)", f"{data['Ls']:.5f}"],
        ["Время ожидания (Wq)", f"{data['Wq']:.5f} мин."],
        ["Время обслуживания (W_obs)", f"{data['W_obs']:.5f} мин."],
        ["Время в системе (Ws)", f"{data['Ws']:.5f} мин."],
        ["Средние потери дохода", f"{data['Loss']:.5f} у.е./мин"],
    ]

    t = Table(table_data, colWidths=[3 * inch, 2.5 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Arial"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    content.append(t)
    content.append(Spacer(1, 0.15 * inch))

    return content


def task_five_output(data):
    heading_style = data["heading_style"]
    normal_style = data["normal_style"]

    content = []
    content.append(
        Paragraph(
            "ЗАДАЧА 5: Замкнутая одноканальная СМО (система Энгсета)", heading_style
        )
    )

    table_data = [
        ["Параметр", "Значение"],
        ["Интенсивность λ (в день)", f"{data['lambda_rate']:.4f}"],
        ["Интенсивность μ (в день)", f"{data['mu_rate']:.4f}"],
        ["Вероятность активно ≥ 85% источников", f"{data['prob_target']:.5f}"],
        ["Среднее число неисправных (Ls)", f"{data['L_broken']:.5f}"],
        ["Абсолютная пропускная способность", f"{data['A']:.5f} заявок/день"],
        ["Среднее время ожидания ремонта (Wq)", f"{data['W_q']:.5f} дн."],
        ["Время в ремонте и очереди (Ws)", f"{data['W_s']:.5f} дн."],
    ]

    t = Table(table_data, colWidths=[3 * inch, 2.5 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Arial"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    content.append(t)
    content.append(Spacer(1, 0.15 * inch))

    return content


def task_six_output(data):
    heading_style = data["heading_style"]

    content = [Paragraph("ЗАДАЧА 6: Замкнутая многоканальная СМО", heading_style)]

    table_data = [
        ["Показатель", "Значение"],
        ["P0 (все каналы свободны)", f"{data['p0']:.5f}"],
        ["Вероятность наличия очереди (P_очер)", f"{data['P_queue']:.5f}"],
        ["Среднее число в очереди (Lq)", f"{data['Lq']:.5f}"],
        ["Среднее число в системе (Ls)", f"{data['Ls']:.5f}"],
        ["Средние свободные каналы", f"{data['k_free']:.5f}"],
        ["Средние занятые каналы", f"{data['k_busy']:.5f}"],
        ["Абсолютная пропускная способность (A)", f"{data['A']:.5f} зав/ч"],
        ["Относительная пропускная способность (Q)", f"{data['Q']:.5f}"],
        ["Среднее время в очереди (Wq)", f"{data['W_q']:.5f} ч."],
        ["Среднее время обслуживания", f"{data['W_obs']:.5f} ч."],
        ["Среднее время в системе (Ws)", f"{data['W_s']:.5f} ч."],
    ]

    t = Table(table_data, colWidths=[3 * inch, 2.5 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Arial"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    content.append(t)
    content.append(Spacer(1, 0.15 * inch))

    return content


def solve_task_1(alpha_h, n_day, target_k):
    # Рассчитываем интенсивности поступления и обслуживания
    arrival_rate = n_day / 24.0
    service_rate = 1.0 / alpha_h
    intensity = arrival_rate / service_rate

    def get_metrics(k):
        # Сумма вероятностей для формулы Эрланга
        sum_p = sum((intensity**i) / math.factorial(i) for i in range(k + 1))
        p0 = 1.0 / sum_p
        p_refusal = (intensity**k) / math.factorial(k) * p0
        throughput = 1.0 - p_refusal
        absolute_throughput = arrival_rate * throughput
        k_busy = intensity * throughput
        utilization = k_busy / k
        return p0, p_refusal, throughput, absolute_throughput, k_busy, utilization

    # Ищем минимальное число каналов для обеспечения Q >= 95%
    k_min = 1
    while True:
        _, _, Q, _, _, _ = get_metrics(k_min)
        if Q >= 0.95:
            break
        k_min += 1

    p0, p_ref, Q, A, k_busy, k_util = get_metrics(target_k)

    return {
        "k_min": k_min,
        "p0": p0,
        "p_refusal": p_ref,
        "Q": Q,
        "A": A,
        "k_busy": k_busy,
        "k_util": k_util,
    }


def solve_task_2(lmbda_day, t_min, alpha_cost, n_queue):
    arrival_rate = lmbda_day / 24.0
    service_rate = 60.0 / t_min
    intensity = arrival_rate / service_rate

    k_min = math.floor(intensity) + 1

    def get_metrics_inf(k):
        sum_p = sum((intensity**i) / math.factorial(i) for i in range(k))
        p0 = 1.0 / (sum_p + (intensity**k) / (math.factorial(k) * (1 - intensity / k)))

        P_k = (intensity**k) / math.factorial(k) * p0
        queue_length = P_k * (intensity / k) / ((1 - intensity / k) ** 2)
        queue_wait_time = queue_length / arrival_rate

        system_length = queue_length + intensity
        total_time = queue_wait_time + 1 / service_rate

        cost = (k / arrival_rate) + alpha_cost * total_time

        return p0, queue_length, system_length, queue_wait_time, total_time, cost

    p0_min, Lq_min, Ls_min, Wq_min, Ws_min, cost_min = get_metrics_inf(k_min)

    best_k = k_min
    best_cost = cost_min
    # Ищем оптимальное число каналов с минимальными затратами
    for k in range(k_min + 1, k_min + 10):
        _, _, _, _, _, cost = get_metrics_inf(k)
        if cost < best_cost:
            best_cost = cost
            best_k = k

    p_queue_le_n = 0
    for i in range(k_min + n_queue + 1):
        if i <= k_min:
            p_i = (intensity**i) / math.factorial(i) * p0_min
        else:
            p_i = (
                (intensity**i)
                / (math.factorial(k_min) * (k_min ** (i - k_min)))
                * p0_min
            )
        p_queue_le_n += p_i

    return {
        "rho": intensity,
        "k_min": k_min,
        "k_opt": best_k,
        "p0_min": p0_min,
        "Lq_min": Lq_min,
        "Ls_min": Ls_min,
        "Wq_min": Wq_min,
        "Ws_min": Ws_min,
        "cost_min": cost_min,
        "cost_opt": best_cost,
        "n_queue": n_queue,
        "p_queue": p_queue_le_n,
    }


def solve_task_3(lmbda_h, t_min, k, n, T_hours, C_cost):
    arrival_rate = lmbda_h
    service_rate = 60.0 / t_min
    intensity = arrival_rate / service_rate

    sum_k = sum((intensity**i) / math.factorial(i) for i in range(k + 1))
    sum_n = sum(
        (intensity**i) / (math.factorial(k) * (k ** (i - k)))
        for i in range(k + 1, k + n + 1)
    )
    p0 = 1.0 / (sum_k + sum_n)

    p_refusal = (intensity ** (k + n)) / (math.factorial(k) * (k**n)) * p0
    Q = 1.0 - p_refusal
    A = arrival_rate * Q

    P_k = (intensity**k) / math.factorial(k) * p0
    rho_k = intensity / k
    if rho_k == 1:
        Lq = P_k * n * (n + 1) / 2
    else:
        Lq = (
            P_k
            * rho_k
            * (1 - (n + 1) * (rho_k**n) + n * (rho_k ** (n + 1)))
            / ((1 - rho_k) ** 2)
        )

    k_busy = intensity * Q
    Ls = Lq + k_busy

    Wq = Lq / arrival_rate
    Ws = Ls / arrival_rate
    W_obs = Ws - Wq

    S_loss = C_cost * arrival_rate * p_refusal * T_hours

    return {
        "p0": p0,
        "p_refusal": p_refusal,
        "Q": Q,
        "A": A,
        "Lq": Lq,
        "k_busy": k_busy,
        "Ls": Ls,
        "Wq": Wq * 60,
        "W_obs": W_obs * 60,
        "Ws": Ws * 60,
        "loss": S_loss,
    }


def solve_task_4(lmbda, t_obs, k, omega, C_cost, eps):
    service_rate = 1.0 / t_obs
    intensity = lmbda / service_rate
    theta = 1.0 / omega

    sum_p = sum((intensity**i) / math.factorial(i) for i in range(k + 1))

    j = 1
    prod = 1.0
    sum_q = 0.0
    P_queue_terms = []

    while True:
        prod *= lmbda / (k * service_rate + j * theta)
        P_queue_terms.append(prod)
        sum_q += prod

        if prod * (intensity**k) / math.factorial(k) < eps:
            break
        j += 1

    p0 = 1.0 / (sum_p + ((intensity**k) / math.factorial(k)) * sum_q)

    Pk = p0 * (intensity**k) / math.factorial(k)
    P_queue = [Pk * term for term in P_queue_terms]

    Lq = sum(j * P_queue[j - 1] for j in range(1, len(P_queue) + 1))

    v_leave = Lq / omega
    P_leave = v_leave / lmbda
    P_obs = 1.0 - P_leave

    k_busy = lmbda * P_obs / service_rate
    Ls = Lq + k_busy
    Wq = Lq / lmbda
    Ws = Ls / lmbda
    W_obs = Ws - Wq

    Loss = C_cost * v_leave

    return {
        "p0": p0,
        "P_obs": P_obs,
        "P_leave": P_leave,
        "Lq": Lq,
        "Ls": Ls,
        "Wq": Wq,
        "W_obs": W_obs,
        "Ws": Ws,
        "Loss": Loss,
    }


def solve_task_5(n_sources, k_req_per_month, t_days, target_P_percent):
    lambda_rate = k_req_per_month / 30.0
    mu_rate = 1.0 / t_days
    intensity = lambda_rate / mu_rate

    P_raw = []
    for i in range(n_sources + 1):
        term = (math.factorial(n_sources) / math.factorial(n_sources - i)) * (
            intensity**i
        )
        P_raw.append(term)

    p0 = 1.0 / sum(P_raw)
    P = [p * p0 for p in P_raw]

    min_active = math.ceil(n_sources * target_P_percent / 100.0)
    max_broken = n_sources - min_active

    prob_target = sum(P[i] for i in range(max_broken + 1))

    L_broken = sum(i * P[i] for i in range(n_sources + 1))
    A = mu_rate * (1.0 - P[0])
    W_s = L_broken / A
    W_q = W_s - (1.0 / mu_rate)

    return {
        "lambda_rate": lambda_rate,
        "mu_rate": mu_rate,
        "prob_target": prob_target,
        "L_broken": L_broken,
        "A": A,
        "W_q": W_q,
        "W_s": W_s,
    }


def solve_task_6(k_channels, n_sources, lmbda, t_obs):
    service_rate = 1.0 / t_obs
    intensity = lmbda / service_rate

    P_raw = []
    for i in range(n_sources + 1):
        if i <= k_channels:
            term = math.comb(n_sources, i) * (intensity**i)
        else:
            term = (
                math.comb(n_sources, i)
                * (
                    math.factorial(i)
                    / (math.factorial(k_channels) * (k_channels ** (i - k_channels)))
                )
                * (intensity**i)
            )
        P_raw.append(term)

    p0 = 1.0 / sum(P_raw)
    P = [p * p0 for p in P_raw]

    Lq = sum((i - k_channels) * P[i] for i in range(k_channels + 1, n_sources + 1))
    Ls = sum(i * P[i] for i in range(n_sources + 1))

    k_busy = sum(i * P[i] for i in range(1, k_channels + 1)) + sum(
        k_channels * P[i] for i in range(k_channels + 1, n_sources + 1)
    )
    k_free = k_channels - k_busy

    A = service_rate * k_busy
    Q = A / (n_sources * lmbda)
    P_queue = sum(P[i] for i in range(k_channels + 1, n_sources + 1))

    W_s = Ls / A
    W_q = Lq / A
    W_obs = k_busy / A

    return {
        "p0": p0,
        "P_queue": P_queue,
        "Lq": Lq,
        "Ls": Ls,
        "k_free": k_free,
        "k_busy": k_busy,
        "A": A,
        "Q": Q,
        "W_q": W_q,
        "W_obs": W_obs,
        "W_s": W_s,
    }


if __name__ == "__main__":
    doc, story, heading_style, normal_style = create_report_document()

    data_style = {"heading_style": heading_style, "normal_style": normal_style}

    result_1 = solve_task_1(alpha_h=1.5, n_day=48, target_k=5)
    result_1.update(data_style)
    story.extend(task_one_output(result_1))

    result_2 = solve_task_2(lmbda_day=250, t_min=12, alpha_cost=3, n_queue=3)
    result_2.update(data_style)
    story.extend(task_two_output(result_2))

    result_3 = solve_task_3(lmbda_h=6, t_min=1, k=10, n=4, T_hours=8, C_cost=95)
    result_3.update(data_style)
    story.extend(task_three_output(result_3))

    story.append(PageBreak())

    result_4 = solve_task_4(
        lmbda=2.0, t_obs=0.8, k=3, omega=4.0, C_cost=100.0, eps=0.001
    )
    result_4.update(data_style)
    story.extend(task_four_output(result_4))

    result_5 = solve_task_5(
        n_sources=16, k_req_per_month=2, t_days=1.0, target_P_percent=85
    )
    result_5.update(data_style)
    story.extend(task_five_output(result_5))

    result_6 = solve_task_6(k_channels=4, n_sources=18, lmbda=2.1, t_obs=0.4)
    result_6.update(data_style)
    story.extend(task_six_output(result_6))

    doc.build(story)
    print("Отчет успешно создан: Отчет_СМО.pdf")
