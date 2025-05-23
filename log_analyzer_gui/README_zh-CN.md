# Android 日志分析器 GUI

一个用户友好的 Android 日志分析器图形界面工具，基于 Electron 和 Python (使用 Eel 库) 构建。此应用程序允许用户轻松选择 Android 日志文件，分析常见问题，并以结构化格式查看结果。

## 功能特性

*   **图形用户界面:** 易于使用的界面，用于选择日志文件和查看分析结果。
*   **核心分析引擎:** 利用与[命令行版本](../android_log_analyzer/README.md)相同的强大 Python 分析逻辑，可检测：
    *   Java 崩溃
    *   应用程序无响应 (ANR) 错误
    *   Native Crash (原生崩溃) 提示
    *   Kernel Panic (内核崩溃)、Watchdog (看门狗) 重置以及其他严重系统错误
*   **结构化结果显示:**
    *   检测到的问题类型的摘要计数。
    *   所有已发现问题的详细、可筛选列表。
    *   一个模态框视图，用于检查每个特定问题的完整详细信息。
*   **跨平台:** 设计用于打包成 Linux (AppImage, .deb) 和 Windows (.exe) 应用。*(构建版本应经过验证)*

## 屏幕截图

*(占位符：待应用程序可用后在此处添加屏幕截图。)*

1.  **主应用程序窗口 (文件选择):**
    *   *(描述：显示用于选择日志文件的初始视图。)*
    *   `[Screenshot_Main_Window.png]`

2.  **分析结果视图 (摘要和表格):**
    *   *(描述：显示包含摘要统计信息和检测到的问题表格的结果屏幕。)*
    *   `[Screenshot_Results_View.png]`

3.  **问题详情模态框:**
    *   *(描述：显示包含所选问题完整详细信息的模态对话框。)*
    *   `[Screenshot_Detail_Modal.png]`

## 系统要求

### 使用已打包的应用程序
*   **Linux:** AppImage 或 .deb 包。无需外部依赖。
*   **Windows:** NSIS 安装程序 (.exe)。无需外部依赖。
    *(注意：请从项目的 Releases 页面下载软件包 - 此处应有链接。)*

### 从源码运行 (开发环境)
*   Python 3.7+
    *   `eel` 库 (`pip install eel`)
*   Node.js (包含 npm)，推荐 LTS 版本。
*   对核心 `android_log_analyzer` 模块的访问权限 (预期位于同级目录 `../android_log_analyzer` 中)。

## 安装与使用

### 使用已打包的应用程序
1.  从项目的 releases 页面下载适用于您系统的软件包 (例如, Linux 的 `.AppImage`，Windows 的 `.exe` 安装程序)。
2.  **Linux (AppImage):**
    *   使 AppImage 可执行：`chmod +x Android_Log_Analyzer_GUI-x.y.z.AppImage`
    *   运行它：`./Android_Log_Analyzer_GUI-x.y.z.AppImage`
3.  **Windows (安装程序):**
    *   运行 `.exe` 安装程序并按照屏幕上的说明操作。
    *   从开始菜单或桌面快捷方式启动应用程序。

### 从源码运行 (开发环境)
1.  **克隆仓库 (或确保您同时拥有 `log_analyzer_gui` 和 `android_log_analyzer` 目录)。**
    ```bash
    # git clone ... (如果这是一个 git 仓库)
    # 确保两个项目文件夹都存在。
    ```
2.  **导航到 GUI 项目目录：**
    ```bash
    cd path/to/log_analyzer_gui
    ```
3.  **安装 Node.js 依赖：**
    ```bash
    npm install
    ```
4.  **安装 Python 依赖：**
    ```bash
    pip install eel
    ```
5.  **运行应用程序：**
    ```bash
    npm start
    ```
    这将启动 Electron 应用程序。Python Eel 服务器将由 Electron 主进程自动启动。

## 从源码构建

要创建可分发的软件包 (AppImage, deb, exe)，请使用 `electron-builder`。

1.  确保所有开发依赖都已安装 (`npm install`)。
2.  从 `log_analyzer_gui` 目录运行构建命令：
    ```bash
    npm run build
    ```
3.  打包好的应用程序将位于 `log_analyzer_gui/dist` 目录中。

## 项目结构 (关键文件)

*   `log_analyzer_gui/`: GUI 应用程序的根目录。
    *   `main_gui.py`: Python 后端脚本，使用 Eel 连接 JavaScript 和核心分析器。
    *   `electron_bootstrap.js`: Electron 主进程脚本，创建浏览器窗口并管理 Python 子进程。
    *   `package.json`: 定义 Node.js 依赖、脚本 (start, build) 和 `electron-builder` 配置。
    *   `web/`: 包含前端文件 (HTML, CSS, JavaScript)。
        *   `main.html`: UI 的主 HTML 页面。
        *   `script.js`: 前端 JavaScript 逻辑。
        *   `style.css`: CSS 样式。
    *   `build_assets/`: 包含用于打包的图标等资源。
*   `../android_log_analyzer/`: (假定的同级目录) 包含核心 Python 日志分析逻辑。
    *   `log_analyzer.py`: 解析和分析日志的主要脚本。
    *   `__init__.py`: 使此目录成为一个 Python 包。
```
