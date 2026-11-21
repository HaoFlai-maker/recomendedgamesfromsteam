import re
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

COL_BLUE_DARK = "#1b3a4b"
COL_BLUE = "#2c6e8f"
COL_BLUE_MID = "#5d92ae"
COL_BLUE_LIGHT = "#8fa8b8"
COL_BLUE_PALE = "#b6c2ca"
COL_ORANGE = "#d1622a"
COL_GOLD = "#e6a23c"
COL_GREY = "#93a3ae"
COL_GRID = "#e3eaee"
COL_SPINE = "#c8d3da"

BAR_COLORS = [COL_BLUE_PALE, COL_BLUE_LIGHT, COL_BLUE_MID, COL_BLUE, COL_ORANGE]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.edgecolor": COL_BLUE_DARK,
    "axes.labelcolor": COL_BLUE_DARK,
    "axes.titlecolor": COL_BLUE_DARK,
    "text.color": COL_BLUE_DARK,
    "xtick.color": COL_BLUE_DARK,
    "ytick.color": COL_BLUE_DARK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
})

DPI = 160
OUT_DIR = Path(__file__).resolve().parent / "charts"

def fmt_float(x, nd=1):
    return f"{x:.{nd}f}".replace(".", ",")


def fmt_thousands(x):
    return f"{x:,.1f}".replace(",", " ").replace(".", ",")


def game_word(n):
    n = abs(int(n)) % 100
    if 11 <= n <= 19:
        return "игр"
    n %= 10
    if n == 1:
        return "игра"
    if 2 <= n <= 4:
        return "игры"
    return "игр"

