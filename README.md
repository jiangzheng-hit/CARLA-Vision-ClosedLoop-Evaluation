# CARLA Vision Closed Loop Evaluation

面向自动驾驶仿真初学者的 Windows 项目，用于演示如何将开源纯视觉驾驶模型接入 CARLA 0.9.16，完成传感器输入、神经网络推理、轨迹与速度预测、PID 控制以及 Leaderboard 评分的闭环。

## 当前状态

本仓库正在从个人可运行版本整理为可复现的公开版本。现有验证使用 LEAD Vision-only ResNet34 预训练模型，输入为六路 RGB 摄像头、GNSS、IMU 和速度计。Town01 短路线完成率为 100%，碰撞和闯红灯均为 0，主要扣分项为低速违规。

## 数据流

```text
6 路 RGB 图像 + GNSS + IMU + 车速
        -> LEAD 视觉模型
        -> 未来轨迹 + 目标速度
        -> PID 控制器
        -> CARLA 转向 油门 刹车
        -> Leaderboard JSON
        -> CSV 与 Markdown 报告
```

## 仓库内容

- `scenarios/`：晴天、雨天、夜间三种短路线配置
- `tools/summarize_results.py`：汇总 Leaderboard JSON 的独立工具
- `examples/`：脱敏后的示例结果

## 快速查看结果汇总工具

将一个或多个 `checkpoint_endpoint.json` 放入 `outputs/` 的任意子目录后运行：

```powershell
python tools/summarize_results.py
```

工具会生成 `outputs/summary.csv` 和 `outputs/测试报告.md`。

## 依赖与归属

本仓库不会分发 CARLA、LEAD 源码或模型权重。使用者需要分别遵守各上游项目的许可证和模型发布条款。本项目的贡献集中于 Windows 适配、场景组织、自动化运行、结果汇总和中文学习文档。完整安装流程仍在整理中。

## 局限

- 当前公开示例只验证短路线技术链路，不代表真实道路 L4 能力。
- 尚未完成多路线、多随机种子和复杂交通事件统计。
- 仿真结果不能替代封闭场地和真实车辆测试。
