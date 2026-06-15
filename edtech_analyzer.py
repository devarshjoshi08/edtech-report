#!/usr/bin/env python3
"""
EdTech Weekly Report Generator
Generates HTML reports with charts and insights from educational usage data.
Usage: python3 edtech_analyzer.py [--current FILE] [--previous FILE] [--output DIR]
"""

import argparse
import base64
import io
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Force UTF-8 output so emoji in print() work on Windows terminals (cp1252 default)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# ─── Color Palette ───────────────────────────────────────────────────────────
COLORS = {
    "primary":   "#1a3a5c",
    "secondary": "#2e86ab",
    "accent":    "#f18f01",
    "success":   "#27ae60",
    "warning":   "#f39c12",
    "danger":    "#e74c3c",
    "light":     "#f0f4f8",
    "muted":     "#7f8c8d",
    "lang":      "#3498db",
    "math":      "#9b59b6",
    "english":   "#e67e22",
    "ct":        "#1abc9c",
}

plt.rcParams.update({
    "figure.facecolor": "none",
    "axes.facecolor":   "#f8fafc",
    "axes.edgecolor":   "#dde3ea",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "font.family":      "DejaVu Sans",
    "font.size":        10,
    "axes.titlesize":   12,
    "axes.titleweight": "bold",
    "axes.titlecolor":  COLORS["primary"],
    "axes.labelcolor":  COLORS["primary"],
    "xtick.color":      COLORS["muted"],
    "ytick.color":      COLORS["muted"],
    "grid.color":       "#dde3ea",
    "grid.linestyle":   "--",
    "grid.alpha":       0.6,
})


def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="jpeg", dpi=150, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def generate_demo_data(curr_path, prev_path=None):
    """Generates realistic demo Excel files for testing without real data."""
    import pandas as pd
    import numpy as np
    
    np.random.seed(42)
    districts = ["North District", "South District", "East District", "West District"]
    schools_per_district = 4
    students_per_school = 60
    
    data = []
    student_id = 1000
    for d in districts:
        for s in range(schools_per_district):
            school_name = f"{d} - School {s+1}"
            for i in range(students_per_school):
                student_id += 1
                cls = np.random.choice([3, 4, 5, 6, 7, 8])
                engagement = np.random.choice(["high", "medium", "low", "zero"], p=[0.2, 0.4, 0.3, 0.1])
                
                if engagement == "zero":
                    total_usage = np.random.randint(0, 50)
                    lang_w = eng_w = math_w = ct_w = 0
                elif engagement == "low":
                    total_usage = np.random.randint(50, 500)
                    lang_w = np.random.randint(0, 20)
                    eng_w = np.random.randint(0, 15)
                    math_w = np.random.randint(0, 20)
                    ct_w = np.random.randint(0, 5)
                elif engagement == "medium":
                    total_usage = np.random.randint(500, 2000)
                    lang_w = np.random.randint(10, 50)
                    eng_w = np.random.randint(10, 40)
                    math_w = np.random.randint(10, 50)
                    ct_w = np.random.randint(0, 20)
                else:
                    total_usage = np.random.randint(2000, 8000)
                    lang_w = np.random.randint(30, 90)
                    eng_w = np.random.randint(30, 80)
                    math_w = np.random.randint(30, 90)
                    ct_w = np.random.randint(10, 40)
                    
                weekly_usage = lang_w + eng_w + math_w + ct_w
                total_usage += weekly_usage
                
                lang_lvl = round(np.random.uniform(1.0, 5.5), 1) if total_usage > 100 else 0
                math_lvl = round(np.random.uniform(1.0, 5.5), 1) if total_usage > 100 else 0
                eng_lvl = round(np.random.uniform(1.0, 5.5), 1) if total_usage > 100 else 0
                
                data.append({
                    "username": f"student_{student_id}",
                    "district": d,
                    "s.name": school_name,
                    "Project Name": "Demo Project 2026",
                    "class": cls,
                    "Language": total_usage * 0.3,
                    "english": total_usage * 0.25,
                    "Math": total_usage * 0.35,
                    "FLN": total_usage * 0.05,
                    "CT": total_usage * 0.05,
                    "Total Usage": total_usage,
                    "Language_weekly": lang_w,
                    "English_weekly": eng_w,
                    "Math_weekly": math_w,
                    "CT_Weekly": ct_w,
                    "Weekly Usage": weekly_usage,
                    "Lang PreciseLevel": lang_lvl,
                    "English PreciseLevel": eng_lvl,
                    "Math Precise Level": math_lvl,
                })
                
    curr_df = pd.DataFrame(data)
    curr_df.to_excel(curr_path, index=False)
    
    if prev_path:
        prev_data = []
        for row in data:
            prev_row = row.copy()
            factor = np.random.uniform(0.7, 1.3)
            for c in ["Language_weekly", "English_weekly", "Math_weekly", "CT_Weekly"]:
                prev_row[c] = int(row[c] * factor)
            prev_row["Weekly Usage"] = prev_row["Language_weekly"] + prev_row["English_weekly"] + prev_row["Math_weekly"] + prev_row["CT_Weekly"]
            prev_row["Total Usage"] -= row["Weekly Usage"]
            prev_row["Total Usage"] = max(0, prev_row["Total Usage"])
            
            prev_row["Lang PreciseLevel"] = max(0, row["Lang PreciseLevel"] - np.random.uniform(0, 0.2))
            prev_row["English PreciseLevel"] = max(0, row["English PreciseLevel"] - np.random.uniform(0, 0.2))
            prev_row["Math Precise Level"] = max(0, row["Math Precise Level"] - np.random.uniform(0, 0.2))
            prev_data.append(prev_row)
            
        prev_df = pd.DataFrame(prev_data)
        prev_df.to_excel(prev_path, index=False)
        
    return curr_path, prev_path


def load_data(path):
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    # Normalize numeric cols
    num_cols = ["Language", "english", "Math", "FLN", "CT",
                "Total Usage", "Language_weekly", "English_weekly",
                "Math_weekly", "CT_Weekly", "Weekly Usage",
                "Lang PreciseLevel", "English PreciseLevel", "Math Precise Level"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df


def filter_common_students(curr_df, prev_df):
    """Restrict both weeks to students present in BOTH files (matched on 'username').

    In comparison mode the two files can have different rosters (new joiners,
    dropouts, re-uploads, etc.), which skews WoW deltas because the "current"
    and "previous" KPIs would be computed over different populations. Limiting
    both dataframes to the intersection of usernames keeps the comparison
    apples-to-apples.
    """
    if prev_df is None or "username" not in curr_df.columns or "username" not in prev_df.columns:
        return curr_df, prev_df

    common = set(curr_df["username"]) & set(prev_df["username"])
    curr_common = curr_df[curr_df["username"].isin(common)].reset_index(drop=True)
    prev_common = prev_df[prev_df["username"].isin(common)].reset_index(drop=True)

    print(f"   ℹ️  Common students in both weeks: {len(common)} "
          f"(current had {len(curr_df)}, previous had {len(prev_df)} — "
          f"{len(curr_df) - len(curr_common)} / {len(prev_df) - len(prev_common)} dropped)")

    return curr_common, prev_common


# ─── KPI Computation ─────────────────────────────────────────────────────────

def has_english(df):
    """True only if meaningful English usage exists in the data."""
    eng_cols = [c for c in ["English_weekly", "english"] if c in df.columns]
    return any(df[c].sum() > 0 for c in eng_cols)


def compute_kpis(df):
    total = len(df)
    active = (df["Weekly Usage"] > 0).sum()
    kpis = {
        "total_students": total,
        "active_students": int(active),
        "inactive_students": int(total - active),
        "activation_rate": round(active / total * 100, 1) if total else 0,
        "avg_weekly_usage": round(df["Weekly Usage"].mean(), 1),
        "avg_total_usage": round(df["Total Usage"].mean(), 1),
        "districts": df["district"].nunique(),
        "schools": df["s.name"].nunique(),
        "projects": df["Project Name"].nunique(),
    }
    if has_english(df):
        kpis["avg_english_level"] = round(df["English PreciseLevel"].mean(), 2)
    return kpis


def compute_delta(curr_kpis, prev_kpis):
    deltas = {}
    for k, v in curr_kpis.items():
        prev = prev_kpis.get(k, v)
        if isinstance(v, (int, float)) and prev != 0:
            deltas[k] = round(v - prev, 2)
        else:
            deltas[k] = None
    return deltas


# ─── Red Flags ───────────────────────────────────────────────────────────────

def find_red_flags(df, prev_df=None):
    flags = []

    # Completely inactive schools
    school_active = df.groupby("s.name")["Weekly Usage"].mean()
    zero_schools = school_active[school_active == 0].index.tolist()
    if zero_schools:
        flags.append({
            "level": "critical",
            "title": "🚨 Zero Activity Schools",
            "detail": f"{len(zero_schools)} school(s) recorded ZERO weekly usage this week: "
                      + ", ".join(zero_schools[:5])
                      + (f" (+{len(zero_schools)-5} more)" if len(zero_schools) > 5 else ""),
        })

    # High inactive student ratio
    inactive_pct = (df["Weekly Usage"] == 0).mean() * 100
    if inactive_pct > 40:
        flags.append({
            "level": "critical" if inactive_pct > 60 else "warning",
            "title": "⚠️ High Inactivity Rate",
            "detail": f"{inactive_pct:.1f}% of students had ZERO weekly usage. "
                      f"Target should be below 30%.",
        })

    # Students with very low proficiency
    low_lang = (df["Lang PreciseLevel"] < 3).sum()
    low_math = (df["Math Precise Level"] < 3).sum()
    if low_lang > 0:
        flags.append({
            "level": "warning",
            "title": "📉 Below Basic Language Proficiency",
            "detail": f"{low_lang} students ({low_lang/len(df)*100:.1f}%) are below Level 3 in Language. Needs targeted intervention.",
        })
    if low_math > 0:
        flags.append({
            "level": "warning",
            "title": "📉 Below Basic Math Proficiency",
            "detail": f"{low_math} students ({low_math/len(df)*100:.1f}%) are below Level 3 in Math. Needs targeted intervention.",
        })

    # Students with zero English usage but not zero total (only if school has English)
    if has_english(df):
        no_eng = ((df["english"] == 0) & (df["Total Usage"] > 1000)).sum()
        if no_eng > 50:
            flags.append({
                "level": "info",
                "title": "ℹ️ No English Engagement",
                "detail": f"{no_eng} active students have zero English usage. Consider promoting English content.",
            })

    # WoW drops (if prev data)
    if prev_df is not None:
        curr_avg = df["Weekly Usage"].mean()
        prev_avg = prev_df["Weekly Usage"].mean()
        drop_pct = (prev_avg - curr_avg) / prev_avg * 100 if prev_avg else 0
        if drop_pct > 10:
            flags.append({
                "level": "critical",
                "title": "📉 Week-on-Week Drop in Engagement",
                "detail": f"Average weekly usage dropped by {drop_pct:.1f}% vs last week "
                          f"({prev_avg:.1f} → {curr_avg:.1f} mins). Immediate follow-up required.",
            })

        curr_active_rate = (df["Weekly Usage"] > 0).mean() * 100
        prev_active_rate = (prev_df["Weekly Usage"] > 0).mean() * 100
        active_drop = prev_active_rate - curr_active_rate
        if active_drop > 5:
            flags.append({
                "level": "warning",
                "title": "👥 Activation Rate Decline",
                "detail": f"Active student % fell from {prev_active_rate:.1f}% to {curr_active_rate:.1f}% "
                          f"({active_drop:.1f}pp decline).",
            })

    return flags


# ─── Chart Generators ────────────────────────────────────────────────────────

def chart_district_usage(df):
    data = df.groupby("district")["Weekly Usage"].mean().sort_values(ascending=True)
    act  = df.groupby("district").apply(
        lambda x: (x["Weekly Usage"] > 0).mean() * 100, include_groups=False
    ).reindex(data.index)

    n      = len(data)
    fig_h  = max(5, n * 0.42)
    bar_h  = max(0.3, min(0.6, 0.6 - (n - 10) * 0.01))
    cmap   = plt.colormaps["tab20"]
    colors = [cmap(i % 20) for i in range(n)]

    fig, axes = plt.subplots(1, 2, figsize=(13, fig_h))

    bars = axes[0].barh(data.index, data.values, color=colors,
                        height=bar_h, edgecolor="none")
    axes[0].bar_label(bars, fmt="%.1f min", padding=4,
                      color=COLORS["primary"], fontsize=8)
    axes[0].set_title("Avg Weekly Usage by District")
    axes[0].set_xlabel("Minutes")
    axes[0].grid(axis="x", alpha=0.4)

    bars2 = axes[1].barh(act.index, act.values, color=colors,
                          height=bar_h, edgecolor="none")
    axes[1].bar_label(bars2, fmt="%.1f%%", padding=4,
                      color=COLORS["primary"], fontsize=8)
    axes[1].set_title("Student Activation Rate by District")
    axes[1].set_xlabel("% Active Students")
    axes[1].set_xlim(0, 115)
    axes[1].grid(axis="x", alpha=0.4)

    fig.tight_layout(pad=2)
    return fig_to_base64(fig)


def chart_subject_breakdown(df):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    subjects = {"Language": COLORS["lang"], "Math": COLORS["math"], "CT": COLORS["ct"]}
    col_map  = {"Language": "Language_weekly", "Math": "Math_weekly", "CT": "CT_Weekly"}
    if has_english(df):
        subjects["English"] = COLORS["english"]
        col_map["English"]  = "English_weekly"
    avgs   = {s: df[col_map[s]].mean() for s in subjects}
    labels = list(avgs.keys())
    vals   = list(avgs.values())
    colors = [subjects[s] for s in labels]

    bars = axes[0].bar(labels, vals, color=colors, edgecolor="none", width=0.55)
    axes[0].bar_label(bars, fmt="%.1f min", padding=4, fontsize=9, color=COLORS["primary"])
    axes[0].set_title("Avg Weekly Engagement by Subject")
    axes[0].set_ylabel("Minutes / Week")
    axes[0].grid(axis="y", alpha=0.4)

    # Pie chart of time share
    non_zero = [(l, v, c) for l, v, c in zip(labels, vals, colors) if v > 0]
    if non_zero:
        pie_labels, pie_vals, pie_colors = zip(*non_zero)
        wedges, texts, autotexts = axes[1].pie(
            pie_vals, labels=pie_labels, colors=pie_colors,
            autopct="%1.1f%%", startangle=140,
            wedgeprops={"edgecolor": "white", "linewidth": 2},
            textprops={"fontsize": 9}
        )
        for at in autotexts:
            at.set_color("white")
            at.set_fontweight("bold")
        axes[1].set_title("Subject Time Share (Weekly)")

    fig.tight_layout(pad=2)
    return fig_to_base64(fig)


def chart_proficiency_distribution(df):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    configs = [
        ("Lang PreciseLevel", "Language Proficiency", COLORS["lang"]),
        ("Math Precise Level", "Math Proficiency", COLORS["math"]),
        ("English PreciseLevel", "English Proficiency", COLORS["english"]),
    ]
    for ax, (col, title, color) in zip(axes, configs):
        data = df[col][df[col] > 0]
        if len(data) > 0:
            bins = np.arange(0, max(data.max() + 1, 6), 0.5)
            ax.hist(data, bins=bins, color=color, alpha=0.85, edgecolor="white", linewidth=0.5)
            ax.axvline(data.mean(), color=COLORS["danger"], linestyle="--", linewidth=1.5,
                       label=f"Avg: {data.mean():.2f}")
            ax.legend(fontsize=8, framealpha=0)
        ax.set_title(title)
        ax.set_xlabel("Proficiency Level")
        ax.set_ylabel("# Students")
        ax.grid(axis="y", alpha=0.4)
    fig.tight_layout(pad=2)
    return fig_to_base64(fig)


def chart_school_comparison(df):
    school_stats = df.groupby("s.name").agg(
        avg_weekly=("Weekly Usage", "mean"),
        students=("username", "count"),
        activation=("Weekly Usage", lambda x: (x > 0).mean() * 100),
        lang_level=("Lang PreciseLevel", "mean"),
        math_level=("Math Precise Level", "mean"),
    ).reset_index().sort_values("avg_weekly", ascending=True)

    top_n = 30
    if len(school_stats) > top_n:
        school_stats = pd.concat([school_stats.head(10), school_stats.tail(20)])

    fig, ax = plt.subplots(figsize=(14, max(6, len(school_stats) * 0.40)))
    bar_colors = [COLORS["danger"] if v < 20 else
                  COLORS["warning"] if v < 50 else
                  COLORS["success"] for v in school_stats["avg_weekly"]]
    bars = ax.barh(school_stats["s.name"], school_stats["avg_weekly"],
                   color=bar_colors, edgecolor="none", height=0.6)
    ax.bar_label(bars, fmt="%.0f min", padding=3, fontsize=8, color=COLORS["primary"])
    ax.set_title("Average Weekly Usage per School\n(Red = Critical, Orange = Needs Attention, Green = Good)")
    ax.set_xlabel("Avg Minutes / Week")
    ax.grid(axis="x", alpha=0.4)

    legend_patches = [
        mpatches.Patch(color=COLORS["danger"], label="< 20 min (Critical)"),
        mpatches.Patch(color=COLORS["warning"], label="20–50 min (Needs Attention)"),
        mpatches.Patch(color=COLORS["success"], label="> 50 min (Good)"),
    ]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=8, framealpha=0.9)
    fig.tight_layout(pad=2)
    return fig_to_base64(fig)


