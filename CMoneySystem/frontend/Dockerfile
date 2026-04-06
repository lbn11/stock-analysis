# 多阶段构建 - 前端 React 应用
FROM node:20-alpine as base

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY package*.json ./
RUN npm ci

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 5173

# 开发环境
FROM base as development
ENV VITE_MODE=development
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# 生产构建
FROM node:20-alpine as build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 生产环境（使用 nginx 提供静态文件）
FROM nginx:alpine as production
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
