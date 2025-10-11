# 无头模式使用指南

## 什么是无头模式？

无头模式（Headless Mode）是指 Chrome 浏览器在后台运行，不显示任何窗口界面。这种模式特别适合：
- 🖥️ 在服务器上运行（无图形界面）
- 💻 在本地后台运行（节省资源）
- 🤖 自动化任务（无需人工干预）

## 使用方法

### 方法一：修改配置文件（推荐）

1. 编辑 `config.py`，设置：
```python
HEADLESS_MODE = True
```

2. 直接运行主程序：
```bash
python valuescan.py
```

### 方法二：使用专用启动脚本

```bash
python start_headless.py
```

## ⚠️ 重要注意事项

### 首次使用必须先登录

无头模式需要使用已登录的 Cookie，因此：

1. **首次使用前**，必须先用**有头模式**登录一次：
   ```bash
   # 确保 config.py 中 HEADLESS_MODE = False
   python start_with_chrome.py
   ```

2. 在打开的 Chrome 浏览器中：
   - 访问 valuescan.io
   - 登录你的账号
   - 确认能正常访问

3. 登录成功后，关闭程序（Ctrl+C）

4. **复制登录状态**到无头模式：
   ```bash
   # macOS/Linux
   cp -r chrome-debug-profile chrome-headless-profile
   
   # Windows
   xcopy chrome-debug-profile chrome-headless-profile /E /I
   ```

5. 现在可以切换到无头模式了：
   ```python
   # 修改 config.py
   HEADLESS_MODE = True
   ```

### 如果 Cookie 过期

如果运行时发现无法获取数据（可能是 Cookie 过期），需要：
1. 切回有头模式重新登录
2. 再次复制 profile 目录

## 两种模式对比

| 特性 | 有头模式 | 无头模式 |
|------|---------|----------|
| 显示浏览器窗口 | ✅ 是 | ❌ 否 |
| 资源占用 | 较高 | 较低 |
| 可以登录账号 | ✅ 是 | ❌ 否（需要已登录） |
| 适用场景 | 首次登录、调试 | 长期后台运行 |
| 服务器使用 | ❌ 需要图形界面 | ✅ 完美支持 |

## 故障排查

### 问题1：无法启动无头 Chrome
```
错误: 启动浏览器失败
```
**解决方案**：
- 确保已安装 Chrome 浏览器
- 检查是否有足够的系统权限
- 尝试重启电脑

### 问题2：无法获取 API 数据
```
未捕获到任何请求
```
**解决方案**：
- 可能是 Cookie 过期，需要重新登录
- 按照"首次使用必须先登录"步骤重新操作

### 问题3：内存占用过高
**解决方案**：
- 启用自动重启功能（config.py 中设置 `CHROME_AUTO_RESTART_HOURS = 3`）
- 定期重启程序

## 性能优化建议

1. **启用自动重启**：防止内存泄漏
   ```python
   CHROME_AUTO_RESTART_HOURS = 3  # 每3小时重启
   ```

2. **后台运行**（Linux/macOS）：
   ```bash
   nohup python valuescan.py > output.log 2>&1 &
   ```

3. **使用 systemd 守护进程**（Linux）：
   创建服务文件 `/etc/systemd/system/valuescan.service`

4. **查看日志**：
   ```bash
   tail -f valuescan.log
   ```

## 快速命令参考

```bash
# 有头模式 - 首次登录
python start_with_chrome.py

# 复制登录状态
cp -r chrome-debug-profile chrome-headless-profile

# 无头模式 - 后台运行
python start_headless.py

# 或者修改配置后运行
python valuescan.py
```
