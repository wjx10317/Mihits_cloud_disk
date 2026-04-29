# Mihits 网盘客户端

桌面端网盘应用，基于 Electron + Vue 3 + FastAPI。

## 技术栈

- **前端**：Vue 3 + Element Plus + Pinia + TypeScript
- **桌面**：Electron (electron-vite)
- **后端**：FastAPI + SQLAlchemy 2.0 + PostgreSQL
- **存储**：MinIO (S3 兼容对象存储)

## 项目结构

```
Mihits_wangpan/
├── client/          # Electron + Vue 3 前端
├── server/          # FastAPI 后端
└── docs/            # 设计文档与开发计划
```

## 开发

详见 `docs/plans/` 目录下的设计文档。

### 后端启动

```bash
cd server
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端启动

```bash
cd client
npm install
npm run dev
```
