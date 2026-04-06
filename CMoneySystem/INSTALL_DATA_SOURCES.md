# 📦 数据源依赖安装指南

由于环境限制，请手动执行以下命令来安装数据源依赖。

## 方法 1：使用安装脚本（推荐）

```bash
cd /storage/emulated/0/Download/CMoney/CMoneySystem

# 给脚本执行权限
chmod +x install_data_sources.sh

# 运行安装脚本
bash install_data_sources.sh
```

## 方法 2：手动安装（如果脚本失败）

```bash
# 1. 安装 AkShare（主要数据源）
pip install akshare

# 2. 安装数据处理库
pip install pandas numpy

# 3. 安装网络请求库（通常已安装）
pip install requests

# 4. 一次性安装所有依赖
pip install akshare pandas numpy requests
```

## 方法 3：使用 requirements.txt

```bash
cd /storage/emulated/0/Download/CMoney/CMoneySystem

# 安装所有依赖
pip install -r requirements.txt
```

---

## 验证安装

安装完成后，运行以下命令验证：

```bash
python3 -c "import akshare; print('AkShare 版本:', akshare.__version__)"
python3 -c "import pandas; print('Pandas 版本:', pandas.__version__)"
python3 -c "import numpy; print('NumPy 版本:', numpy.__version__)"
python3 -c "import requests; print('Requests 版本:', requests.__version__)"
```

预期输出：
```
AkShare 版本: 1.12.+
Pandas 版本: 2.+
NumPy 版本: 1.+
Requests 版本: 2.+
```

---

## 测试数据源

依赖安装成功后，运行测试脚本：

```bash
python3 test_data_sources.py
```

---

## 常见问题

### Q1: pip 安装速度慢？

**A**: 使用国内镜像源
```bash
pip install akshare -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: 权限错误？

**A**: 使用 --user 参数
```bash
pip install --user akshare pandas numpy
```

### Q3: 网络连接失败？

**A**: 尝试：
1. 检查网络连接
2. 使用 VPN 或代理
3. 等待几分钟后重试

### Q4: 内存不足？

**A**: Termux 环境可以尝试：
```bash
# 清理 pip 缓存
pip cache purge

# 然后重新安装
pip install akshare
```

---

## 安装后的下一步

1. ✅ 验证安装成功
2. ✅ 运行 `python3 test_data_sources.py` 测试数据源
3. ✅ 启动后端：`python3 main.py`
4. ✅ 启动前端：`cd frontend && npm run dev`
5. ✅ 访问系统：http://localhost:5173

---

## 最低要求

| 包名 | 版本 | 必需性 |
|------|------|--------|
| Python | 3.7+ | 必需 |
| Flask | 2.0+ | 必需 |
| AkShare | 1.10+ | 推荐（真实数据） |
| Pandas | 1.3+ | 推荐（数据处理） |
| NumPy | 1.20+ | 推荐（数值计算） |
| Requests | 2.25+ | 必需（网络请求） |

---

## 注意事项

⚠️ **安装时间**：首次安装 AkShare 可能需要 3-5 分钟

⚠️ **网络要求**：需要稳定的网络连接

⚠️ **磁盘空间**：约需要 200MB 空间

⚠️ **Python 版本**：确保使用 Python 3.7 或更高版本

---

**安装完成后，系统就可以获取真实的股票数据了！** 🎉