def chart_class_performance(df):
    """Class-wise weekly usage breakdown by subject (no level data)."""
    class_data = df.groupby("class").agg(
        lang_w=("Language_weekly", "mean"),
        math_w=("Math_weekly",     "mean"),
        eng_w=("English_weekly",   "mean"),
        ct_w=("CT_Weekly",         "mean"),
        weekly=("Weekly Usage",    "mean"),
        count=("username",         "count"),
    ).reset_index()

    show_eng = has_english(df)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    x = np.arange(len(class_data))
    w = 0.22
    axes[0].bar(x - w*1.5, class_data["lang_w"], width=w, color=COLORS["lang"],  label="Language")
    axes[0].bar(x - w*0.5, class_data["math_w"], width=w, color=COLORS["math"],  label="Math")
    if show_eng:
        axes[0].bar(x + w*0.5, class_data["eng_w"],  width=w, color=COLORS["english"], label="English")
    axes[0].bar(x + w*(1.5 if show_eng else 0.5),
                class_data["ct_w"], width=w, color=COLORS["ct"], label="CT")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([f"Class {c}" for c in class_data["class"]])
    axes[0].set_title("Avg Weekly Usage by Subject & Class (min)")
    axes[0].set_ylabel("Minutes / Week")
    axes[0].legend(fontsize=8, framealpha=0)
    axes[0].grid(axis="y", alpha=0.4)

    bars = axes[1].bar([f"Class {c}" for c in class_data["class"]], class_data["weekly"],
                       color=COLORS["secondary"], edgecolor="none", width=0.55)
    for bar, n in zip(bars, class_data["count"]):
        axes[1].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.5,
                     f"{bar.get_height():.0f}m\n(n={int(n)})",
                     ha="center", va="bottom", fontsize=8, color=COLORS["primary"])
    axes[1].set_title("Total Avg Weekly Usage by Class (min)")
    axes[1].set_ylabel("Minutes / Week")
    axes[1].grid(axis="y", alpha=0.4)

    fig.tight_layout(pad=2)
    return fig_to_base64(fig)


def chart_top_bottom_schools(df):
    """Top 10 / Bottom 10 schools by avg Total Usage per active student.

    Active student = Total Usage > 0.
    Bottom 10 excludes schools whose avg_total_per_active == 0
    (i.e. schools with zero-usage students only) so every school shown
    has at least some real engagement.
    """
    def _avg_total_per_active(grp):
        active = grp[grp["Total Usage"] > 0]
        if len(active) == 0:
            return 0.0
        return active["Total Usage"].mean()

    school_stats = df.groupby("s.name").apply(
        lambda g: pd.Series({
            "avg_total_per_active": _avg_total_per_active(g),
            "active_students": int((g["Total Usage"] > 0).sum()),
            "total_students": len(g),
        }), include_groups=False
    ).reset_index()
    school_stats["activation"] = (
        school_stats["active_students"] / school_stats["total_students"] * 100
    ).round(1)
    school_stats = school_stats.sort_values("avg_total_per_active")

    top10   = school_stats.tail(10).iloc[::-1]   # highest first
    bottom10 = school_stats[
        school_stats["avg_total_per_active"] > 0
    ].head(10)                                   # lowest with some usage

    fig, axes = plt.subplots(1, 2, figsize=(14, max(5, max(len(top10), len(bottom10)) * 0.5)))

    # ── Bottom 10 ────────────────────────────────────────────────────────────
    axes[0].barh(range(len(bottom10)), bottom10["avg_total_per_active"],
                 color=COLORS["danger"], edgecolor="none", height=0.55)
    axes[0].set_yticks(range(len(bottom10)))
    axes[0].set_yticklabels(bottom10["s.name"], fontsize=8)
    axes[0].set_title(f"Bottom {len(bottom10)} Schools\nAvg Total Usage / Active Student",
                      color=COLORS["danger"])
    axes[0].set_xlabel("Minutes (Total Usage)")
    axes[0].grid(axis="x", alpha=0.4)
    for i, (_, row) in enumerate(bottom10.iterrows()):
        v = row["avg_total_per_active"]
        axes[0].text(v + max(bottom10["avg_total_per_active"]) * 0.01, i,
                     f"{v:,.0f}m  ({row['active_students']}/{row['total_students']} active)",
                     va="center", fontsize=7.5, color=COLORS["primary"])

    # ── Top 10 ───────────────────────────────────────────────────────────────
    axes[1].barh(range(len(top10)), top10["avg_total_per_active"],
                 color=COLORS["success"], edgecolor="none", height=0.55)
    axes[1].set_yticks(range(len(top10)))
    axes[1].set_yticklabels(top10["s.name"], fontsize=8)
    axes[1].set_title(f"Top {len(top10)} Schools\nAvg Total Usage / Active Student",
                      color=COLORS["success"])
    axes[1].set_xlabel("Minutes (Total Usage)")
    axes[1].grid(axis="x", alpha=0.4)
    for i, (_, row) in enumerate(top10.iterrows()):
        v = row["avg_total_per_active"]
        axes[1].text(v + max(top10["avg_total_per_active"]) * 0.01, i,
                     f"{v:,.0f}m  ({row['active_students']}/{row['total_students']} active)",
                     va="center", fontsize=7.5, color=COLORS["primary"])

    fig.tight_layout(pad=2)
    return fig_to_base64(fig)


def _wow_bar(ax, labels, curr_vals, prev_vals, title):
    """Shared helper: draws a grouped WoW bar chart on the given axes."""
    x = np.arange(len(labels))
    w = 0.35
    b1 = ax.bar(x - w/2, prev_vals, w, label="Prev Week",
                color=COLORS["muted"], alpha=0.75, edgecolor="none")
    b2 = ax.bar(x + w/2, curr_vals, w, label="This Week",
                color=[COLORS["success"] if c >= p else COLORS["danger"]
                       for c, p in zip(curr_vals, prev_vals)],
                edgecolor="none")
    ax.bar_label(b1, fmt="%.1f", padding=2, fontsize=7.5, color=COLORS["muted"])
    ax.bar_label(b2, fmt="%.1f", padding=2, fontsize=7.5, color=COLORS["primary"])
    for i, (c, p) in enumerate(zip(curr_vals, prev_vals)):
        delta = c - p
        arrow = "▲" if delta >= 0 else "▼"
        clr   = COLORS["success"] if delta >= 0 else COLORS["danger"]
        top   = max(c, p) + (max(curr_vals) or 1) * 0.05
        ax.text(i, top, f"{arrow}{abs(delta):.1f}",
                ha="center", fontsize=8, color=clr, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15 if len(labels) > 5 else 0,
                       ha="right" if len(labels) > 5 else "center", fontsize=9)
    ax.set_title(title)
    ax.set_ylabel("Avg Minutes / Student")
    ax.legend(fontsize=9, framealpha=0)
    ax.grid(axis="y", alpha=0.4)


def chart_wow_comparison(curr_df, prev_df):
    """State-level Week-on-Week comparison (usage subjects only, no level data)."""
    metrics = {"Weekly Usage": "Weekly Usage",
               "Language":     "Language_weekly",
               "Math":         "Math_weekly",
               "CT":           "CT_Weekly"}
    if has_english(curr_df):
        metrics["English"] = "English_weekly"

    labels    = list(metrics.keys())
    curr_vals = [curr_df[col].mean() for col in metrics.values()]
    prev_vals = [prev_df[col].mean() for col in metrics.values()]

    fig, ax = plt.subplots(figsize=(12, 5))
    _wow_bar(ax, labels, curr_vals, prev_vals,
             "State-level Week-on-Week — Avg Usage per Student (min)")
    fig.tight_layout(pad=2)
    return fig_to_base64(fig)


def chart_project_wow(curr_df, prev_df=None):
    """Project-wise weekly usage — WoW if prev_df given, else current week only."""
    curr_proj = curr_df.groupby("Project Name")["Weekly Usage"].mean().sort_values(ascending=False)

    if prev_df is not None:
        prev_proj  = prev_df.groupby("Project Name")["Weekly Usage"].mean()
        all_proj   = curr_proj.index.union(prev_proj.index)
        curr_vals  = [curr_proj.get(p, 0) for p in all_proj]
        prev_vals  = [prev_proj.get(p, 0) for p in all_proj]
        labels     = list(all_proj)

        n       = len(labels)
        fig_h   = max(5, n * 0.55)
        fig, ax = plt.subplots(figsize=(13, fig_h))
        y  = np.arange(n)
        w  = 0.38
        b1 = ax.barh(y - w/2, prev_vals, w, label="Prev Week",
                     color=COLORS["muted"], alpha=0.75, edgecolor="none")
        b2 = ax.barh(y + w/2, curr_vals, w, label="This Week",
                     color=[COLORS["success"] if c >= p else COLORS["danger"]
                            for c, p in zip(curr_vals, prev_vals)],
                     edgecolor="none")
        for i, (c, p) in enumerate(zip(curr_vals, prev_vals)):
            delta = c - p
            arrow = "▲" if delta >= 0 else "▼"
            clr   = COLORS["success"] if delta >= 0 else COLORS["danger"]
            ax.text(max(c, p) + (max(curr_vals) or 1) * 0.01, i,
                    f"  {arrow}{abs(delta):.1f}",
                    va="center", fontsize=8, color=clr, fontweight="bold")
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel("Avg Minutes / Student")
        ax.set_title("Project-wise Week-on-Week — Avg Weekly Usage (min)")
        ax.legend(fontsize=9, framealpha=0)
        ax.grid(axis="x", alpha=0.4)

    else:
        n       = len(curr_proj)
        fig_h   = max(4, n * 0.5)
        fig, ax = plt.subplots(figsize=(12, fig_h))
        cmap    = plt.colormaps["tab20"]
        colors  = [cmap(i % 20) for i in range(n)]
        bars    = ax.barh(curr_proj.index, curr_proj.values,
                          color=colors, edgecolor="none", height=0.55)
        ax.bar_label(bars, fmt="%.1f min", padding=4, fontsize=9,
                     color=COLORS["primary"])
        ax.set_xlabel("Avg Minutes / Student")
        ax.set_title("Project-wise Avg Weekly Usage (min)")
        ax.grid(axis="x", alpha=0.4)

    fig.tight_layout(pad=2)
    return fig_to_base64(fig)


