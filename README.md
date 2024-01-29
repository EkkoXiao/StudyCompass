## 人机交互理论与技术小组项目
   
### 环境配置

要求 `python=3.10` 创建环境，运行

```
pip install -r requirements.txt
```

可能出现 `fitz` 库 `No module named "frontend"` 报错，需要删除 `pymupdf` 库重装（原因未知）

### 运行应用

**建议仅使用 Windows 系统进行测试，MacOS 等系统可能遇到字体不支持无法显示等情况，且无法启用联网搜索**

在根目录下执行 `python ./src/app.py` 即可运行应用。

当前仓库为仅支持前端效果展示版本，不支持文件的上传和生成操作。

实时问答系统因 `openai-api-key` 已过期无法使用。
