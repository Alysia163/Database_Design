# 学生成绩数据库系统

本项目包含两个版本：

- `score_management_web/`：Flask Web 版，作为主要演示版本。
- `main.py`：终端交互版，保留原有功能。

## Web 版启动

1. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

2. 在 MySQL 中导入数据库：

   ```bash
   mysql -u root -p < student_score_db.sql
   ```

3. 如本机 MySQL 密码不是 `AbcD@314159`，可通过环境变量配置：

   ```powershell
   $env:SCORE_DB_PASSWORD="你的MySQL密码"
   ```

   也可以在 `score_management_web/db_config.py` 中修改默认值。

4. 启动 Web 服务：

   ```bash
   cd score_management_web
   python app.py
   ```

5. 浏览器访问：

   ```text
   http://127.0.0.1:5000
   ```

## 默认账号

- 管理员：`admin1` / `admin1`
- 管理员：`admin2` / `123456`
- 学生：`2024001` / `123456`

## 本次优化重点

- Web 版数据库访问改为每个请求独立打开、提交/回滚并关闭连接，避免多次点击后连接占用导致页面卡住。
- 数据库连接增加 `connect_timeout`、`read_timeout`、`write_timeout`，MySQL 异常时会快速返回提示。
- Flask 启动关闭调试模式，避免异常进入调试阻塞页。
- 学生、课程删除时会先删除关联成绩，减少外键约束报错。
- 后台侧边栏空链接已改为真实功能页面链接。
