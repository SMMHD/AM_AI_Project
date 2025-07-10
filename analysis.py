# analysis.py (Final Version)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


def analyze_final_results(csv_file="experimental_results.csv"):
    """
    داده‌های نهایی نتایج را از فایل CSV خوانده و نمودارهای کلیدی را برای گزارش نهایی تولید می‌کند.
    """
    # تنظیمات اولیه برای ظاهر زیباتر و حرفه‌ای‌تر نمودارها
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams['figure.figsize'] = (12, 7)
    plt.rcParams['axes.titlesize'] = 18
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['legend.title_fontsize'] = 14

    # ۱. بررسی وجود فایل نتایج
    if not os.path.exists(csv_file):
        print(f"Error: The file '{csv_file}' was not found.")
        print("Please run 'main.py' first to generate the final results.")
        return

    # ۲. خواندن داده‌های نهایی از فایل CSV
    try:
        df = pd.read_csv(csv_file)
        print("Successfully loaded final results. Data summary:")
        print(df)
    except Exception as e:
        print(f"Error reading or processing CSV file: {e}")
        return

    # --- نمودار ۱: مقایسه میانگین وظایف تکمیل‌شده (معیار موفقیت) ---
    plt.figure()
    ax1 = sns.barplot(data=df, x="config_name", y="avg_tasks_completed", hue="agent_type", palette="viridis")

    ax1.set_title("Comparison of Average Tasks Completed (Success Rate)", fontweight='bold')
    ax1.set_xlabel("Experimental Scenario")
    ax1.set_ylabel("Average Tasks Completed")
    ax1.set_ylim(0, df['avg_tasks_completed'].max() * 1.1 + 0.5)
    ax1.legend(title="Agent Type")

    output_path_tasks = "final_comparison_tasks.png"
    plt.savefig(output_path_tasks, dpi=300, bbox_inches='tight')
    print(f"\n✓ Final 'Tasks' chart saved to: {output_path_tasks}")
    plt.close()  # بستن نمودار فعلی

    # --- نمودار ۲: مقایسه میانگین زمان تکمیل وظیفه (مهم‌ترین نمودار - معیار بهره‌وری) ---
    plt.figure()

    # فقط داده‌هایی را رسم می‌کنیم که وظیفه‌ای در آن‌ها انجام شده باشد
    plot_data = df[df['avg_completion_time'] > 0].copy()

    if plot_data.empty:
        print("No tasks were completed in any trial, skipping efficiency plot.")
        return

    ax2 = sns.barplot(data=plot_data, x="config_name", y="avg_completion_time", hue="agent_type", palette="plasma")

    ax2.set_title("Comparison of Average Task Completion Time (Efficiency)", fontweight='bold')
    ax2.set_xlabel("Experimental Scenario")
    ax2.set_ylabel("Average Steps to Complete All Tasks")
    ax2.legend(title="Agent Type")

    output_path_efficiency = "final_comparison_efficiency.png"
    plt.savefig(output_path_efficiency, dpi=300, bbox_inches='tight')
    print(f"✓ Final 'Efficiency' chart saved to: {output_path_efficiency}")
    plt.close()  # بستن نمودار فعلی

    print("\nAnalysis complete. All charts have been generated.")


if __name__ == "__main__":
    analyze_final_results()