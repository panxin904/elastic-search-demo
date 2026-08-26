---
title: 边缘智能 AI
---

# 边缘智能 AI

> 边缘端推理：TensorFlow Lite / ONNX / OpenVINO。低延迟 + 隐私保护 + 离线可用。

## 🎯 核心要点

- TensorFlow Lite：Google 主导，跨平台（ARM / x86 / MCU）
- ONNX Runtime：跨框架互操作，模型量化工具链完善
- OpenVINO：Intel 优化，x86 CPU / GPU / VPU 加速
- 典型应用：图像分类 / 物体检测 / 异常检测 / 语音唤醒

## 🛠️ 实战示例

```python
# TensorFlow Lite Python 推理
import tflite_runtime.interpreter as tflite

interpreter = tflite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

interpreter.set_tensor(input_details[0]["index"], input_data)
interpreter.invoke()
predictions = interpreter.get_tensor(output_details[0]["index"])
```

## 🔗 相关链接

- [KubeEdge](./framework)
- [设备影子](../04-management/shadow)
- [← 返回 边缘计算 目录](./)
- [← 返回 iot 首页](../)
## 🎯 AI 框架选型

- **TensorFlow Lite**：Google 主导，跨平台
- **ONNX Runtime**：跨框架互操作
- **OpenVINO**：Intel 优化（x86 CPU / GPU / VPU）
- **模型量化**：INT8 / FP16（牺牲精度换速度）
**硬件**：NPU（神经网络处理器）加速推理
**硬件加速**：NPU / GPU / VPU 按场景选，NPU 能效比最高。


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
