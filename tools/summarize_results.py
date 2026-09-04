"""将 LEAD/Leaderboard JSON 结果汇总成 CSV 和中文 Markdown 报告。"""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = PROJECT_ROOT / "outputs"


def read_result(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        record = data["_checkpoint"]["global_record"]
        scores = record["scores_mean"]
        infractions = record["infractions"]
        meta = record["meta"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError):
        return None

    relative = path.parent.relative_to(OUTPUT_ROOT).as_posix()
    scenario = path.parent.name
    if "_clear_day" in scenario:
        scenario = "晴天"
    elif "_rain" in scenario or scenario == "smoke_vision_only":
        scenario = "雨天"
    elif "_night" in scenario:
        scenario = "夜间"
    else:
        scenario = scenario

    duration_system = float(meta.get("duration_system", 0) or 0)
    duration_game = float(meta.get("duration_game", 0) or 0)
    return {
        "场景": scenario,
        "状态": record.get("status", "Unknown"),
        "驾驶得分": round(float(scores.get("score_composed", 0)), 3),
        "路线完成率(%)": round(float(scores.get("score_route", 0)), 3),
        "违规惩罚系数": round(float(scores.get("score_penalty", 0)), 5),
        "碰撞": round(sum(float(infractions.get(k, 0) or 0) for k in ("collisions_layout", "collisions_pedestrian", "collisions_vehicle")), 3),
        "闯红灯": round(float(infractions.get("red_light", 0) or 0), 3),
        "驶出道路": round(float(infractions.get("outside_route_lanes", 0) or 0), 3),
        "低速违规": round(float(infractions.get("min_speed_infractions", 0) or 0), 3),
        "仿真时长(s)": round(duration_game, 3),
        "实际耗时(s)": round(duration_system, 3),
        "实时率": round(duration_game / duration_system, 3) if duration_system else 0,
        "结果目录": relative,
    }


def main() -> int:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    candidates = sorted(OUTPUT_ROOT.rglob("checkpoint_endpoint.json"))
    rows = [row for path in candidates if (row := read_result(path)) is not None]
    if not rows:
        print("没有找到有效的 checkpoint_endpoint.json")
        return 1

    csv_path = OUTPUT_ROOT / "summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    best = max(rows, key=lambda row: row["驾驶得分"])
    report_path = OUTPUT_ROOT / "测试报告.md"
    headers = ["场景", "状态", "驾驶得分", "路线完成率(%)", "碰撞", "闯红灯", "低速违规", "实时率"]
    lines = [
        "# CARLA 纯视觉闭环测评报告",
        "",
        f"生成时间：{datetime.now():%Y-%m-%d %H:%M:%S}",
        "",
        "## 测试对象",
        "",
        "LEAD Vision-only ResNet34 开源模型；感知使用六路 RGB 摄像头，车辆状态使用 GPS、IMU 和速度计。",
        "",
        "## 结果汇总",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    lines.extend([
        "",
        "## 结论",
        "",
        f"当前最高驾驶得分为 **{best['驾驶得分']}**（{best['场景']}），路线完成率 {best['路线完成率(%)']}%。",
        "安全指标优先观察碰撞、闯红灯和驶出道路；效率指标观察低速违规和实时率。",
        "当前短路线结果证明了感知—规划—控制—评分闭环可运行，但不等同于真实道路 L4 能力认证。",
        "",
        "## 下一步定位方向",
        "",
        "1. 若低速违规明显：检查视觉退化是否降低目标速度，并分析速度控制 PID。",
        "2. 若恶劣天气得分下降：对比晴天/雨天/夜间，归因于图像质量与模型泛化。",
        "3. 若出现碰撞或闯灯：保留原始 JSON，结合录像定位事件前后的模型输出与控制量。",
    ])
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"已汇总 {len(rows)} 个有效结果")
    print(csv_path)
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