def chart_district_wow(curr_df, prev_df):
    """District-wise WoW — avg weekly usage comparison."""
    curr_d = curr_df.groupby("district")["Weekly Usage"].mean().sort_values(ascending=False)
    prev_d = prev_df.groupby("district")["Weekly Usage"].mean()
    all_d  = curr_d.index.union(prev_d.index)
    curr_v = [curr_d.get(d, 0) for d in all_d]
    prev_v = [prev_d.get(d, 0) for d in all_d]
    labels = list(all_d)

    n      = len(labels)
    fig_h  = max(5, n * 0.48)
    fig, ax = plt.subplots(figsize=(13, fig_h))
    y  = np.arange(n)
    w  = 0.38
    ax.barh(y - w/2, prev_v, w, label="Prev Week",
            color=COLORS["muted"], alpha=0.75, edgecolor="none")
    ax.barh(y + w/2, curr_v, w, label="This Week",
            color=[COLORS["success"] if c >= p else COLORS["danger"]
                   for c, p in zip(curr_v, prev_v)],
            edgecolor="none")
    for i, (c, p) in enumerate(zip(curr_v, prev_v)):
        delta = c - p
        arrow = "▲" if delta >= 0 else "▼"
        clr   = COLORS["success"] if delta >= 0 else COLORS["danger"]
        ax.text(max(c, p) + (max(curr_v) or 1) * 0.01, i,
                f"  {arrow}{abs(delta):.1f}",
                va="center", fontsize=8, color=clr, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Avg Minutes / Student")
    ax.set_title("District-wise Week-on-Week — Avg Weekly Usage (min)")
    ax.legend(fontsize=9, framealpha=0)
    ax.grid(axis="x", alpha=0.4)
    fig.tight_layout(pad=2)
    return fig_to_base64(fig)


def chart_activity_heatmap_proxy(df):
    """School × Subject heatmap — capped at top 50 schools for readability."""
    school_subject = df.groupby("s.name").agg(
        Language=("Language_weekly", "mean"),
        Math=("Math_weekly", "mean"),
        English=("English_weekly", "mean"),
        CT=("CT_Weekly", "mean"),
    ).fillna(0)

    MAX_SCHOOLS = 50
    note = ""
    if len(school_subject) > MAX_SCHOOLS:
        top_idx = school_subject.sum(axis=1).nlargest(MAX_SCHOOLS).index
        school_subject = school_subject.loc[top_idx]
        note = f" — Top {MAX_SCHOOLS} by Total Engagement"

    n_schools = len(school_subject)
    fig_h = max(6, n_schools * 0.32)
    fig, ax = plt.subplots(figsize=(10, fig_h))
    data = school_subject.values
    im = ax.imshow(data, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(school_subject.columns)))
    ax.set_xticklabels(school_subject.columns, fontsize=10)
    ax.set_yticks(range(n_schools))
    lbl_size = max(5, min(8, int(180 / n_schools)))
    ax.set_yticklabels(school_subject.index, fontsize=lbl_size)
    plt.colorbar(im, ax=ax, label="Avg Minutes / Week", shrink=0.6)

    if n_schools <= 60:
        threshold = data.max() * 0.6
        for i in range(n_schools):
            for j in range(len(school_subject.columns)):
                val = data[i, j]
                ax.text(j, i, f"{val:.0f}", ha="center", va="center",
                        fontsize=max(5, lbl_size - 1),
                        color="white" if val > threshold else COLORS["primary"])

    ax.set_title(f"Subject Engagement Heatmap by School (Avg min/week){note}")
    fig.tight_layout()
    return fig_to_base64(fig)


# ─── Mail Body Generator ──────────────────────────────────────────────────────

def generate_mail_body(kpis, deltas, flags, df, report_date):
    active = kpis["active_students"]
    total = kpis["total_students"]
    rate = kpis["activation_rate"]

    def delta_str(key):
        if deltas and deltas.get(key) is not None:
            d = deltas[key]
            sign = "+" if d >= 0 else ""
            arrow = "↑" if d > 0 else ("↓" if d < 0 else "→")
            return f" ({arrow} {sign}{d} WoW)"
        return ""

    school_stats = df.groupby("s.name").agg(
        weekly=("Weekly Usage", "mean"),
        activation=("Weekly Usage", lambda x: (x > 0).mean() * 100)
    ).reset_index()
    top3 = school_stats.nlargest(3, "weekly")
    bottom3 = school_stats.nsmallest(3, "weekly")

    flag_lines = ""
    if flags:
        flag_lines = "\n🔴 KEY ALERTS:\n"
        for f in flags:
            flag_lines += f"• {f['title']}: {f['detail']}\n"

    top_schools = "\n".join(
        f"  {i+1}. {r['s.name']}: {r['weekly']:.0f} min/week ({r['activation']:.0f}% active)"
        for i, (_, r) in enumerate(top3.iterrows())
    )
    bottom_schools = "\n".join(
        f"  {i+1}. {r['s.name']}: {r['weekly']:.0f} min/week ({r['activation']:.0f}% active)"
        for i, (_, r) in enumerate(bottom3.iterrows())
    )

    mail = f"""Subject: 📊 Weekly EdTech Usage Report – {report_date}

Hi Team,

Please find below the weekly EdTech usage summary for the week ending {report_date}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 WEEKLY SNAPSHOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Students Enrolled   : {total}
• Active Students This Week : {active}{delta_str('active_students')} ({rate}% activation rate)
• Inactive Students         : {kpis['inactive_students']} ({100-rate:.1f}%)

• Avg Weekly Usage          : {kpis['avg_weekly_usage']} min{delta_str('avg_weekly_usage')}
• Avg Total Usage (cumul.)  : {kpis['avg_total_usage']} min

• Districts Covered         : {kpis['districts']}
• Schools Covered           : {kpis['schools']}
{flag_lines}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 PROFICIENCY LEVELS (Avg)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Avg Weekly Usage : {kpis['avg_weekly_usage']} min{delta_str('avg_weekly_usage')}
• Avg Total Usage  : {kpis['avg_total_usage']} min{delta_str('avg_total_usage')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 TOP PERFORMING SCHOOLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{top_schools}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ SCHOOLS NEEDING IMMEDIATE ATTENTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{bottom_schools}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📎 Full interactive report with charts is attached.

Please ensure field team follows up with schools showing zero or very low activity.

Regards,
EdTech Analytics Team"""

    return mail


# ─── HTML Report Builder ─────────────────────────────────────────────────────

def kpi_card(label, value, delta=None, unit="", suffix="", is_bad=False):
    delta_html = ""
    if delta is not None:
        color = COLORS["success"] if delta >= 0 else COLORS["danger"]
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "→")
        sign = "+" if delta > 0 else ""
        delta_html = f'<span style="color:{color};font-size:12px;display:block;margin-top:4px">{arrow} {sign}{delta} WoW</span>'

    bg = "#fff5f5" if is_bad else "white"
    border = f"3px solid {COLORS['danger']}" if is_bad else f"1px solid #e8ecf0"

    return f"""
    <div style="background:{bg};border:{border};border-radius:10px;padding:18px 16px;
                text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
        <div style="font-size:11px;color:{COLORS['muted']};text-transform:uppercase;
                    letter-spacing:0.08em;font-weight:600;margin-bottom:8px">{label}</div>
        <div style="font-size:28px;font-weight:700;color:{COLORS['primary']}">
            {unit}{value}{suffix}
        </div>
        {delta_html}
    </div>"""


def flag_html(flags):
    if not flags:
        return '<div style="color:#27ae60;padding:12px;font-weight:600">✅ No critical red flags this week!</div>'
    colors = {"critical": ("#ffe8e8", COLORS["danger"]), "warning": ("#fff8e8", COLORS["warning"]),
              "info": ("#e8f4fd", COLORS["secondary"])}
    html = ""
    for f in flags:
        bg, border = colors.get(f["level"], ("#f5f5f5", COLORS["muted"]))
        html += f"""
        <div style="background:{bg};border-left:4px solid {border};border-radius:4px;
                    padding:12px 16px;margin-bottom:8px;">
            <strong style="color:{border}">{f['title']}</strong>
            <div style="margin-top:4px;font-size:13px;color:{COLORS['primary']}">{f['detail']}</div>
        </div>"""
    return html


def school_table_html(df):
    school_stats = df.groupby("s.name").agg(
        students=("username", "count"),
        avg_weekly=("Weekly Usage", "mean"),
        activation=("Weekly Usage", lambda x: (x > 0).mean() * 100),
        lang_level=("Lang PreciseLevel", "mean"),
        math_level=("Math Precise Level", "mean"),
        district=("district", "first"),
    ).reset_index().sort_values("avg_weekly", ascending=False)

    rows = ""
    for _, r in school_stats.iterrows():
        status_color = (COLORS["danger"] if r["avg_weekly"] < 20 else
                        COLORS["warning"] if r["avg_weekly"] < 50 else COLORS["success"])
        badge = ("🔴" if r["avg_weekly"] < 20 else "🟡" if r["avg_weekly"] < 50 else "🟢")
        rows += f"""<tr style="border-bottom:1px solid #f0f0f0">
            <td style="padding:9px 12px">{badge} {r['s.name']}</td>
            <td style="padding:9px 12px">{r['district']}</td>
            <td style="padding:9px 12px;text-align:center">{int(r['students'])}</td>
            <td style="padding:9px 12px;text-align:center;color:{status_color};font-weight:600">
                {r['avg_weekly']:.1f}</td>
            <td style="padding:9px 12px;text-align:center">{r['activation']:.1f}%</td>
            <td style="padding:9px 12px;text-align:center">{r['lang_level']:.2f}</td>
            <td style="padding:9px 12px;text-align:center">{r['math_level']:.2f}</td>
        </tr>"""

    return f"""
    <table style="width:100%;border-collapse:collapse;font-size:13px">
        <thead>
            <tr style="background:{COLORS['primary']};color:white">
                <th style="padding:10px 12px;text-align:left">School</th>
                <th style="padding:10px 12px;text-align:left">District</th>
                <th style="padding:10px 12px;text-align:center">Students</th>
                <th style="padding:10px 12px;text-align:center">Avg Weekly (min)</th>
                <th style="padding:10px 12px;text-align:center">Activation</th>
                <th style="padding:10px 12px;text-align:center">Lang Level</th>
                <th style="padding:10px 12px;text-align:center">Math Level</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>"""


