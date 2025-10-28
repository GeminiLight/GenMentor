使用说明：同时启动前端和后端

文件：
- `start_all.sh`：在仓库根目录运行，启动 `backend/main.py` 和 `frontend/main.py`，日志写入 `logs/`，PID 写入 `start_all.pids`。
- `stop_all.sh`：停止 `start_all.pids` 中记录的进程并删除该文件。

示例：
1. 赋予可执行权限（只需做一次）：
   chmod +x start_all.sh stop_all.sh

2. 启动服务：
   ./start_all.sh

   启动后可在 `logs/` 里查看 `backend.log` 和 `frontend.log`，PID 列表在 `start_all.pids`。

3. 停止服务：
   ./stop_all.sh

注意事项：
- 脚本使用 `python3`（从 PATH 启动），如果需要使用虚拟环境，请修改脚本中 `python3` 的路径或在运行前激活虚拟环境。
- 若前端或后端需要监听特定端口，确保端口未被占用。
