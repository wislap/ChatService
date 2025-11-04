# ChatService
> 一个多功能校园应用，目前具有表白墙功能，更多功能仍在开发中

##  技术架构

后端 (FastAPI)
前端 (Vue 3)
##  快速开始

### 环境要求
- **Node.js**: ^20.19.0 || >=22.12.0
- **Python**: 3.8+
- **包管理器**: npm 或 yarn

### 1. 克隆项目
```bash
git clone https://github.com/wislap/ChatService.git
cd ChatService
```
### 2. 后端设置
```bash
cd server

# 安装Python依赖
pip install -r requirements.txt
# 或者使用uv（推荐）
uv sync

# 初始化数据库
python db/create_db.py

# 启动后端
python main.py
```
后端服务将在 `http://127.0.0.1:25578` 启动

### 3. 前端设置
```bash
cd client-vue

# 安装依赖
npm install

# 启动测试服务器
npm run dev
```
前端应用将在 `http://localhost:5173` 启动

### 4. 访问应用
 `http://localhost:5173`

## 开发顺序 
> 1. 前后端的配置文件 包括前后端的ip配置，密钥等
> 2. 博客功能