def prepare_axes(ax, grid_axis="y"):
    ax.grid(axis=grid_axis, color=COL_GRID, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(COL_SPINE)

def add_header(fig, title, subtitle, source):
    fig.text(0.055, 0.955, title, fontsize=15.5, fontweight="bold",
             ha="left", va="top", color=COL_BLUE_DARK)
    fig.text(0.055, 0.888, subtitle, fontsize=10.5,
             ha="left", va="top", color="#5d6b74")
    fig.text(0.055, 0.012, source, fontsize=8.5,
             ha="left", va="bottom", color="#8a949c")

ROW_PATTERN = re.compile(r"^ID:\s*(\d+),\s*Название:\s*(.*),\s*Часы:\s*([\d.]+)\s*$")

def parse_file(path):
    data = []
    text = path.read_text(encoding="utf-8-sig")
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        match = ROW_PATTERN.match(line)
        if match is None:
            continue
        data.append({
            "appid": int(match.group(1)),
            "name": match.group(2).strip(),
            "hours": float(match.group(3)),
        })
    return data

def locate_file():
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
        data = parse_file(p)
        if len(data) == 0:
            sys.exit("Не удалось разобрать файл: " + str(p))
        print("Использую файл:", p)
        return data, p.name

    base = Path(__file__).resolve().parent
    options = [
        base / "games_data.csv",
        base / "games_data (1).csv",
        Path.home() / "Downloads" / "games_data (1).csv",
        Path.home() / "Downloads" / "games_data.csv",
    ]
    for opt in options:
        if opt.exists():
            data = parse_file(opt)
            if len(data) > 0:
                print("Использую файл:", opt)
                return data, opt.name

    sys.exit("Файл с данными не найден. Положите games_data.csv рядом со скриптом "
             "или укажите путь первым аргументом.")

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows, src_name = locate_file()
    n = len(rows)

    hours = np.array([r["hours"] for r in rows], dtype=float)
    appids = np.array([r["appid"] for r in rows], dtype=float)

    total_hours = hours.sum()
    median_hours = float(np.median(hours))
    mean_hours = float(hours.mean())

    source_line = (f"Источник: выгрузка игровой библиотеки Steam — {n} игр, "
                   f"{fmt_thousands(total_hours)} ч суммарно ({src_name}).")

    group_defs = [
        ("Ни разу не запускали", hours == 0, BAR_COLORS[0]),
        ("Меньше часа", (hours > 0) & (hours < 1), BAR_COLORS[1]),
        ("1–10 часов", (hours >= 1) & (hours < 10), BAR_COLORS[2]),
        ("10–50 часов", (hours >= 10) & (hours < 50), BAR_COLORS[3]),
        ("Больше 50 часов", hours >= 50, BAR_COLORS[4]),
    ]
    groups = [(label, int(mask.sum()), color) for label, mask, color in group_defs]

    small_games = sum(cnt for _, cnt, _ in groups[:3])
    small_share = small_games / n * 100

    fig, ax = plt.subplots(figsize=(12.4, 4.2), dpi=DPI)
    offset = 0.0
    for label, cnt, color in groups:
        pct = cnt / n * 100
        ax.barh(0, pct, left=offset, height=0.92, color=color,
                edgecolor="white", linewidth=2.0, zorder=3)
        ax.text(offset + pct / 2, 0.10, str(cnt), ha="center", va="center",
                fontsize=15, fontweight="bold", color="white", zorder=4)
        ax.text(offset + pct / 2, -0.16, f"{fmt_float(pct, 1)} %", ha="center",
                va="center", fontsize=9.5, color="white", zorder=4)
        offset += pct

    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ("left", "bottom"):
        ax.spines[s].set_visible(False)

    legend_patches = [Patch(facecolor=c, edgecolor="none", label=l)
                      for l, _, c in groups]
    ax.legend(handles=legend_patches, loc="upper center",
              bbox_to_anchor=(0.5, -0.06), ncol=5, frameon=False,
              fontsize=10.2, handlelength=1.4, columnspacing=1.6,
              handletextpad=0.6)

    add_header(
        fig,
        f"{fmt_float(small_share, 0)} % библиотеки — игры, в которые почти не играли",
        f"Из {n} игр {groups[0][1]} не запускали ни разу, ещё {groups[1][1]} — "
        f"меньше часа. Медиана вложенного времени — {fmt_float(median_hours, 1)} ч "
        f"на игру, меньше 10 часов набрали {small_games} {game_word(small_games)}.",
        source_line,
    )
    fig.subplots_adjust(left=0.055, right=0.99, top=0.79, bottom=0.235)
    fig.savefig(OUT_DIR / "01_struktura_biblioteki.png",
                bbox_inches="tight", pad_inches=0.32)
    plt.close(fig)

    sorted_desc = np.sort(hours)[::-1]
    cumulative = np.cumsum(sorted_desc) / total_hours * 100
    x_pct = np.arange(1, n + 1) / n * 100

    idx_50 = int(np.searchsorted(cumulative, 50) + 1)
    idx_80 = int(np.searchsorted(cumulative, 80) + 1)

    fig, ax = plt.subplots(figsize=(10.6, 6.8), dpi=DPI)
    ax.plot(x_pct, cumulative, color=COL_BLUE, linewidth=3.0, zorder=4,
            label="Реальное распределение времени")
    ax.plot([0, 100], [0, 100], color=COL_GREY, linewidth=1.8,
            linestyle=(0, (5, 4)), zorder=2,
            label="Если бы все игры игрались одинаково")
    ax.fill_between(x_pct, x_pct, cumulative, color=COL_BLUE,
                    alpha=0.10, zorder=1)

    markers = [
        (idx_50, 50, f"{idx_50} игр → половина времени", 13, 44),
        (idx_80, 80, f"{idx_80} игр → 80 % времени", 24, 72),
    ]
    for idx, val, text, tx, ty in markers:
        cx = idx / n * 100
        ax.scatter([cx], [val], s=110, color=COL_ORANGE, zorder=6,
                   edgecolor="white", linewidth=1.6)
        ax.vlines(cx, 0, val, color=COL_ORANGE, linewidth=1.1,
                  linestyle=":", zorder=3)
        ax.hlines(val, 0, cx, color=COL_ORANGE, linewidth=1.1,
                  linestyle=":", zorder=3)
        ax.annotate(text, xy=(cx, val), xytext=(tx, ty),
                    fontsize=11.5, fontweight="bold", color=COL_ORANGE,
                    arrowprops=dict(arrowstyle="-", color=COL_ORANGE,
                                    linewidth=1.1, shrinkA=2, shrinkB=7))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xticks(range(0, 101, 20))
    ax.set_yticks(range(0, 101, 20))
    ax.set_xlabel("Доля игр в библиотеке, % (игры отсортированы по времени)",
                  fontsize=11.5)
    ax.set_ylabel("Накопленная доля всего игрового времени, %", fontsize=11.5)
    ax.legend(loc="lower right", frameon=False, fontsize=10.5)

    add_header(
        fig,
        f"{fmt_float(idx_50 / n * 100, 1)} % игр забирают половину всего игрового времени",
        f"{idx_50} игр из {n} — это 50 % всех {fmt_thousands(total_hours)} ч; "
        f"{idx_80} игр (каждая седьмая) закрывают уже 80 % времени. "
        f"Остальные {n - idx_80} игр делят 20 %.",
        source_line,
    )
    fig.subplots_adjust(left=0.09, right=0.97, top=0.85, bottom=0.115)
    fig.savefig(OUT_DIR / "02_koncentraciya_vremeni.png",
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)

    top15 = sorted(rows, key=lambda r: r["hours"], reverse=True)[:15]
    top15.reverse()

    top_names = []
    for r in top15:
        nm = r["name"]
        top_names.append(nm if len(nm) <= 34 else nm[:32] + "…")

    top_values = [r["hours"] for r in top15]
    bar_colors_top = [COL_ORANGE if i >= len(top15) - 2 else COL_BLUE
                      for i in range(len(top15))]

    top15_share = sum(top_values) / total_hours * 100
    top2_share = (top_values[-1] + top_values[-2]) / total_hours * 100

    fig, ax = plt.subplots(figsize=(11.8, 7.4), dpi=DPI)
    bars = ax.barh(range(len(top15)), top_values, color=bar_colors_top,
                   height=0.72, zorder=3)
    max_val = max(top_values)
    for b, v in zip(bars, top_values):
        ax.text(v + max_val * 0.012, b.get_y() + b.get_height() / 2,
                f"{fmt_float(v, 1)} ч", va="center", fontsize=10.5,
                color=COL_BLUE_DARK,
                fontweight="bold" if v > 500 else "normal")

    ax.set_yticks(range(len(top15)))
    ax.set_yticklabels(top_names, fontsize=10.5)
    ax.set_xlabel("Накопленное время, часов", fontsize=11.5)
    ax.set_xlim(0, max_val * 1.17)
    prepare_axes(ax, "x")
    ax.tick_params(axis="y", length=0)

    ax.text(max_val * 0.47, 10.7,
            "■  Counter-Strike 2 + Dead by Daylight\n"
            f"     = {fmt_thousands(top_values[-1] + top_values[-2])} ч = "
            f"{fmt_float(top2_share, 0)} % всего времени",
            fontsize=11.5, fontweight="bold", color=COL_ORANGE,
            ha="left", va="center")

    add_header(
        fig,
        "Топ-15 игр: две игры забирают больше трети всего времени",
        f"Топ-15 = {fmt_float(top15_share, 0)} % игрового времени; "
        f"оставшиеся {n - 15} игр делят {fmt_float(100 - top15_share, 0)} %.",
        source_line,
    )
    fig.subplots_adjust(left=0.235, right=0.97, top=0.88, bottom=0.095)
    fig.savefig(OUT_DIR / "03_top15_igr.png",
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)

    hour_bins = [
        (0, 0, "0"), (0, 1, "0–1"), (1, 2, "1–2"), (2, 5, "2–5"),
        (5, 10, "5–10"), (10, 25, "10–25"), (25, 50, "25–50"),
        (50, 100, "50–100"), (100, np.inf, "100+"),
    ]
    bin_counts = []
    bin_labels = []
    for lo, hi, lab in hour_bins:
        if hi == 0:
            cnt = int((hours == 0).sum())
        elif np.isinf(hi):
            cnt = int((hours >= lo).sum())
        else:
            cnt = int(((hours >= lo) & (hours < hi)).sum())
        bin_counts.append(cnt)
        bin_labels.append(lab)

    fig, ax = plt.subplots(figsize=(11.8, 6.6), dpi=DPI)
    ax.axvspan(-0.5, 4.5, color="#eef4f8", zorder=0)
    hist_colors = [BAR_COLORS[0], BAR_COLORS[0], BAR_COLORS[1], BAR_COLORS[1],
                   BAR_COLORS[2], BAR_COLORS[2], BAR_COLORS[3],
                   COL_ORANGE, COL_ORANGE]
    ax.bar(range(len(hour_bins)), bin_counts, color=hist_colors,
           width=0.76, zorder=3)
    for i, c in enumerate(bin_counts):
        ax.text(i, c + 1.8, str(c), ha="center", fontsize=11,
                fontweight="bold")

    ax.set_xticks(range(len(hour_bins)))
    ax.set_xticklabels(bin_labels, fontsize=10.5)
    ax.set_xlabel("Накопленное время в игре, часов", fontsize=11.5, labelpad=6)
    ax.set_ylabel("Количество игр", fontsize=11.5)
    ax.set_ylim(0, max(bin_counts) * 1.32)
    ax.set_xlim(-0.6, len(hour_bins) - 0.4)
    prepare_axes(ax, "y")

    ax.annotate(
        f"меньше 10 часов — {small_games} {game_word(small_games)} "
        f"({fmt_float(small_share, 0)} % библиотеки)",
        xy=(0.68, 71.8), xytext=(2.0, 90), fontsize=11.5, ha="center",
        color=COL_BLUE_DARK, fontweight="bold",
        arrowprops=dict(arrowstyle="-|>", color=COL_BLUE_DARK,
                        linewidth=1.3, shrinkA=6, shrinkB=3),
    )

    ax.axhline(median_hours, color=COL_BLUE_MID, linewidth=1.4,
               linestyle=(0, (4, 3)), zorder=2)
    ax.text(0.995, 0.965, f"пунктир — медиана: {fmt_float(median_hours, 1)} ч",
            ha="right", va="top", fontsize=9.5, color="#7d99a9",
            transform=ax.transAxes)

    add_header(
        fig,
        "Длинный хвост: почти 70 % игр не дотягивают до 10 часов",
        f"Медиана — {fmt_float(median_hours, 1)} ч, среднее — "
        f"{fmt_float(mean_hours, 1)} ч: типичная картина «библиотеки на будущее», "
        f"где большинство покупок так и не освоено.",
        source_line,
    )
    fig.subplots_adjust(left=0.075, right=0.98, top=0.845, bottom=0.115)
    fig.savefig(OUT_DIR / "04_raspredelenie_chasov.png",
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)

    franchise_keys = {
        "Resident Evil": ["resident evil"],
        "Outlast": ["outlast"],
        "The Jackbox Party Pack": ["jackbox"],
        "Life is Strange": ["life is strange"],
        "Mortal Kombat": ["mortal kombat"],
        "Slime Rancher": ["slime rancher"],
        "Hunt: Showdown": ["hunt: showdown"],
        "Alan Wake": ["alan wake"],
        "Metro 2033": ["metro 2033"],
        "Fireboy & Watergirl": ["fireboy & watergirl"],
    }

    franchises = []
    for title, keys in franchise_keys.items():
        chosen = [r for r in rows
                  if any(k in r["name"].lower() for k in keys)]
        if chosen:
            total_h = sum(r["hours"] for r in chosen)
            franchises.append((title, len(chosen), total_h))

    franchises.sort(key=lambda t: t[2])
    franchise_games = sum(f[1] for f in franchises)
    outlast_info = next(f for f in franchises if f[0] == "Outlast")

    fig, ax = plt.subplots(figsize=(11.8, 6.8), dpi=DPI)
    y_positions = np.arange(len(franchises))
    franchise_hours = [f[2] for f in franchises]
    franchise_colors = [COL_ORANGE if v == max(franchise_hours) else COL_BLUE
                        for v in franchise_hours]

    ax.barh(y_positions, franchise_hours, color=franchise_colors,
            height=0.7, zorder=3)
    max_fh = max(franchise_hours)
    for y, (title, cnt, hrs) in zip(y_positions, franchises):
        ax.text(hrs + max_fh * 0.016, y,
                f"{fmt_float(hrs, 0)} ч  ·  {cnt} {game_word(cnt)}  ·  "
                f"{fmt_float(hrs / cnt, 1)} ч/игра",
                va="center", fontsize=10.2, color=COL_BLUE_DARK)

    ax.set_yticks(y_positions)
    ax.set_yticklabels([f[0] for f in franchises], fontsize=10.5)
    ax.set_xlabel("Суммарное время в играх серии, часов", fontsize=11.5)
    ax.set_xlim(0, max_fh * 1.30)
    ax.set_ylim(-0.7, len(franchises) - 0.25)
    prepare_axes(ax, "x")
    ax.tick_params(axis="y", length=0)

    add_header(
        fig,
        f"Игрок держится за свои серии: 3 игры Outlast — это "
        f"{fmt_float(outlast_info[2], 0)} часа",
        f"В среднем {fmt_float(outlast_info[2] / outlast_info[1], 0)} ч на игру "
        f"в серии Outlast против {fmt_float(median_hours, 1)} ч по библиотеке. "
        f"{franchise_games} {game_word(franchise_games)} из {n} — это серии, "
        f"остальные — одиночные покупки.",
        source_line,
    )
    fig.subplots_adjust(left=0.235, right=0.965, top=0.86, bottom=0.105)
    fig.savefig(OUT_DIR / "05_serii_igr.png",
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)

    appid_buckets = [
        (0, 100_000, "до 100 тыс."),
        (100_000, 500_000, "100–500 тыс."),
        (500_000, 1_500_000, "0,5–1,5 млн"),
        (1_500_000, 3_500_000, "1,5–3,5 млн"),
        (3_500_000, 10**10, "3,5 млн и выше"),
    ]
    bucket_names, bucket_counts, bucket_avgs = [], [], []
    for lo, hi, lab in appid_buckets:
        subset = [r["hours"] for r in rows if lo <= r["appid"] < hi]
        if not subset:
            continue
        bucket_names.append(lab)
        bucket_counts.append(len(subset))
        bucket_avgs.append(sum(subset) / len(subset))

    fig, ax = plt.subplots(figsize=(11.6, 6.7), dpi=DPI)
    xs = np.arange(len(bucket_names))
    ax.bar(xs, bucket_counts, color="#dbe6ec", width=0.6, zorder=3,
           edgecolor="#b9c9d3", linewidth=1.0)
    for x_, c in zip(xs, bucket_counts):
        ax.text(x_, c + 1.6, str(c), ha="center", fontsize=11,
                fontweight="bold", color=COL_BLUE_DARK)

    ax.set_ylim(0, max(bucket_counts) * 1.42)
    ax.set_xticks(xs)
    ax.set_xticklabels(bucket_names, fontsize=10.5)
    ax.set_xlabel("Группа игр по AppID: чем больше номер, тем позже игра "
                  "появилась в каталоге Steam", fontsize=10.8, labelpad=8)
    ax.set_ylabel("Количество игр в группе", fontsize=11.5)
    prepare_axes(ax, "y")

    ax2 = ax.twinx()
    ax2.plot(xs, bucket_avgs, color=COL_ORANGE, linewidth=2.6, marker="o",
             markersize=9, markerfacecolor="white", markeredgewidth=2.2,
             zorder=5)
    for x_, v in zip(xs, bucket_avgs):
        ax2.annotate(f"{fmt_float(v, 0)} ч", xy=(x_, v), xytext=(0, 14),
                     textcoords="offset points", ha="center", fontsize=10.5,
                     color=COL_ORANGE, fontweight="bold")

    ax2.set_ylim(0, max(bucket_avgs) * 1.6)
    ax2.set_ylabel("Среднее время на одну игру, часов", fontsize=11.5,
                   color=COL_ORANGE)
    ax2.tick_params(axis="y", colors=COL_ORANGE, length=0)
    ax2.spines["right"].set_visible(True)
    ax2.spines["right"].set_color(COL_ORANGE)
    ax2.spines["top"].set_visible(False)

    legend_handles = [
        Patch(facecolor="#dbe6ec", edgecolor="#b9c9d3",
              label="Сколько игр в группе"),
        Line2D([0], [0], color=COL_ORANGE, linewidth=2.6, marker="o",
               markerfacecolor="white", markeredgewidth=2.2,
               label="Среднее время на одну игру"),
    ]
    ax.legend(handles=legend_handles, loc="upper left", frameon=False,
              fontsize=10.3)

    add_header(
        fig,
        "Библиотека растёт быстрее, чем находится время на игры",
        f"Самые старые {bucket_counts[0]} игр наиграны в среднем на "
        f"{fmt_float(bucket_avgs[0], 0)} ч, а {bucket_counts[-1]} самых новых — "
        f"в среднем {fmt_float(bucket_avgs[-1], 1)} ч. Новые покупки оседают "
        f"в бэклоге.",
        source_line,
    )
    fig.subplots_adjust(left=0.085, right=0.90, top=0.845, bottom=0.155)
    fig.savefig(OUT_DIR / "06_pokoleniya_biblioteki.png",
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)

    print(f"Всего игр: {n}, суммарно часов: {fmt_thousands(total_hours)}")
    print(f"Медиана: {fmt_float(median_hours)} ч, среднее: {fmt_float(mean_hours)} ч")
    print(f"Ни разу не запускали: {groups[0][1]} "
          f"({fmt_float(groups[0][1] / n * 100)} %)")
    print(f"Меньше 10 часов: {small_games} ({fmt_float(small_share)} %)")
    print(f"50 % времени дают {idx_50} игр, 80 % — {idx_80} игр")
    print(f"Топ-15 = {fmt_float(top15_share)} % времени, "
          f"топ-2 = {fmt_float(top2_share)} %")
    print("Графики сохранены в:", OUT_DIR)

if __name__ == "__main__":
    main()