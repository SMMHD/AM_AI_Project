# main.py

# وارد کردن کلاس تستر از ماژول مربوطه
from tester import ProjectTester


def main():
    """
    تابع اصلی برنامه که فرآیند اجرای آزمایش‌ها را آغاز می‌کند.
    """
    print("Multi-Agent Systems Project - Simulation Runner")
    print("=================================================")

    # یک نمونه از کلاس تستر ایجاد می‌کنیم
    tester = ProjectTester()

    # متد مقایسه را برای اجرای تمام آزمایش‌ها و ذخیره نتایج فراخوانی می‌کنیم
    tester.run_comparison()

    print("\n✓ Simulation complete! Results saved to 'experimental_results.csv'.")
    print("You can now run 'analysis.py' to generate the final plots.")



if __name__ == "__main__":
    main()