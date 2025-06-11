# 📥 Android Log Analyzer Windows版本下载说明

## 🎯 下载方式

### 方法1: GitHub Release（推荐）
1. 访问项目的GitHub Release页面：
   https://github.com/shixian64/test/releases/tag/v0.2.0-windows

2. 在Assets部分下载：
   - `AndroidLogAnalyzer_Windows_v0.2.0.zip` (6.6MB)

### 方法2: 手动构建
如果您想自己构建可执行文件：

```bash
# 1. 克隆仓库
git clone https://github.com/shixian64/test.git
cd test

# 2. 设置Python环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -e ".[dev]"
pip install pyinstaller

# 4. 运行构建脚本
chmod +x build_simple.sh
./build_simple.sh

# 5. 获取构建结果
# 可执行文件位于: AndroidLogAnalyzer_Windows/AndroidLogAnalyzer.exe
```

## 📦 包内容说明

下载的zip文件包含：

```
AndroidLogAnalyzer_Windows/
├── AndroidLogAnalyzer.exe     # 主可执行文件 (6.7MB)
├── README.md                  # 英文完整文档
├── README_zh-CN.md           # 中文完整文档
├── USAGE.md                  # 快速使用指南
├── analyze_log.bat           # Windows批处理辅助工具
└── sample.log                # 示例日志文件（用于测试）
```

## 🚀 安装和使用

### 安装步骤
1. 下载 `AndroidLogAnalyzer_Windows_v0.2.0.zip`
2. 解压到任意目录（如 `C:\Tools\AndroidLogAnalyzer\`）
3. 无需其他安装步骤

### 使用方法

#### GUI模式（图形界面）
```
双击 AndroidLogAnalyzer.exe
```

#### 命令行模式
```cmd
# 进入解压目录
cd C:\Tools\AndroidLogAnalyzer

# 分析日志文件
AndroidLogAnalyzer.exe your_log_file.log

# 使用批处理文件
analyze_log.bat your_log_file.log

# 测试示例
AndroidLogAnalyzer.exe sample.log
```

## ✅ 系统要求

- **操作系统**: Windows 7/8/10/11 (64位)
- **内存**: 最少512MB可用内存
- **磁盘**: 至少50MB可用空间
- **依赖**: 无需安装Python或其他软件

## 🔍 功能验证

下载后可以使用示例文件测试：

```cmd
AndroidLogAnalyzer.exe sample.log
```

预期输出：
```
Log Analysis Report
===================
Summary:
  Java Crashes: 1
  ANRs: 3
  Native Crash Hints: 3
  System Errors: 5
  Memory Issues: 1
===================
```

## 🛠️ 故障排除

### 常见问题

**Q: 提示"无法运行此应用"**
A: 确保系统是64位Windows，右键选择"以管理员身份运行"

**Q: 杀毒软件报警**
A: 这是误报，可以添加到白名单。程序是开源的，完全安全

**Q: 程序无响应**
A: 对于大文件分析可能需要时间，请耐心等待

**Q: 找不到日志文件**
A: 确保文件路径正确，支持相对路径和绝对路径

### 获取帮助
```cmd
AndroidLogAnalyzer.exe --help
```

## 📞 技术支持

- **项目主页**: https://github.com/shixian64/test
- **问题反馈**: https://github.com/shixian64/test/issues
- **使用文档**: 查看包内README.md获取详细信息

## 🔄 版本信息

- **当前版本**: v0.2.0
- **发布日期**: 2024-06-11
- **文件大小**: 6.6MB (压缩包)
- **可执行文件**: 6.7MB

## 📋 更新检查

定期访问GitHub Release页面检查新版本：
https://github.com/shixian64/test/releases

## 🙏 反馈建议

如果您在使用过程中遇到问题或有改进建议，欢迎：

1. 在GitHub上提交Issue
2. 提供具体的日志文件样本（如果涉及分析问题）
3. 描述您的使用场景和期望功能

---

**🎉 感谢使用Android Log Analyzer！让Android日志分析变得简单高效！**