def build_html_report(curr_df, prev_df, report_date, output_path):
    kpis = compute_kpis(curr_df)
    prev_kpis = compute_kpis(prev_df) if prev_df is not None else None
    deltas = compute_delta(kpis, prev_kpis) if prev_kpis else None
    flags = find_red_flags(curr_df, prev_df)

    print("  Generating charts...")
    _has_eng   = has_english(curr_df)
    _has_prev  = prev_df is not None
    chart1     = chart_district_usage(curr_df)
    chart2     = chart_subject_breakdown(curr_df)
    chart5     = chart_class_performance(curr_df)
    chart6     = chart_top_bottom_schools(curr_df)
    chart_proj = chart_project_wow(curr_df, prev_df)
    chart_state_wow  = chart_wow_comparison(curr_df, prev_df) if _has_prev else None
    chart_dist_wow   = chart_district_wow(curr_df, prev_df)   if _has_prev else None

    def d(key):
        return deltas.get(key) if deltas else None

    def wrap_chart_html(chart_base64, filename="chart.jpg"):
        if not chart_base64: return ""
        name = filename.replace(".jpg", "").replace(".png", "")
        return f'<img src="data:image/jpeg;base64,{chart_base64}" style="width:100%;border-radius:8px" id="img_{name}">'

    state_wow_section = ""
    if chart_state_wow:
        state_wow_section = f"""
  <div class="section full">
    <div class="section-hdr">
      <h2>📊 State-level Week-on-Week Comparison</h2>
      <button class="dl-btn" onclick="dlSection(this,'State_WoW')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart_state_wow, 'state_wow.jpg')}
  </div>"""

    dist_wow_section = ""
    if chart_dist_wow:
        dist_wow_section = f"""
  <div class="section full">
    <div class="section-hdr">
      <h2>🗺️ District-wise Week-on-Week</h2>
      <button class="dl-btn" onclick="dlSection(this,'District_WoW')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart_dist_wow, 'district_wow.jpg')}
  </div>"""

    inactive_schools = curr_df.groupby("s.name")["Weekly Usage"].mean()
    inactive_list = inactive_schools[inactive_schools == 0].index.tolist()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EdTech Weekly Report – {report_date}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #f0f4f8;
    color: {COLORS["primary"]};
    line-height: 1.6;
  }}
  .header {{
    background: linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["secondary"]} 100%);
    color: white;
    padding: 28px 48px;
  }}
  .header h1 {{ font-size: 24px; font-weight: 700; }}
  .header p  {{ opacity: 0.85; margin-top: 4px; font-size: 13px; }}
  .container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
  }}
  .section {{
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  }}
  .full {{ grid-column: 1 / -1; }}
  h2 {{
    font-size: 15px;
    font-weight: 700;
    color: {COLORS["primary"]};
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid #f0f4f8;
  }}
  .section-hdr {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid #f0f4f8;
  }}
  .section-hdr h2 {{
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
  }}
  .dl-btn {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    background: {COLORS["secondary"]};
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 11px;
    font-weight: 600;
    font-family: 'Segoe UI', sans-serif;
    opacity: 0.85;
    transition: opacity 0.15s;
    white-space: nowrap;
  }}
  .dl-btn:hover {{ opacity: 1; background: {COLORS["primary"]}; }}
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 10px;
  }}
  .chart-container {{ border-radius: 8px; }}
  .download-btn {{
    display: none;
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(26, 58, 92, 0.85);
    color: white;
    padding: 6px 12px;
    border-radius: 4px;
    text-decoration: none;
    font-size: 12px;
    font-weight: bold;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }}
  .download-btn:hover {{ background: #1a3a5c; }}
  @media print {{
    body {{ background: white; }}
    .section {{ box-shadow: none; border: 1px solid #e0e7ef; page-break-inside: avoid; }}
    .dl-btn {{ display: none !important; }}
  }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
function dlSection(btn, name) {{
  var section = btn.closest('.section');
  var img = section.querySelector('img');
  var titleEl = section.querySelector('h2');
  btn.style.visibility = 'hidden';

  function triggerDownload(blob) {{
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = (name || 'section') + '.jpg';
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
    btn.style.visibility = 'visible';
  }}

  if (img) {{
    // Chart section: composite title + chart at native image resolution
    var titleText = (titleEl ? titleEl.innerText : name).replace(/[^\\x00-\\x7E]/g, '').trim();
    var tmpImg = new Image();
    tmpImg.onload = function() {{
      var pad = 20, titleH = 50;
      var cvs = document.createElement('canvas');
      cvs.width  = tmpImg.naturalWidth;
      cvs.height = tmpImg.naturalHeight + titleH + pad;
      var ctx = cvs.getContext('2d');
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, cvs.width, cvs.height);
      ctx.fillStyle = '#1a3a5c';
      ctx.font = 'bold 28px Segoe UI, Arial, sans-serif';
      ctx.fillText(titleText, pad, pad + 28);
      ctx.drawImage(tmpImg, 0, titleH + pad);
      cvs.toBlob(triggerDownload, 'image/jpeg', 0.93);
    }};
    tmpImg.src = img.src;
  }} else {{
    // KPI / Red Flags / text sections: use html2canvas
    var origBg = section.style.background;
    section.style.background = '#ffffff';
    html2canvas(section, {{
      scale: 2, backgroundColor: '#ffffff', useCORS: true, logging: false
    }}).then(function(canvas) {{
      section.style.background = origBg;
      canvas.toBlob(triggerDownload, 'image/jpeg', 0.93);
    }});
  }}
}}
</script>
</head>
<body>

<div class="header">
  <h1>📊 EdTech Weekly Analytics Report</h1>
  <p>Report Date: <strong>{report_date}</strong> &nbsp;|&nbsp;
     Data: <strong>{len(curr_df):,} students</strong> across
     <strong>{curr_df["s.name"].nunique()} schools</strong> &amp;
     <strong>{curr_df["district"].nunique()} districts</strong>
     {' &nbsp;|&nbsp; ▸ WoW comparison enabled' if prev_df is not None else ''}
  </p>
</div>

<div class="container">

  <!-- KPIs – full width -->
  <div class="section full">
    <div class="section-hdr">
      <h2>🎯 Key Performance Indicators</h2>
      <button class="dl-btn" onclick="dlSection(this,'KPI_Summary')">⬇ Save as JPG</button>
    </div>
    <div class="kpi-grid">
      {kpi_card("Total Students",    kpis["total_students"])}
      {kpi_card("Active Students",   kpis["active_students"],   d("active_students"))}
      {kpi_card("Activation Rate",   kpis["activation_rate"],   d("activation_rate"),   suffix="%",
                is_bad=kpis["activation_rate"] < 50)}
      {kpi_card("Inactive Students", kpis["inactive_students"],
                -d("inactive_students") if d("inactive_students") else None,
                is_bad=kpis["inactive_students"] > kpis["total_students"] * 0.4)}
      {kpi_card("Avg Weekly Usage",  kpis["avg_weekly_usage"],  d("avg_weekly_usage"),  suffix=" min")}
      {kpi_card("Avg Total Usage",   kpis["avg_total_usage"],   d("avg_total_usage"),   suffix=" min")}
      {kpi_card("Schools",           kpis["schools"])}
      {kpi_card("Districts",         kpis["districts"])}
      {kpi_card("Projects",          kpis["projects"])}
    </div>
  </div>

  <!-- Red Flags – full width -->
  <div class="section full">
    <div class="section-hdr">
      <h2>🚨 Red Flags &amp; Alerts</h2>
      <button class="dl-btn" onclick="dlSection(this,'Red_Flags')">⬇ Save as JPG</button>
    </div>
    {flag_html(flags)}
    {f'<div style="margin-top:10px;padding:8px 14px;background:#fff3f3;border-radius:6px;font-size:12px"><strong>Schools with ZERO activity:</strong> {", ".join(inactive_list[:10]) + (" …+" + str(len(inactive_list)-10) + " more" if len(inactive_list) > 10 else "")}</div>' if inactive_list else ""}
  </div>

  {state_wow_section}

  <!-- Project-wise WoW – full width -->
  <div class="section full">
    <div class="section-hdr">
      <h2>📁 Project-wise {'Week-on-Week' if _has_prev else 'Weekly Usage'}</h2>
      <button class="dl-btn" onclick="dlSection(this,'Project_WoW')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart_proj, 'project_wow.jpg')}
  </div>

  {dist_wow_section}

  <!-- District current-week + Subject side by side -->
  <div class="section">
    <div class="section-hdr">
      <h2>🗺️ District-level Engagement (This Week)</h2>
      <button class="dl-btn" onclick="dlSection(this,'District_Engagement')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart1, 'district_engagement.jpg')}
  </div>

  <div class="section">
    <div class="section-hdr">
      <h2>📚 Subject-wise Engagement</h2>
      <button class="dl-btn" onclick="dlSection(this,'Subject_Engagement')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart2, 'subject_engagement.jpg')}
  </div>

  <!-- Top/Bottom + Class side by side -->
  <div class="section">
    <div class="section-hdr">
      <h2>🏅 Top vs Bottom Schools</h2>
      <button class="dl-btn" onclick="dlSection(this,'Top_Bottom_Schools')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart6, 'top_bottom_schools.jpg')}
  </div>

  <div class="section">
    <div class="section-hdr">
      <h2>🏫 Usage by Class</h2>
      <button class="dl-btn" onclick="dlSection(this,'Class_Performance')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart5, 'class_performance.jpg')}
  </div>

  <p class="full" style="text-align:center;font-size:11px;color:{COLORS['muted']};padding:8px 0">
    Generated by EdTech Analytics Tool &nbsp;•&nbsp; {datetime.now().strftime('%d %b %Y, %H:%M')}
    &nbsp;•&nbsp; Full school-level data in the accompanying Excel summary
  </p>

</div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✅ HTML report saved: {output_path}")


# ─── Excel Summary Export ─────────────────────────────────────────────────────

def export_excel_summary(curr_df, prev_df, kpis, deltas, flags, report_date, output_path):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()

    # ── Style helpers ─────────────────────────────────────────────────────────
    H_FILL  = PatternFill("solid", fgColor="1A3A5C")
    S_FILL  = PatternFill("solid", fgColor="2E86AB")
    A_FILL  = PatternFill("solid", fgColor="EBF5FB")
    G_FILL  = PatternFill("solid", fgColor="D5F5E3")
    R_FILL  = PatternFill("solid", fgColor="FADBD8")
    W_FILL  = PatternFill("solid", fgColor="FEF9E7")
    I_FILL  = PatternFill("solid", fgColor="EBF5FB")

    H_FONT  = Font(name="Segoe UI", bold=True, color="FFFFFF", size=10)
    B_FONT  = Font(name="Segoe UI", size=10)
    T_FONT  = Font(name="Segoe UI", bold=True, color="1A3A5C", size=13)
    SUB_FONT= Font(name="Segoe UI", bold=True, color="1A3A5C", size=10)

    thin   = Side(style="thin",   color="D0D7DE")
    BD     = Border(left=thin, right=thin, top=thin, bottom=thin)
    CTR    = Alignment(horizontal="center", vertical="center", wrap_text=True)
    LFT    = Alignment(horizontal="left",   vertical="center", wrap_text=True)

    def hdr(ws, row, ncols):
        for c in range(1, ncols + 1):
            cell = ws.cell(row=row, column=c)
            cell.fill = H_FILL; cell.font = H_FONT
            cell.alignment = CTR; cell.border = BD

    def body_row(ws, row, ncols, alt=False):
        for c in range(1, ncols + 1):
            cell = ws.cell(row=row, column=c)
            cell.font = B_FONT; cell.border = BD
            cell.alignment = CTR
            if alt: cell.fill = A_FILL

    def title_cell(ws, row, col, text, span_to=None):
        cell = ws.cell(row=row, column=col, value=text)
        cell.font = T_FONT; cell.alignment = LFT
        cell.fill = PatternFill("solid", fgColor="F0F4F8")
        if span_to:
            ws.merge_cells(start_row=row, start_column=col,
                           end_row=row, end_column=span_to)

    def auto_width(ws, mn=10, mx=48):
        for col in ws.columns:
            best = mn
            for cell in col:
                try:
                    best = max(best, len(str(cell.value or "")))
                except Exception:
                    pass
            ws.column_dimensions[get_column_letter(col[0].column)].width = min(mx, best + 4)

    prev_kpis = compute_kpis(prev_df) if prev_df is not None else {}

    # ── Sheet 1: Weekly Snapshot ──────────────────────────────────────────────
    ws = wb.active
    ws.title = "Weekly Snapshot"
    ws.row_dimensions[1].height = 28

    title_cell(ws, 1, 1, f"EdTech Weekly Snapshot — {report_date}", span_to=4)
    ws.append([])

    cols = ["Metric", "This Week", "Last Week", "Change (WoW)"]
    ws.append(cols); hdr(ws, 3, 4)

    rows_def = [
        ("Total Students",          kpis["total_students"],      prev_kpis.get("total_students"),      "total_students",      False),
        ("Active Students",         kpis["active_students"],     prev_kpis.get("active_students"),     "active_students",     False),
        ("Inactive Students",       kpis["inactive_students"],   prev_kpis.get("inactive_students"),   "inactive_students",   True),
        ("Activation Rate (%)",     kpis["activation_rate"],     prev_kpis.get("activation_rate"),     "activation_rate",     False),
        ("Avg Weekly Usage (min)",  kpis["avg_weekly_usage"],    prev_kpis.get("avg_weekly_usage"),    "avg_weekly_usage",    False),
        ("Avg Total Usage (min)",   kpis["avg_total_usage"],     prev_kpis.get("avg_total_usage"),     "avg_total_usage",     False),
        ("Districts Covered",       kpis["districts"],           prev_kpis.get("districts"),           "districts",           False),
        ("Schools Covered",         kpis["schools"],             prev_kpis.get("schools"),             "schools",             False),
        ("Projects",                kpis["projects"],            prev_kpis.get("projects"),            "projects",            False),
    ]

    for i, (label, curr_v, prev_v, key, invert) in enumerate(rows_def):
        delta = deltas.get(key) if deltas else None
        delta_str = ("+" if delta and delta > 0 else "") + str(delta) if delta is not None else "N/A"
        ws.append([label, curr_v, prev_v if prev_v is not None else "N/A", delta_str])
        r = 4 + i; body_row(ws, r, 4, alt=(i % 2 == 0))
        ws.cell(r, 1).alignment = LFT
        # Colour delta cell
        if delta is not None:
            good = delta < 0 if invert else delta > 0
            ws.cell(r, 4).fill = G_FILL if good else (R_FILL if (delta != 0) else A_FILL)

    auto_width(ws)

    # ── Sheet 2: Red Flags ────────────────────────────────────────────────────
    ws2 = wb.create_sheet("Red Flags")
    title_cell(ws2, 1, 1, f"Red Flags & Alerts — {report_date}", span_to=3)
    ws2.append([])
    ws2.append(["Severity", "Alert", "Detail"]); hdr(ws2, 3, 3)

    level_fill = {"critical": R_FILL, "warning": W_FILL, "info": I_FILL}
    for i, f in enumerate(flags):
        ws2.append([f["level"].upper(), f["title"].replace("🚨","").replace("⚠️","")
                    .replace("📉","").replace("👥","").replace("ℹ️","").strip(),
                    f["detail"]])
        r = 4 + i; body_row(ws2, r, 3, alt=False)
        ws2.cell(r, 1).fill = level_fill.get(f["level"], A_FILL)
        ws2.cell(r, 1).font = Font(name="Segoe UI", bold=True, size=10)
        ws2.cell(r, 1).alignment = CTR
        ws2.cell(r, 2).alignment = LFT
        ws2.cell(r, 3).alignment = LFT

    if not flags:
        ws2.append(["—", "No red flags this week ✅", ""])
        body_row(ws2, 4, 3); ws2.cell(4, 2).fill = G_FILL

    auto_width(ws2)

    # ── Sheet 3: District Summary ─────────────────────────────────────────────
    ws3 = wb.create_sheet("District Summary")
    title_cell(ws3, 1, 1, f"District-level Summary — {report_date}", span_to=8)
    ws3.append([])

    dist = curr_df.groupby("district").agg(
        Students=("username", "count"),
        Active=("Weekly Usage", lambda x: (x > 0).sum()),
        Activation_pct=("Weekly Usage", lambda x: round((x > 0).mean() * 100, 1)),
        Avg_Weekly=("Weekly Usage", lambda x: round(x.mean(), 1)),
        Avg_Total=("Total Usage", lambda x: round(x.mean(), 1)),
        Lang_Level=("Lang PreciseLevel", lambda x: round(x.mean(), 2)),
        Math_Level=("Math Precise Level", lambda x: round(x.mean(), 2)),
        Eng_Level=("English PreciseLevel", lambda x: round(x.mean(), 2)),
        Schools=("s.name", "nunique"),
    ).reset_index().sort_values("Avg_Weekly", ascending=False)

    ws3.append(["District", "Schools", "Students", "Active", "Activation %",
                "Avg Weekly (min)", "Avg Total (min)", "Lang Level", "Math Level", "Eng Level"])
    hdr(ws3, 3, 10)

    for i, (_, row) in enumerate(dist.iterrows()):
        ws3.append([row["district"], row["Schools"], row["Students"], row["Active"],
                    row["Activation_pct"], row["Avg_Weekly"], row["Avg_Total"],
                    row["Lang_Level"], row["Math_Level"], row["Eng_Level"]])
        r = 4 + i; body_row(ws3, r, 10, alt=(i % 2 == 0))
        ws3.cell(r, 1).alignment = LFT
        act_cell = ws3.cell(r, 5)
        act_cell.fill = (G_FILL if row["Activation_pct"] >= 70 else
                         W_FILL if row["Activation_pct"] >= 40 else R_FILL)

    auto_width(ws3)

    # ── Sheet 4: Top & Bottom Schools (by Avg Total Usage / Active Student) ────
    ws4 = wb.create_sheet("School Rankings")
    title_cell(ws4, 1, 1,
               f"School Rankings (Avg Total Usage / Active Student) — {report_date}",
               span_to=9)
    ws4.append([])

    school_cols = ["School", "District", "Total Students", "Active Students",
                   "Activation %", "Avg Total Usage / Active (min)",
                   "Lang Level", "Math Level", "Status"]

    # Build per-school stats with the new metric
    def _school_agg(grp):
        active_mask = grp["Total Usage"] > 0
        active_cnt  = int(active_mask.sum())
        total_cnt   = len(grp)
        avg_total   = round(grp.loc[active_mask, "Total Usage"].mean(), 1) if active_cnt else 0.0
        return pd.Series({
            "district":    grp["district"].iloc[0],
            "students":    total_cnt,
            "active":      active_cnt,
            "activation":  round(active_cnt / total_cnt * 100, 1) if total_cnt else 0.0,
            "avg_total":   avg_total,
            "lang":        round(grp["Lang PreciseLevel"].mean(), 2),
            "math":        round(grp["Math Precise Level"].mean(), 2),
        })

    school_stats = curr_df.groupby("s.name").apply(
        _school_agg, include_groups=False
    ).reset_index()

    top10 = school_stats.nlargest(10, "avg_total")
    # Bottom 10: exclude schools with 0 avg (no active students at all)
    bot10 = school_stats[
        school_stats["avg_total"] > 0
    ].nsmallest(10, "avg_total")

    for label, subset, fill_good in [("🏆 Top 10 – Highest Avg Total Usage / Active Student", top10, True),
                                      ("⚠️ Bottom 10 – Lowest (with some usage)", bot10, False)]:
        ws4.append([label]); r = ws4.max_row
        ws4.cell(r, 1).font = SUB_FONT
        ws4.cell(r, 1).fill = G_FILL if fill_good else R_FILL
        ws4.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
        ws4.append(school_cols); hdr(ws4, ws4.max_row, 9)

        for i, (_, row) in enumerate(subset.iterrows()):
            status = ("🟢 Good"    if row["avg_total"] >= 5000 else
                      "🟡 Watch"   if row["avg_total"] >= 1000 else "🔴 Critical")
            ws4.append([row["s.name"], row["district"], row["students"],
                        row["active"], row["activation"], row["avg_total"],
                        row["lang"], row["math"], status])
            r2 = ws4.max_row; body_row(ws4, r2, 9, alt=(i % 2 == 0))
            ws4.cell(r2, 1).alignment = LFT
            ws4.cell(r2, 2).alignment = LFT
            st_fill = (G_FILL if row["avg_total"] >= 5000 else
                       W_FILL if row["avg_total"] >= 1000 else R_FILL)
            ws4.cell(r2, 9).fill = st_fill
        ws4.append([])

    auto_width(ws4)

    # ── Sheet 5: Subject Breakdown by District ────────────────────────────────
    ws5 = wb.create_sheet("Subject by District")
    title_cell(ws5, 1, 1, f"Subject Engagement by District — {report_date}", span_to=6)
    ws5.append([])
    ws5.append(["District", "Lang (min/wk)", "Math (min/wk)", "English (min/wk)",
                "CT (min/wk)", "Total Weekly (min)"])
    hdr(ws5, 3, 6)

    subj = curr_df.groupby("district").agg(
        Lang=("Language_weekly",  lambda x: round(x.mean(), 1)),
        Math=("Math_weekly",      lambda x: round(x.mean(), 1)),
        Eng=("English_weekly",    lambda x: round(x.mean(), 1)),
        CT=("CT_Weekly",          lambda x: round(x.mean(), 1)),
    ).reset_index()
    subj["Total"] = (subj["Lang"] + subj["Math"] + subj["Eng"] + subj["CT"]).round(1)
    subj = subj.sort_values("Total", ascending=False)

    for i, (_, row) in enumerate(subj.iterrows()):
        ws5.append([row["district"], row["Lang"], row["Math"],
                    row["Eng"], row["CT"], row["Total"]])
        r = 4 + i; body_row(ws5, r, 6, alt=(i % 2 == 0))
        ws5.cell(r, 1).alignment = LFT

    auto_width(ws5)

    # ── Sheet 6: Email Body ───────────────────────────────────────────────────
    ws6 = wb.create_sheet("Email Body")
    mail = generate_mail_body(kpis, deltas, flags, curr_df, report_date)
    title_cell(ws6, 1, 1, "Ready-to-Copy Email Body", span_to=2)
    ws6.append([])
    ws6.cell(3, 1).value = mail
    ws6.cell(3, 1).alignment = Alignment(wrap_text=True, vertical="top")
    ws6.cell(3, 1).font = Font(name="Courier New", size=10)
    ws6.column_dimensions["A"].width = 90
    ws6.row_dimensions[3].height = max(400, mail.count("\n") * 15)

    wb.save(output_path)
    print(f"  ✅ Excel summary saved: {output_path}")


# ─── Current-Week-Only Mode ──────────────────────────────────────────────────
# A second mode that generates insights and charts for the current week only,
# WITHOUT week-on-week comparison. Adds richer, single-week-focused visuals.

def generate_current_week_insights(df):
    """Produce concise, single-week narrative insights (no WoW dependency)."""
    insights = []
    total = len(df)
    if total == 0:
        return insights

    active = int((df["Weekly Usage"] > 0).sum())
    activation_rate = active / total * 100

    # 1. Engagement mix
    power_users = int((df["Weekly Usage"] >= 180).sum())
    active_users = int(((df["Weekly Usage"] >= 60) & (df["Weekly Usage"] < 180)).sum())
    moderate = int(((df["Weekly Usage"] >= 20) & (df["Weekly Usage"] < 60)).sum())
    low = int(((df["Weekly Usage"] > 0) & (df["Weekly Usage"] < 20)).sum())
    inactive = int((df["Weekly Usage"] == 0).sum())
    insights.append({
        "title": "🎯 Engagement Mix",
        "detail": (f"{power_users} Power Users (≥180m), {active_users} Active (60–180m), "
                   f"{moderate} Moderate (20–60m), {low} Low (<20m), {inactive} Inactive (0m). "
                   f"Activation rate: {activation_rate:.1f}%."),
        "level": "info",
    })

    # 2. Most-engaged subject
    subj_avg = {
        "Language": df["Language_weekly"].mean(),
        "English":  df["English_weekly"].mean(),
        "Math":     df["Math_weekly"].mean(),
        "CT":       df["CT_Weekly"].mean(),
    }
    top_subject = max(subj_avg, key=subj_avg.get)
    insights.append({
        "title": "📚 Most-Engaged Subject",
        "detail": (f"{top_subject} leads at {subj_avg[top_subject]:.1f} min/student. Mix: "
                   + ", ".join(f"{s} {v:.0f}m" for s, v in subj_avg.items())),
        "level": "info",
    })

    # 3. District leaderboard gap
    dist_avg = df.groupby("district")["Weekly Usage"].mean().sort_values(ascending=False)
    if len(dist_avg) >= 2:
        gap = dist_avg.iloc[0] - dist_avg.iloc[-1]
        insights.append({
            "title": "🗺️ District Leaderboard",
            "detail": (f"'{dist_avg.index[0]}' leads with {dist_avg.iloc[0]:.1f} min/student. "
                       f"Gap vs lowest ('{dist_avg.index[-1]}' at {dist_avg.iloc[-1]:.1f}m) is "
                       f"{gap:.1f} min — indicates uneven adoption."),
            "level": "info",
        })

    # 4. Subject diversity
    div = (
        (df["Language_weekly"] > 0).astype(int)
        + (df["English_weekly"] > 0).astype(int)
        + (df["Math_weekly"] > 0).astype(int)
        + (df["CT_Weekly"] > 0).astype(int)
    )
    multi = int((div >= 3).sum())
    single = int((div == 1).sum())
    avg_div_active = div[df["Weekly Usage"] > 0].mean() if active else 0
    insights.append({
        "title": "🌈 Subject Diversity",
        "detail": (f"{multi} students engage with 3+ subjects this week; {single} stick to just one. "
                   f"Avg subjects per active student: {avg_div_active:.2f} / 4."),
        "level": "info",
    })

    # 5. Proficiency mastery
    high_lang = int((df["Lang PreciseLevel"] >= 4).sum())
    high_math = int((df["Math Precise Level"] >= 4).sum())
    high_eng  = int((df["English PreciseLevel"] >= 4).sum())
    insights.append({
        "title": "🏆 Proficiency Mastery",
        "detail": (f"At Level ≥4: Language {high_lang} ({high_lang/total*100:.1f}%), "
                   f"Math {high_math} ({high_math/total*100:.1f}%), "
                   f"English {high_eng} ({high_eng/total*100:.1f}%)."),
        "level": "info",
    })

    # 6. School health
    school_act = df.groupby("s.name").apply(
        lambda g: (g["Weekly Usage"] > 0).mean() * 100, include_groups=False
    )
    healthy = int((school_act >= 70).sum())
    if len(school_act) > 0:
        insights.append({
            "title": "🏫 School Health",
            "detail": (f"{healthy} of {len(school_act)} schools have ≥70% activation. "
                       f"Best: '{school_act.idxmax()}' ({school_act.max():.1f}%). "
                       f"Worst: '{school_act.idxmin()}' ({school_act.min():.1f}%)."),
            "level": "info",
        })

    # 7. Usage vs proficiency correlation
    df_corr = df[df["Weekly Usage"] > 0].copy()
    if len(df_corr) > 5:
        df_corr["avg_prof"] = df_corr[
            ["Lang PreciseLevel", "Math Precise Level", "English PreciseLevel"]
        ].mean(axis=1)
        df_corr = df_corr[df_corr["avg_prof"] > 0]
        if len(df_corr) > 5:
            corr = df_corr["Weekly Usage"].corr(df_corr["avg_prof"])
            trend = ("a clear positive" if corr > 0.3 else
                     "a mild positive"  if corr > 0.1 else
                     "no meaningful"    if abs(corr) <= 0.1 else
                     "a mild negative"  if corr > -0.3 else "a clear negative")
            insights.append({
                "title": "🔬 Usage ↔ Proficiency",
                "detail": (f"Correlation between weekly usage and avg proficiency is "
                           f"{corr:.2f} — {trend} link this week."),
                "level": "info",
            })

    return insights


def chart_engagement_segments(df):
    """Donut + bar chart showing distribution of students by weekly engagement tier."""
    tiers = [
        ("Power (≥180m)",     int((df["Weekly Usage"] >= 180).sum()),                                COLORS["success"]),
        ("Active (60-180m)",  int(((df["Weekly Usage"] >= 60) & (df["Weekly Usage"] < 180)).sum()), COLORS["secondary"]),
        ("Moderate (20-60m)", int(((df["Weekly Usage"] >= 20) & (df["Weekly Usage"] < 60)).sum()),  COLORS["accent"]),
        ("Low (1-20m)",       int(((df["Weekly Usage"] > 0)  & (df["Weekly Usage"] < 20)).sum()),   COLORS["warning"]),
        ("Inactive (0m)",     int((df["Weekly Usage"] == 0).sum()),                                  COLORS["danger"]),
    ]
    non_zero = [t for t in tiers if t[1] > 0]
    if not non_zero:
        fig, ax = plt.subplots(figsize=(11, 4))
        ax.text(0.5, 0.5, "No engagement data", ha="center", va="center")
        return fig_to_base64(fig)

    labels = [t[0] for t in non_zero]
    sizes  = [t[1] for t in non_zero]
    colors = [t[2] for t in non_zero]
    total  = sum(sizes)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Donut
    wedges, _, autotexts = axes[0].pie(
        sizes, labels=labels, colors=colors,
        autopct=lambda pct: f"{pct:.1f}%\n({int(round(pct/100*total))})",
        startangle=90, pctdistance=0.78,
        wedgeprops={"width": 0.4, "edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 9},
    )
    for at in autotexts:
        at.set_color("white"); at.set_fontweight("bold"); at.set_fontsize(8)
    axes[0].set_title("Student Engagement Segments")
    axes[0].text(0, 0, f"{total}\nStudents", ha="center", va="center",
                 fontsize=14, fontweight="bold", color=COLORS["primary"])

    # Bar
    y_pos = np.arange(len(labels))
    bars = axes[1].barh(y_pos, sizes, color=colors, edgecolor="none", height=0.6)
    axes[1].set_yticks(y_pos); axes[1].set_yticklabels(labels, fontsize=9)
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Number of Students")
    axes[1].set_title("Engagement Tier Counts")
    axes[1].grid(axis="x", alpha=0.4)
    for bar, s in zip(bars, sizes):
        axes[1].text(bar.get_width() + max(sizes) * 0.01,
                     bar.get_y() + bar.get_height() / 2,
                     f"{s} ({s/total*100:.1f}%)",
                     va="center", fontsize=8.5, color=COLORS["primary"])

    fig.tight_layout(pad=2)
    return fig_to_base64(fig)


def chart_usage_distribution(df):
    """Histogram of weekly usage with mean/median + tier thresholds marked."""
    data = df["Weekly Usage"].values
    if (data > 0).any():
        cap = np.percentile(data[data > 0], 99)
        cap = max(cap, 60)
    else:
        cap = 100
    capped = np.clip(data, 0, cap)

    fig, ax = plt.subplots(figsize=(13, 5))
    ax.hist(capped, bins=30, color=COLORS["secondary"],
            edgecolor="white", alpha=0.85, linewidth=0.5)

    for thr, color, lbl in [(20, COLORS["warning"], "Low (20m)"),
                            (60, COLORS["accent"],  "Moderate (60m)"),
                            (180, COLORS["success"], "Power (180m)")]:
        if thr < cap:
            ax.axvline(thr, color=color, linestyle="--", linewidth=1.5,
                       label=lbl, alpha=0.85)

    mean   = df["Weekly Usage"].mean()
    median = df["Weekly Usage"].median()
    ax.axvline(mean,   color=COLORS["danger"],  linestyle="-",  linewidth=2,
               label=f"Mean: {mean:.1f}m")
    ax.axvline(median, color=COLORS["primary"], linestyle=":",  linewidth=2,
               label=f"Median: {median:.1f}m")

    ax.set_title(f"Weekly Usage Distribution (capped at {cap:.0f}m for readability)")
    ax.set_xlabel("Minutes / Week")
    ax.set_ylabel("# Students")
    ax.legend(fontsize=9, framealpha=0.9, loc="upper right")
    ax.grid(axis="y", alpha=0.4)
    fig.tight_layout(pad=2)
    return fig_to_base64(fig)


def chart_subject_diversity(df):
    """How many subjects each student touched + per-subject reach %."""
    div = (
        (df["Language_weekly"] > 0).astype(int)
        + (df["English_weekly"] > 0).astype(int)
        + (df["Math_weekly"] > 0).astype(int)
        + (df["CT_Weekly"] > 0).astype(int)
    )
    counts = div.value_counts().sort_index()
    for k in range(5):
        if k not in counts.index:
            counts[k] = 0
    counts = counts.sort_index()

    labels = [f"{i} subj" for i in counts.index]
    pal = [COLORS["danger"], COLORS["warning"], COLORS["accent"],
           COLORS["secondary"], COLORS["success"]]

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    bars = axes[0].bar(labels, counts.values, color=pal, edgecolor="none", width=0.6)
    total = counts.sum()
    for bar, v in zip(bars, counts.values):
        if v > 0:
            axes[0].text(bar.get_x() + bar.get_width()/2,
                         bar.get_height() + max(counts.values) * 0.02,
                         f"{v}\n({v/total*100:.1f}%)",
                         ha="center", va="bottom", fontsize=8.5,
                         color=COLORS["primary"], fontweight="bold")
    axes[0].set_title("Subject Diversity per Student (this week)")
    axes[0].set_ylabel("# Students")
    axes[0].set_xlabel("# Subjects Engaged")
    axes[0].grid(axis="y", alpha=0.4)

    reach_n = {
        "Language": int((df["Language_weekly"] > 0).sum()),
        "English":  int((df["English_weekly"] > 0).sum()),
        "Math":     int((df["Math_weekly"] > 0).sum()),
        "CT":       int((df["CT_Weekly"] > 0).sum()),
    }
    reach_pct = {k: (v / len(df) * 100 if len(df) else 0) for k, v in reach_n.items()}
    subj_colors = [COLORS["lang"], COLORS["english"], COLORS["math"], COLORS["ct"]]
    bars2 = axes[1].bar(list(reach_pct.keys()), list(reach_pct.values()),
                         color=subj_colors, edgecolor="none", width=0.55)
    for bar, (k, v) in zip(bars2, reach_n.items()):
        axes[1].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + max(reach_pct.values()) * 0.02,
                     f"{v}\n({reach_pct[k]:.1f}%)",
                     ha="center", va="bottom", fontsize=8.5,
                     color=COLORS["primary"], fontweight="bold")
    axes[1].set_title("Per-Subject Reach (% of all students)")
    axes[1].set_ylabel("% Students")
    axes[1].grid(axis="y", alpha=0.4)

    fig.tight_layout(pad=2)
    return fig_to_base64(fig)


def chart_proficiency_vs_usage(df):
    """Scatter plot: Weekly Usage vs Avg Proficiency, coloured by class."""
    df_plot = df[df["Weekly Usage"] > 0].copy()
    df_plot["avg_prof"] = df_plot[
        ["Lang PreciseLevel", "Math Precise Level", "English PreciseLevel"]
    ].mean(axis=1)
    df_plot = df_plot[df_plot["avg_prof"] > 0]

    fig, ax = plt.subplots(figsize=(11, 5))
    if len(df_plot) == 0:
        ax.text(0.5, 0.5, "Not enough data for scatter",
                ha="center", va="center", transform=ax.transAxes, fontsize=12)
        return fig_to_base64(fig)

    if "class" in df_plot.columns and df_plot["class"].notna().any():
        classes = sorted(df_plot["class"].dropna().unique())
        cmap = plt.colormaps["viridis"]
        cmap_n = max(1, len(classes) - 1)
        for i, c in enumerate(classes):
            sub = df_plot[df_plot["class"] == c]
            ax.scatter(sub["Weekly Usage"], sub["avg_prof"],
                       color=cmap(i / cmap_n), alpha=0.55, s=30,
                       label=f"Class {c}", edgecolors="white", linewidths=0.5)
        ax.legend(title="Class", fontsize=8, title_fontsize=9,
                  framealpha=0.9, loc="best", ncol=2)
    else:
        ax.scatter(df_plot["Weekly Usage"], df_plot["avg_prof"],
                   color=COLORS["secondary"], alpha=0.55, s=30,
                   edgecolors="white", linewidths=0.5)

    corr = df_plot["Weekly Usage"].corr(df_plot["avg_prof"])
    try:
        z = np.polyfit(df_plot["Weekly Usage"], df_plot["avg_prof"], 1)
        xp = np.linspace(df_plot["Weekly Usage"].min(),
                         df_plot["Weekly Usage"].max(), 50)
        ax.plot(xp, np.polyval(z, xp), color=COLORS["danger"],
                linewidth=2, linestyle="--", label=f"Trend (r={corr:.2f})")
    except Exception:
        pass

    ax.set_title(f"Weekly Usage vs Avg Proficiency  (correlation = {corr:.2f})")
    ax.set_xlabel("Weekly Usage (min)")
    ax.set_ylabel("Avg Proficiency Level (Lang/Math/Eng)")
    ax.grid(alpha=0.4)
    fig.tight_layout(pad=2)
    return fig_to_base64(fig)


def chart_district_subject_heatmap(df):
    """District × Subject heatmap of avg weekly engagement (min/student)."""
    matrix = df.groupby("district").agg(
        Language=("Language_weekly", "mean"),
        English=("English_weekly",   "mean"),
        Math=("Math_weekly",         "mean"),
        CT=("CT_Weekly",             "mean"),
    ).round(1)

    fig, ax = plt.subplots(figsize=(11, max(4, len(matrix) * 0.55)))
    if len(matrix) == 0:
        return fig_to_base64(fig)

    im = ax.imshow(matrix.values, cmap="YlGnBu", aspect="auto")
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, fontsize=10)
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels(matrix.index, fontsize=9)
    plt.colorbar(im, ax=ax, label="Avg Minutes / Week", shrink=0.7)

    vmax = max(0.0001, matrix.values.max())
    threshold = vmax * 0.6
    for i in range(len(matrix.index)):
        for j in range(len(matrix.columns)):
            v = matrix.values[i, j]
            ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                    fontsize=10, fontweight="bold",
                    color="white" if v > threshold else COLORS["primary"])

    ax.set_title("District × Subject — Avg Weekly Engagement (min)")
    fig.tight_layout(pad=2)
    return fig_to_base64(fig)


def chart_top_active_schools(df):
    """Top-10 schools by Avg Weekly Usage + Top-10 by Activation Rate, side-by-side."""
    stats = df.groupby("s.name").agg(
        weekly=("Weekly Usage", "mean"),
        activation=("Weekly Usage", lambda x: (x > 0).mean() * 100),
        students=("username", "count"),
    ).reset_index()

    top_usage  = stats.nlargest(10, "weekly")
    top_active = stats.nlargest(10, "activation")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    axes[0].barh(range(len(top_usage)), top_usage["weekly"],
                 color=COLORS["success"], edgecolor="none", height=0.6)
    axes[0].set_yticks(range(len(top_usage)))
    axes[0].set_yticklabels(top_usage["s.name"], fontsize=8.5)
    axes[0].invert_yaxis()
    axes[0].set_title("Top 10 Schools — Avg Weekly Usage")
    axes[0].set_xlabel("Minutes / Week")
    axes[0].grid(axis="x", alpha=0.4)
    if len(top_usage):
        max_v = max(top_usage["weekly"])
        for i, (_, r) in enumerate(top_usage.iterrows()):
            axes[0].text(r["weekly"] + max_v * 0.01, i,
                         f"{r['weekly']:.1f}m", va="center",
                         fontsize=8, color=COLORS["primary"])

    axes[1].barh(range(len(top_active)), top_active["activation"],
                 color=COLORS["secondary"], edgecolor="none", height=0.6)
    axes[1].set_yticks(range(len(top_active)))
    axes[1].set_yticklabels(top_active["s.name"], fontsize=8.5)
    axes[1].invert_yaxis()
    axes[1].set_title("Top 10 Schools — Activation Rate")
    axes[1].set_xlabel("% Active Students")
    axes[1].set_xlim(0, 110)
    axes[1].grid(axis="x", alpha=0.4)
    for i, (_, r) in enumerate(top_active.iterrows()):
        axes[1].text(r["activation"] + 1, i,
                     f"{r['activation']:.1f}%", va="center",
                     fontsize=8, color=COLORS["primary"])

    fig.tight_layout(pad=2)
    return fig_to_base64(fig)


def build_html_report_current_only(df, report_date, output_path):
    """HTML report focused on current week only (no WoW comparison)."""
    kpis     = compute_kpis(df)
    flags    = find_red_flags(df, None)
    insights = generate_current_week_insights(df)

    print("  Generating current-week-only charts...")
    chart_segments         = chart_engagement_segments(df)
    chart_usage_hist       = chart_usage_distribution(df)
    chart_diversity        = chart_subject_diversity(df)
    chart_scatter          = chart_proficiency_vs_usage(df)
    chart_district_heatmap = chart_district_subject_heatmap(df)
    chart_top_schools      = chart_top_active_schools(df)

    chart1 = chart_district_usage(df)
    chart2 = chart_subject_breakdown(df)
    chart3 = chart_proficiency_distribution(df)
    chart5 = chart_class_performance(df)
    chart6 = chart_top_bottom_schools(df)

    def wrap_chart_html(c, fn="chart.jpg"):
        if not c:
            return ""
        name = fn.replace(".jpg", "")
        return (f'<img src="data:image/jpeg;base64,{c}" '
                f'style="width:100%;border-radius:8px" id="img_{name}">')

    def insight_html(items):
        if not items:
            return '<div style="color:#7f8c8d;padding:12px">No insights generated.</div>'
        html = ""
        for ins in items:
            html += f"""
            <div style="background:#f7fafc;border-left:4px solid {COLORS['secondary']};
                        border-radius:4px;padding:12px 16px;margin-bottom:8px">
                <strong style="color:{COLORS['primary']}">{ins['title']}</strong>
                <div style="margin-top:4px;font-size:13px;color:{COLORS['primary']}">{ins['detail']}</div>
            </div>"""
        return html

    inactive_schools = df.groupby("s.name")["Weekly Usage"].mean()
    inactive_list = inactive_schools[inactive_schools == 0].index.tolist()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EdTech Weekly Report (Current Week) – {report_date}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f0f4f8;
         color: {COLORS["primary"]}; line-height: 1.6; }}
  .header {{ background: linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["secondary"]} 100%);
             color: white; padding: 28px 48px; }}
  .header h1 {{ font-size: 24px; font-weight: 700; }}
  .header p  {{ opacity: 0.85; margin-top: 4px; font-size: 13px; }}
  .badge {{ display:inline-block;background:rgba(255,255,255,0.18);color:white;
            padding:3px 10px;border-radius:12px;font-size:10px;margin-left:10px;
            font-weight:700;letter-spacing:0.08em;vertical-align:middle; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 20px;
                display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
  .section {{ background: white; border-radius: 10px; padding: 20px;
              box-shadow: 0 2px 10px rgba(0,0,0,0.06); }}
  .full {{ grid-column: 1 / -1; }}
  h2 {{ font-size: 15px; font-weight: 700; color: {COLORS["primary"]};
        margin-bottom: 14px; padding-bottom: 8px; border-bottom: 2px solid #f0f4f8; }}
  .section-hdr {{ display: flex; justify-content: space-between; align-items: center;
                  margin-bottom: 14px; padding-bottom: 8px; border-bottom: 2px solid #f0f4f8; }}
  .section-hdr h2 {{ margin-bottom: 0; padding-bottom: 0; border-bottom: none; }}
  .dl-btn {{ display: inline-flex; align-items: center; gap: 5px;
             padding: 5px 12px; background: {COLORS["secondary"]}; color: white;
             border: none; border-radius: 5px; cursor: pointer;
             font-size: 11px; font-weight: 600; font-family: 'Segoe UI', sans-serif;
             opacity: 0.85; transition: opacity 0.15s; white-space: nowrap; }}
  .dl-btn:hover {{ opacity: 1; background: {COLORS["primary"]}; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px; }}
  @media print {{
    body {{ background: white; }}
    .section {{ box-shadow: none; border: 1px solid #e0e7ef; page-break-inside: avoid; }}
    .dl-btn {{ display: none !important; }}
  }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
function dlSection(btn, name) {{
  var section = btn.closest('.section');
  var img = section.querySelector('img');
  var titleEl = section.querySelector('h2');
  btn.style.visibility = 'hidden';

  function triggerDownload(blob) {{
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = (name || 'section') + '.jpg';
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
    btn.style.visibility = 'visible';
  }}

  if (img) {{
    var titleText = (titleEl ? titleEl.innerText : name).replace(/[^\\x00-\\x7E]/g, '').trim();
    var tmpImg = new Image();
    tmpImg.onload = function() {{
      var pad = 20, titleH = 50;
      var cvs = document.createElement('canvas');
      cvs.width  = tmpImg.naturalWidth;
      cvs.height = tmpImg.naturalHeight + titleH + pad;
      var ctx = cvs.getContext('2d');
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, cvs.width, cvs.height);
      ctx.fillStyle = '#1a3a5c';
      ctx.font = 'bold 28px Segoe UI, Arial, sans-serif';
      ctx.fillText(titleText, pad, pad + 28);
      ctx.drawImage(tmpImg, 0, titleH + pad);
      cvs.toBlob(triggerDownload, 'image/jpeg', 0.93);
    }};
    tmpImg.src = img.src;
  }} else {{
    var origBg = section.style.background;
    section.style.background = '#ffffff';
    html2canvas(section, {{
      scale: 2, backgroundColor: '#ffffff', useCORS: true, logging: false
    }}).then(function(canvas) {{
      section.style.background = origBg;
      canvas.toBlob(triggerDownload, 'image/jpeg', 0.93);
    }});
  }}
}}
</script>
</head>
<body>

<div class="header">
  <h1>📊 EdTech Weekly Snapshot<span class="badge">CURRENT WEEK ONLY</span></h1>
  <p>Report Date: <strong>{report_date}</strong> &nbsp;|&nbsp;
     Data: <strong>{len(df):,} students</strong> across
     <strong>{df["s.name"].nunique()} schools</strong> &amp;
     <strong>{df["district"].nunique()} districts</strong>
     &nbsp;|&nbsp; ▸ Single-week insights mode (no WoW comparison)
  </p>
</div>

<div class="container">

  <!-- KPIs -->
  <div class="section full">
    <div class="section-hdr">
      <h2>🎯 Key Performance Indicators</h2>
      <button class="dl-btn" onclick="dlSection(this,'KPI_Summary')">⬇ Save as JPG</button>
    </div>
    <div class="kpi-grid">
      {kpi_card("Total Students",    kpis["total_students"])}
      {kpi_card("Active Students",   kpis["active_students"])}
      {kpi_card("Activation Rate",   kpis["activation_rate"],  suffix="%",
                is_bad=kpis["activation_rate"] < 50)}
      {kpi_card("Inactive Students", kpis["inactive_students"],
                is_bad=kpis["inactive_students"] > kpis["total_students"] * 0.4)}
      {kpi_card("Avg Weekly Usage",  kpis["avg_weekly_usage"],  suffix=" min")}
      {kpi_card("Avg Total Usage",   kpis["avg_total_usage"],   suffix=" min")}
      {kpi_card("Schools",           kpis["schools"])}
      {kpi_card("Districts",         kpis["districts"])}
      {kpi_card("Projects",          kpis["projects"])}
    </div>
  </div>

  <!-- This week's insights -->
  <div class="section full">
    <div class="section-hdr">
      <h2>💡 This Week's Insights</h2>
      <button class="dl-btn" onclick="dlSection(this,'Insights')">⬇ Save as JPG</button>
    </div>
    {insight_html(insights)}
  </div>

  <!-- Red flags -->
  <div class="section full">
    <div class="section-hdr">
      <h2>🚨 Red Flags &amp; Alerts</h2>
      <button class="dl-btn" onclick="dlSection(this,'Red_Flags')">⬇ Save as JPG</button>
    </div>
    {flag_html(flags)}
    {f'<div style="margin-top:10px;padding:8px 14px;background:#fff3f3;border-radius:6px;font-size:12px"><strong>Schools with ZERO activity:</strong> {", ".join(inactive_list[:10]) + (" …+" + str(len(inactive_list)-10) + " more" if len(inactive_list) > 10 else "")}</div>' if inactive_list else ""}
  </div>

  <!-- Engagement segments -->
  <div class="section full">
    <div class="section-hdr">
      <h2>👥 Student Engagement Segmentation</h2>
      <button class="dl-btn" onclick="dlSection(this,'Engagement_Segments')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart_segments, 'engagement_segments.jpg')}
  </div>

  <!-- Usage histogram -->
  <div class="section full">
    <div class="section-hdr">
      <h2>📊 Weekly Usage Distribution</h2>
      <button class="dl-btn" onclick="dlSection(this,'Usage_Distribution')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart_usage_hist, 'usage_distribution.jpg')}
  </div>

  <!-- District + Subject side-by-side -->
  <div class="section">
    <div class="section-hdr">
      <h2>🗺️ District-level Engagement</h2>
      <button class="dl-btn" onclick="dlSection(this,'District_Engagement')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart1, 'district_engagement.jpg')}
  </div>

  <div class="section">
    <div class="section-hdr">
      <h2>📚 Subject-wise Engagement</h2>
      <button class="dl-btn" onclick="dlSection(this,'Subject_Engagement')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart2, 'subject_engagement.jpg')}
  </div>

  <!-- Subject diversity -->
  <div class="section full">
    <div class="section-hdr">
      <h2>🌈 Subject Diversity &amp; Reach</h2>
      <button class="dl-btn" onclick="dlSection(this,'Subject_Diversity')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart_diversity, 'subject_diversity.jpg')}
  </div>

  <!-- District × Subject heatmap -->
  <div class="section full">
    <div class="section-hdr">
      <h2>🌡️ District × Subject Heatmap</h2>
      <button class="dl-btn" onclick="dlSection(this,'District_Subject_Heatmap')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart_district_heatmap, 'district_subject_heatmap.jpg')}
  </div>

  <!-- Proficiency distribution -->
  <div class="section full">
    <div class="section-hdr">
      <h2>📈 Proficiency Level Distribution</h2>
      <button class="dl-btn" onclick="dlSection(this,'Proficiency_Distribution')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart3, 'proficiency_distribution.jpg')}
  </div>

  <!-- Usage vs Proficiency scatter -->
  <div class="section full">
    <div class="section-hdr">
      <h2>🔬 Weekly Usage vs Proficiency</h2>
      <button class="dl-btn" onclick="dlSection(this,'Usage_vs_Proficiency')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart_scatter, 'usage_vs_proficiency.jpg')}
  </div>

  <!-- Top 10 schools spotlight -->
  <div class="section full">
    <div class="section-hdr">
      <h2>🏆 Top 10 Schools — Usage &amp; Activation</h2>
      <button class="dl-btn" onclick="dlSection(this,'Top_10_Schools')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart_top_schools, 'top_10_schools.jpg')}
  </div>

  <!-- Top/Bottom + Class side-by-side -->
  <div class="section">
    <div class="section-hdr">
      <h2>🏅 Top vs Bottom Schools (Total Usage)</h2>
      <button class="dl-btn" onclick="dlSection(this,'Top_Bottom_Schools')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart6, 'top_bottom_schools.jpg')}
  </div>

  <div class="section">
    <div class="section-hdr">
      <h2>🏫 Performance by Class</h2>
      <button class="dl-btn" onclick="dlSection(this,'Class_Performance')">⬇ Save as JPG</button>
    </div>
    {wrap_chart_html(chart5, 'class_performance.jpg')}
  </div>

  <p class="full" style="text-align:center;font-size:11px;color:{COLORS['muted']};padding:8px 0">
    Generated by EdTech Analytics Tool (Current-Week Mode) &nbsp;•&nbsp;
    {datetime.now().strftime('%d %b %Y, %H:%M')} &nbsp;•&nbsp;
    Full school-level data in the accompanying Excel summary
  </p>

</div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✅ HTML report saved: {output_path}")


def export_excel_summary_current_only(df, kpis, flags, insights, report_date, output_path):
    """Excel summary for current-week-only mode (no WoW columns)."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()

    H_FILL = PatternFill("solid", fgColor="1A3A5C")
    A_FILL = PatternFill("solid", fgColor="EBF5FB")
    G_FILL = PatternFill("solid", fgColor="D5F5E3")
    R_FILL = PatternFill("solid", fgColor="FADBD8")
    W_FILL = PatternFill("solid", fgColor="FEF9E7")
    I_FILL = PatternFill("solid", fgColor="EBF5FB")

    H_FONT   = Font(name="Segoe UI", bold=True, color="FFFFFF", size=10)
    B_FONT   = Font(name="Segoe UI", size=10)
    T_FONT   = Font(name="Segoe UI", bold=True, color="1A3A5C", size=13)
    SUB_FONT = Font(name="Segoe UI", bold=True, color="1A3A5C", size=10)

    thin = Side(style="thin", color="D0D7DE")
    BD   = Border(left=thin, right=thin, top=thin, bottom=thin)
    CTR  = Alignment(horizontal="center", vertical="center", wrap_text=True)
    LFT  = Alignment(horizontal="left",   vertical="center", wrap_text=True)

    def hdr(ws, row, ncols):
        for c in range(1, ncols + 1):
            cell = ws.cell(row=row, column=c)
            cell.fill = H_FILL; cell.font = H_FONT
            cell.alignment = CTR; cell.border = BD

    def body_row(ws, row, ncols, alt=False):
        for c in range(1, ncols + 1):
            cell = ws.cell(row=row, column=c)
            cell.font = B_FONT; cell.border = BD; cell.alignment = CTR
            if alt: cell.fill = A_FILL

    def title_cell(ws, row, col, text, span_to=None):
        cell = ws.cell(row=row, column=col, value=text)
        cell.font = T_FONT; cell.alignment = LFT
        cell.fill = PatternFill("solid", fgColor="F0F4F8")
        if span_to:
            ws.merge_cells(start_row=row, start_column=col,
                           end_row=row, end_column=span_to)

    def auto_width(ws, mn=10, mx=60):
        for col in ws.columns:
            best = mn
            for cell in col:
                try:
                    best = max(best, len(str(cell.value or "")))
                except Exception:
                    pass
            ws.column_dimensions[get_column_letter(col[0].column)].width = min(mx, best + 4)

    # Sheet 1: Snapshot
    ws = wb.active
    ws.title = "This Week Snapshot"
    title_cell(ws, 1, 1, f"EdTech Current-Week Snapshot — {report_date}", span_to=3)
    ws.append([])
    ws.append(["Metric", "Value", "Notes"]); hdr(ws, 3, 3)

    rows = [
        ("Total Students",         kpis["total_students"],    "All students in dataset"),
        ("Active Students",        kpis["active_students"],   "Weekly usage > 0"),
        ("Inactive Students",      kpis["inactive_students"], "Target < 30%"),
        ("Activation Rate (%)",    kpis["activation_rate"],   "Active / Total"),
        ("Avg Weekly Usage (min)", kpis["avg_weekly_usage"],  "Across all students"),
        ("Avg Total Usage (min)",  kpis["avg_total_usage"],   "Cumulative since start"),
        ("Schools Covered",        kpis["schools"],           ""),
        ("Districts Covered",      kpis["districts"],         ""),
        ("Projects",               kpis["projects"],          ""),
    ]
    for i, (m, v, note) in enumerate(rows):
        ws.append([m, v, note])
        r = 4 + i; body_row(ws, r, 3, alt=(i % 2 == 0))
        ws.cell(r, 1).alignment = LFT
        ws.cell(r, 3).alignment = LFT
    auto_width(ws)

    # Sheet 2: Insights
    ws2 = wb.create_sheet("Insights")
    title_cell(ws2, 1, 1, f"Key Insights — {report_date}", span_to=2)
    ws2.append([])
    ws2.append(["Insight", "Detail"]); hdr(ws2, 3, 2)
    for i, ins in enumerate(insights):
        ws2.append([ins["title"], ins["detail"]])
        r = 4 + i; body_row(ws2, r, 2, alt=(i % 2 == 0))
        ws2.cell(r, 1).alignment = LFT
        ws2.cell(r, 2).alignment = LFT
    auto_width(ws2)

    # Sheet 3: Engagement Segments
    ws3 = wb.create_sheet("Engagement Segments")
    title_cell(ws3, 1, 1, f"Engagement Segmentation — {report_date}", span_to=4)
    ws3.append([])
    ws3.append(["Segment", "Range (min/wk)", "# Students", "% of Total"]); hdr(ws3, 3, 4)

    total = max(1, len(df))
    segs = [
        ("Power Users", "≥ 180",   int((df["Weekly Usage"] >= 180).sum())),
        ("Active",      "60 – 180", int(((df["Weekly Usage"] >= 60) & (df["Weekly Usage"] < 180)).sum())),
        ("Moderate",    "20 – 60",  int(((df["Weekly Usage"] >= 20) & (df["Weekly Usage"] < 60)).sum())),
        ("Low",         "1 – 20",   int(((df["Weekly Usage"] > 0)  & (df["Weekly Usage"] < 20)).sum())),
        ("Inactive",    "0",        int((df["Weekly Usage"] == 0).sum())),
    ]
    for i, (name, rng, n) in enumerate(segs):
        ws3.append([name, rng, n, round(n / total * 100, 1)])
        r = 4 + i; body_row(ws3, r, 4, alt=(i % 2 == 0))
        ws3.cell(r, 1).alignment = LFT
        if name == "Inactive" and n > 0:
            ws3.cell(r, 1).fill = R_FILL
        elif name == "Power Users" and n > 0:
            ws3.cell(r, 1).fill = G_FILL
    auto_width(ws3)

    # Sheet 4: Red Flags
    ws4 = wb.create_sheet("Red Flags")
    title_cell(ws4, 1, 1, f"Red Flags — {report_date}", span_to=3)
    ws4.append([])
    ws4.append(["Severity", "Alert", "Detail"]); hdr(ws4, 3, 3)
    level_fill = {"critical": R_FILL, "warning": W_FILL, "info": I_FILL}
    for i, f in enumerate(flags):
        ws4.append([f["level"].upper(),
                    f["title"].replace("🚨", "").replace("⚠️", "").replace("📉", "")
                    .replace("👥", "").replace("ℹ️", "").strip(),
                    f["detail"]])
        r = 4 + i; body_row(ws4, r, 3)
        ws4.cell(r, 1).fill = level_fill.get(f["level"], A_FILL)
        ws4.cell(r, 1).font = Font(name="Segoe UI", bold=True, size=10)
        ws4.cell(r, 1).alignment = CTR
        ws4.cell(r, 2).alignment = LFT
        ws4.cell(r, 3).alignment = LFT
    if not flags:
        ws4.append(["—", "No red flags this week ✅", ""])
        body_row(ws4, 4, 3); ws4.cell(4, 2).fill = G_FILL
    auto_width(ws4)

    # Sheet 5: District Summary
    ws5 = wb.create_sheet("District Summary")
    title_cell(ws5, 1, 1, f"District-level Summary — {report_date}", span_to=10)
    ws5.append([])
    ws5.append(["District", "Schools", "Students", "Active", "Activation %",
                "Avg Weekly (min)", "Avg Total (min)",
                "Lang Level", "Math Level", "Eng Level"])
    hdr(ws5, 3, 10)
    dist = df.groupby("district").agg(
        Schools=("s.name", "nunique"),
        Students=("username", "count"),
        Active=("Weekly Usage", lambda x: (x > 0).sum()),
        Activation_pct=("Weekly Usage", lambda x: round((x > 0).mean() * 100, 1)),
        Avg_Weekly=("Weekly Usage", lambda x: round(x.mean(), 1)),
        Avg_Total=("Total Usage",   lambda x: round(x.mean(), 1)),
        Lang=("Lang PreciseLevel",  lambda x: round(x.mean(), 2)),
        Math=("Math Precise Level", lambda x: round(x.mean(), 2)),
        Eng=("English PreciseLevel",lambda x: round(x.mean(), 2)),
    ).reset_index().sort_values("Avg_Weekly", ascending=False)
    for i, (_, row) in enumerate(dist.iterrows()):
        ws5.append([row["district"], row["Schools"], row["Students"], row["Active"],
                    row["Activation_pct"], row["Avg_Weekly"], row["Avg_Total"],
                    row["Lang"], row["Math"], row["Eng"]])
        r = 4 + i; body_row(ws5, r, 10, alt=(i % 2 == 0))
        ws5.cell(r, 1).alignment = LFT
        act_cell = ws5.cell(r, 5)
        act_cell.fill = (G_FILL if row["Activation_pct"] >= 70 else
                         W_FILL if row["Activation_pct"] >= 40 else R_FILL)
    auto_width(ws5)

    # Sheet 6: School Rankings (Top/Bottom by Weekly Usage)
    ws6 = wb.create_sheet("School Rankings")
    title_cell(ws6, 1, 1, f"School Rankings — {report_date}", span_to=8)
    ws6.append([])
    school_cols = ["School", "District", "Students", "Active", "Activation %",
                   "Avg Weekly (min)", "Lang Level", "Math Level"]
    school_stats = df.groupby("s.name").agg(
        district=("district", "first"),
        students=("username", "count"),
        active=("Weekly Usage", lambda x: int((x > 0).sum())),
        activation=("Weekly Usage", lambda x: round((x > 0).mean() * 100, 1)),
        weekly=("Weekly Usage", lambda x: round(x.mean(), 1)),
        lang=("Lang PreciseLevel",  lambda x: round(x.mean(), 2)),
        math=("Math Precise Level", lambda x: round(x.mean(), 2)),
    ).reset_index()
    top10 = school_stats.nlargest(10, "weekly")
    bot10 = school_stats[school_stats["weekly"] > 0].nsmallest(10, "weekly")
    for label, subset, good in [("🏆 Top 10 Schools — Avg Weekly Usage", top10, True),
                                 ("⚠️ Bottom 10 Schools (with some usage)", bot10, False)]:
        ws6.append([label]); r = ws6.max_row
        ws6.cell(r, 1).font = SUB_FONT
        ws6.cell(r, 1).fill = G_FILL if good else R_FILL
        ws6.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
        ws6.append(school_cols); hdr(ws6, ws6.max_row, 8)
        for i, (_, row) in enumerate(subset.iterrows()):
            ws6.append([row["s.name"], row["district"], int(row["students"]),
                        int(row["active"]), row["activation"], row["weekly"],
                        row["lang"], row["math"]])
            r2 = ws6.max_row; body_row(ws6, r2, 8, alt=(i % 2 == 0))
            ws6.cell(r2, 1).alignment = LFT
            ws6.cell(r2, 2).alignment = LFT
        ws6.append([])
    auto_width(ws6)

    # Sheet 7: Subject by District
    ws7 = wb.create_sheet("Subject by District")
    title_cell(ws7, 1, 1, f"Subject Engagement by District — {report_date}", span_to=6)
    ws7.append([])
    ws7.append(["District", "Lang (min/wk)", "Math (min/wk)", "English (min/wk)",
                "CT (min/wk)", "Total Weekly (min)"])
    hdr(ws7, 3, 6)
    subj = df.groupby("district").agg(
        Lang=("Language_weekly", lambda x: round(x.mean(), 1)),
        Math=("Math_weekly",     lambda x: round(x.mean(), 1)),
        Eng=("English_weekly",   lambda x: round(x.mean(), 1)),
        CT=("CT_Weekly",         lambda x: round(x.mean(), 1)),
    ).reset_index()
    subj["Total"] = (subj["Lang"] + subj["Math"] + subj["Eng"] + subj["CT"]).round(1)
    subj = subj.sort_values("Total", ascending=False)
    for i, (_, row) in enumerate(subj.iterrows()):
        ws7.append([row["district"], row["Lang"], row["Math"],
                    row["Eng"], row["CT"], row["Total"]])
        r = 4 + i; body_row(ws7, r, 6, alt=(i % 2 == 0))
        ws7.cell(r, 1).alignment = LFT
    auto_width(ws7)

    # Sheet 8: Email Body
    ws8 = wb.create_sheet("Email Body")
    mail = generate_mail_body(kpis, None, flags, df, report_date)
    title_cell(ws8, 1, 1, "Ready-to-Copy Email Body", span_to=2)
    ws8.append([])
    ws8.cell(3, 1).value = mail
    ws8.cell(3, 1).alignment = Alignment(wrap_text=True, vertical="top")
    ws8.cell(3, 1).font = Font(name="Courier New", size=10)
    ws8.column_dimensions["A"].width = 90
    ws8.row_dimensions[3].height = max(400, mail.count("\n") * 15)

    wb.save(output_path)
    print(f"  ✅ Excel summary saved: {output_path}")


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    # No arguments → launch the GUI instead of showing a CLI error
    if len(sys.argv) == 1:
        try:
            import edtech_gui
            edtech_gui.main()
        except Exception as e:
            print(f"Could not launch GUI: {e}")
            print("Run with: python edtech_analyzer.py --current yourfile.xlsx")
        return

    parser = argparse.ArgumentParser(
        description="EdTech Weekly Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single week report (auto-mode: 'current' when no --previous given)
  python3 edtech_analyzer.py --current week26.xlsx

  # Week-on-Week comparison (auto-mode: 'compare')
  python3 edtech_analyzer.py --current week26.xlsx --previous week25.xlsx

  # Force richer current-week-only insights (ignores --previous if given)
  python3 edtech_analyzer.py --current week26.xlsx --mode current

  # Force comparison mode explicitly
  python3 edtech_analyzer.py --current week26.xlsx --previous week25.xlsx --mode compare

  # Custom output location
  python3 edtech_analyzer.py --current data.xlsx --previous prev.xlsx --output ./reports
        """
    )
    parser.add_argument("--current", required=True, help="Current week Excel file (.xlsx)")
    parser.add_argument("--previous", default=None, help="Previous week Excel file for WoW comparison")
    parser.add_argument("--output", default=".", help="Output directory (default: current dir)")
    parser.add_argument("--date", default=None, help="Report date label (default: today)")
    parser.add_argument(
        "--mode", default="auto", choices=["auto", "compare", "current"],
        help="Report mode: 'compare' (vs previous week), 'current' (this-week-only insights), "
             "'auto' (compare if --previous given, else current)."
    )
    args = parser.parse_args()

    # Resolve mode
    mode = args.mode
    if mode == "auto":
        mode = "compare" if args.previous else "current"
    elif mode == "compare" and not args.previous:
        print("⚠️  Mode 'compare' requires --previous. Falling back to 'current' mode.")
        mode = "current"

    report_date = args.date or datetime.now().strftime("%d %B %Y")
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🚀 EdTech Report Generator")
    print(f"   Mode         : {mode.upper()}")
    print(f"   Current file : {args.current}")
    print(f"   Previous file: {args.previous or 'None'}")
    print(f"   Report date  : {report_date}")

    print("\n📂 Loading data...")
    curr_df = load_data(args.current)
    print(f"   ✅ Current: {len(curr_df)} students")
    prev_df = None
    if args.previous and mode == "compare":
        prev_df = load_data(args.previous)
        print(f"   ✅ Previous: {len(prev_df)} students")
        curr_df, prev_df = filter_common_students(curr_df, prev_df)
        print(f"   ✅ Using common students only → Current: {len(curr_df)} | Previous: {len(prev_df)}")
    elif args.previous and mode == "current":
        print(f"   ℹ️  Previous file ignored in 'current' mode.")

    safe_date = report_date.replace(" ", "_").replace(",", "")
    suffix    = "_CurrentWeek" if mode == "current" else ""
    out_html  = output_dir / f"EdTech_Report{suffix}_{safe_date}.html"
    out_xlsx  = output_dir / f"EdTech_Summary{suffix}_{safe_date}.xlsx"

    if mode == "current":
        print("\n📊 Building HTML report (Current-Week-Only mode)...")
        build_html_report_current_only(curr_df, report_date, str(out_html))

        print("\n📊 Building Excel summary (Current-Week-Only mode)...")
        kpis     = compute_kpis(curr_df)
        flags    = find_red_flags(curr_df, None)
        insights = generate_current_week_insights(curr_df)
        export_excel_summary_current_only(curr_df, kpis, flags, insights,
                                          report_date, str(out_xlsx))
    else:
        print("\n📊 Building HTML report...")
        build_html_report(curr_df, prev_df, report_date, str(out_html))

        print("\n📊 Building Excel summary...")
        kpis   = compute_kpis(curr_df)
        deltas = compute_delta(kpis, compute_kpis(prev_df)) if prev_df is not None else None
        flags  = find_red_flags(curr_df, prev_df)
        export_excel_summary(curr_df, prev_df, kpis, deltas, flags,
                             report_date, str(out_xlsx))

    print(f"\n✨ Done!")
    print(f"   HTML  → {out_html.absolute()}")
    print(f"   Excel → {out_xlsx.absolute()}\n")


if __name__ == "__main__":
    main()
