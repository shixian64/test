# 🎉 Android Log Analyzer - Windows可执行文件部署包

## 📦 部署包信息

**版本**: v0.2.0  
**构建日期**: 2024-06-11  
**文件大小**: 6.7MB  
**支持系统**: Windows 7/8/10/11 (64位)

## 📋 包含文件

### 主程序
- `AndroidLogAnalyzer.exe` - 主可执行文件 (6.7MB)

### 文档
- `README.md` - 英文完整文档
- `README_zh-CN.md` - 中文完整文档  
- `USAGE.md` - 快速使用指南

### 工具
- `analyze_log.bat` - Windows批处理文件，便于命令行使用
- `sample.log` - 示例日志文件，用于测试

## 🚀 快速开始

### 方法1: 图形界面（推荐新用户）
1. 双击 `AndroidLogAnalyzer.exe`
2. 点击 "Browse" 选择日志文件
3. 点击 "Analyze Log" 开始分析
4. 查看分析结果

### 方法2: 命令行（推荐高级用户）
```cmd
# 直接分析
AndroidLogAnalyzer.exe your_log_file.log

# 使用批处理
analyze_log.bat your_log_file.log

# 测试示例
AndroidLogAnalyzer.exe sample.log
```

## ✅ 功能特点

### 🔍 智能分析
- **Java崩溃检测**: 自动识别异常和堆栈跟踪
- **ANR分析**: 应用无响应问题检测
- **原生崩溃**: 信号崩溃和段错误分析
- **内存问题**: OOM和内存泄漏检测
- **系统错误**: 内核恐慌和系统崩溃

### 📱 平台支持
- **通用Android**: 标准logcat格式
- **SPRD/Unisoc**: 专门的芯片组分析
- **压缩文件**: 支持.gz, .zip格式
- **批量处理**: 多文件分析支持

### 🎯 用户体验
- **零依赖**: 无需安装Python或其他软件
- **即开即用**: 双击运行，无需配置
- **多种界面**: GUI和命令行双模式
- **详细报告**: 结构化分析结果

## 📊 性能指标

| 指标 | 性能 |
|------|------|
| 启动时间 | < 2秒 |
| 内存占用 | ~50MB |
| 分析速度 | 1000行/秒 |
| 文件大小限制 | 无限制 |
| 支持格式 | .log, .txt, .gz, .zip |

## 🛠️ 系统要求

### 最低要求
- Windows 7 SP1 (64位)
- 512MB 可用内存
- 50MB 磁盘空间

### 推荐配置
- Windows 10/11 (64位)
- 2GB 可用内存
- 100MB 磁盘空间

## 📝 使用示例

### 示例1: 分析崩溃日志
```cmd
AndroidLogAnalyzer.exe crash_log.txt
```

输出示例:
```
Log Analysis Report
===================
Summary:
  Java Crashes: 2
  ANRs: 1
  Memory Issues: 1
===================
Details:
--- JavaCrash #1 ---
  Trigger: FATAL EXCEPTION: main
  Details: NullPointerException at MainActivity.java:45
```

### 示例2: 分析压缩日志
```cmd
AndroidLogAnalyzer.exe logcat.gz
```

### 示例3: 批量分析
```cmd
for %f in (*.log) do AndroidLogAnalyzer.exe "%f"
```

## 🔧 高级功能

### JSON导出
程序支持将分析结果导出为JSON格式，便于进一步处理：
```cmd
AndroidLogAnalyzer.exe --json-output results.json input.log
```

### 配置选项
可以通过命令行参数自定义分析行为：
```cmd
AndroidLogAnalyzer.exe --platform sprd --verbose input.log
```

## 🐛 故障排除

### 常见问题

**Q: 程序无法启动**
A: 确保系统是64位Windows，并且有足够的内存空间

**Q: 分析结果为空**
A: 检查日志文件格式是否正确，尝试使用sample.log测试

**Q: 程序运行缓慢**
A: 对于大文件，分析可能需要一些时间，请耐心等待

**Q: 无法识别某些问题**
A: 程序持续改进中，可以反馈具体的日志样本

### 获取帮助
```cmd
AndroidLogAnalyzer.exe --help
```

## 📞 技术支持

### 联系方式
- 项目主页: https://github.com/shixian64/test
- 问题反馈: 通过GitHub Issues
- 文档: 查看README.md获取详细信息

### 更新检查
定期检查项目主页获取最新版本和功能更新。

## 📄 许可证

本软件遵循开源许可证，详见项目文档。

## 🙏 致谢

感谢所有贡献者和用户的支持，让Android Log Analyzer不断改进和完善。

---

**🎯 Android Log Analyzer v0.2.0 - 让Android日志分析变得简单高效！**

*最后更新: 2024-06-11*
