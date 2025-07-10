# analysis.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


def analyze_final_results(csv_file="experimental_results.csv"):
    """
    داده‌های نهایی نتایج را از فایل CSV خوانده و نمودارهای کلیدی را برای گزارش نهایی تولید می‌کند.
    """
    # تنظیمات اولیه برای ظاهر زیباتر نمودارها
    sns.set_theme(style="whitegrid")

    # ۱. بررسی وجود فایل نتایج
    if not os.path.exists(csv_file):
        print(f"Error: The file '{csv_file}' was not found.")
        print("Please run 'main.py' first to generate the final results.")
        return

    # ۲. خواندن داده‌ها با استفاده از کتابخانه pandas
    try:
        df = pd.read_csv(csv_file)
        print("Successfully loaded final results. Data summary:")
        print(df)
    except Exception as e:
        print(f"Error reading or processing CSV file: {e}")
        return

    # --- نمودار ۱: مقایسه میانگین وظایف تکمیل‌شده ---
    plt.figure(figsize=(12, 7))
    sns.barplot(data=df, x="config_name", y="avg_tasks_completed", hue="agent_type", palette="viridis")

    plt.title("Comparison of Average Tasks Completed", fontsize=16, fontweight='bold')
    plt.xlabel("Experimental Scenario", fontsize=14)
    plt.ylabel("Average Tasks Completed", fontsize=14)
    plt.ylim(0, df['avg_tasks_completed'].max() + 0.5)  # تنظیم محور Y برای نمایش بهتر
    plt.legend(title="Agent Type", fontsize=12)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    # ذخیره نمودار در فایل
    output_path_tasks = "final_comparison_tasks.png"
    plt.savefig(output_path_tasks, dpi=300, bbox_inches='tight')
    print(f"\n✓ Final 'Tasks' chart saved to: {output_path_tasks}")

    # --- نمودار ۲: مقایسه میانگین زمان تکمیل وظیفه (مهم‌ترین نمودار) ---
    plt.figure(figsize=(12, 7))

    # فقط داده‌هایی را رسم می‌کنیم که وظیفه‌ای در آن‌ها انجام شده باشد تا نمودار منطقی باشد
    plot_data = df[df['avg_completion_time'] > 0].copy()

    sns.barplot(data=plot_data, x="config_name", y="avg_completion_time", hue="agent_type", palette="plasma")

    plt.title("Comparison of Average Task Completion Time (Efficiency)", fontsize=16, fontweight='bold')
    plt.xlabel("Experimental Scenario", fontsize=14)
    plt.ylabel("Average Steps to Complete Tasks", fontsize=14)
    plt.legend(title="Agent Type", fontsize=12)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    # ذخیره نمودار در فایل
    output_path_efficiency = "final_comparison_efficiency.png"
    plt.savefig(output_path_efficiency, dpi=300, bbox_inches='tight')
    print(f"✓ Final 'Efficiency' chart saved to: {output_path_efficiency}")

    # نمایش نمودارها در انتها
    plt.show()


if __name__ == "__main__":
    analyze_final_results()