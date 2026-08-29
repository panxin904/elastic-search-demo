---
title: CUDA / GPU 环境
date: 2026-08-15  # date-auto-injected
---

# CUDA / GPU 环境

> 微调 / 推理的 GPU 环境配置。**CUDA + cuDNN + PyTorch + 驱动**对齐。

## 🧰 硬件选型

| 场景 | 推荐 |
|------|------|
| 个人 / 学习 | RTX 4090 (24GB) / RTX 3090 |
| 推理（70B INT4） | A100 80GB × 1 |
| 推理（70B FP16） | H100 80GB × 2 |
| LoRA 微调 7-13B | RTX 4090 / A100 40GB |
| 全量微调 7B | A100 80GB × 1 |
| 全量微调 70B | H100 80GB × 8+ |
| 训练 + 推理 | H100 / A100 80GB × 4-8 |

## 🛠 装驱动

```bash
# NVIDIA 驱动
sudo apt update
sudo apt install -y nvidia-driver-550   # Ubuntu
# 或
sudo dnf install -y nvidia-driver        # RHEL

# 重启
sudo reboot

# 验证
nvidia-smi
```

## 🔧 装 CUDA

```bash
# 方式 1：apt（推荐，绑定 driver）
sudo apt install -y cuda-toolkit-12-6

# 方式 2：runfile（最新版）
wget https://developer.download.nvidia.com/compute/cuda/12.6.0/local_installers/cuda_12.6.0_560.28.03_linux.run
sudo sh cuda_*.run
```

```bash
# 加环境变量
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# 验证
nvcc --version
nvidia-smi
```

## 🐍 装 PyTorch（CUDA 版）

```bash
# 装 PyTorch（CUDA 12.6）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# 装 bitsandbytes（4-bit 量化 / QLoRA）
pip install bitsandbytes

# 装 flash-attn（vLLM / SGLang 用）
pip install flash-attn --no-build-isolation
```

```python
# 验证
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
print(torch.cuda.get_device_capability())
```

## 🔧 多 GPU

```bash
# PyTorch 自动用全部可见 GPU
nvidia-smi
# 看 GPU 0/1/2/3

# 指定可见 GPU
CUDA_VISIBLE_DEVICES=0,2 python train.py
```

## 🚀 vLLM 部署

```bash
# 装
pip install vllm

# 起服务
vllm serve meta-llama/Meta-Llama-3-8B-Instruct \
  --port 8000 \
  --host 0.0.0.0 \
  --gpu-memory-utilization 0.9 \
  --tensor-parallel-size 2     # 2 卡

# 监控
nvidia-smi -l 1     # 1 秒刷新
```

## 🔥 LoRA 微调 GPU 推荐

| 模型大小 | LoRA r | GPU |
|----------|---------|-----|
| 7B | 16 | RTX 4090 (24GB) |
| 13B | 16 | A100 40GB |
| 70B INT4 (QLoRA) | 16-32 | A100 80GB / H100 80GB |
| 70B FP16 | 16-32 | H100 80GB × 2 |

```bash
# QLoRA 70B（24GB 单卡）
pip install bitsandbytes

# 训练命令
accelerate launch --config_file deepspeed_zero3.yaml train.py
```

## 🛠 常见问题

```bash
# 1. CUDA OOM
# 解决：
#    - 减小 batch size
#    - 用 gradient accumulation
#    - 启用 gradient checkpointing
#    - 8-bit 优化器
#    - 量化模型（4-bit / 8-bit）

# 2. cuDNN 报错
pip install torch --upgrade --index-url https://download.pytorch.org/whl/cu121

# 3. NVIDIA 驱动装不上
sudo apt purge nvidia-*
sudo apt autoremove
sudo apt install nvidia-driver-550
sudo reboot

# 4. NVLink / 多卡通信慢
# 检查 nvidia-smi topo -m
```

## 🌐 云 GPU 选项

| 厂商 | 服务 | 特点 |
|------|------|------|
| AWS | EC2 P4d/P5 | 按小时，A100/H100 |
| GCP | Vertex AI / GKE | TPU 选项 |
| Azure | ND A100 | v5 替代 ND v2 |
| Lambda | Hyperplane GPU | 便宜 / 按秒 |
| RunPod | Serverless GPU | 灵活 |
| Vast.ai | Marketplace | 极便宜 |
| CoreWeave | GPU cloud | 训练首选 |

## 🛠 实战：LoRA 微调 7B 单卡 24GB

```bash
# 环境
pip install torch==2.5 transformers peft trl bitsandbytes

# 训练
python train.py \
  --model Qwen/Qwen2.5-7B \
  --lora-r 16 --lora-alpha 32 \
  --batch-size 2 --grad-accum 8 \
  --quantize nf4   # QLoRA 4-bit
```

## 🔗 下一步

- [pip / brew / npm 安装](/12-install/package-managers)
- [Docker 一键部署](/12-install/docker)
- [LoRA / QLoRA](/08-finetuning/lora)
- [vLLM / TGI 服务](/10-deploy/vllm-tgi)