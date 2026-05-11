# Doubao ASR STT (Home Assistant custom integration)

将 Home Assistant 的语音转文字（STT）连接到豆包输入法语音识别 HTTP 服务（[doubaoime-asr](https://github.com/yinghu183/doubaoime-asr)）。

## 功能

- 原生 Home Assistant **STT entity**
- 通过 UI 配置（Config Flow）
- 通过 HTTP POST 调用豆包 ASR 服务的 `/transcribe` 接口
- 支持 HACS 自定义仓库安装
- 兼容 HA 的 WAV 和原始 PCM 音频流

## 前置要求

- Home Assistant 2025.1+
- 已部署 [doubaoime-asr](https://github.com/yinghu183/doubaoime-asr) Docker 服务，且在局域网内可访问

## 部署 Doubao ASR 服务

在群晖 NAS 或任意 Docker 主机上：

```yaml
# docker-compose.yml
services:
  doubao-asr:
    image: ghcr.io/yinghu183/doubaoime-asr:latest
    container_name: doubao-asr
    ports:
      - "8181:8080"
    volumes:
      - ./credentials:/app/credentials
    restart: unless-stopped
```

```bash
docker compose up -d
```

## 通过 HACS 安装

1. HACS → 集成 → ⋮ → **自定义仓库**
2. 添加仓库 URL 并选择类型为 **集成**：
   `https://github.com/yinghu183/ha-funasr-ws-stt`
3. 安装 `Doubao ASR`
4. 重启 Home Assistant
5. 设置 → 设备与服务 → 添加集成 → 搜索 `Doubao ASR`

## 配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 名称 | Doubao ASR | 集成的显示名称 |
| 主机 | 192.168.1.50 | 豆包 ASR 服务 IP |
| 端口 | 8181 | 豆包 ASR 服务端口 |
| 超时 | 30 秒 | 请求超时时间 |

## 说明

- 语音识别实际由豆包云端完成，HA 和 NAS 都需要能访问外网
- 首次部署 doubao-asr 会自动注册设备并缓存凭据
- 该集成在 STT 被调用时才会发起网络请求，无额外的后台开销
