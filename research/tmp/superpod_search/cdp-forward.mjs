// WSL2 -> Windows Chrome CDP 端口转发
// 将 WSL 内 127.0.0.1:9222 转发到 Windows 宿主机 172.30.128.1:9222
// （前提：Windows 侧已用 netsh portproxy 将 9222 暴露到 0.0.0.0）
import net from 'node:net';

const WIN_HOST = process.argv[2] || '172.30.128.1';
const PORT = 9222;

const server = net.createServer((local) => {
  const remote = net.connect({ host: WIN_HOST, port: PORT }, () => {
    console.log(`[forward] 新连接 -> ${WIN_HOST}:${PORT}`);
  });
  local.pipe(remote);
  remote.pipe(local);
  local.on('error', () => remote.destroy());
  remote.on('error', () => local.destroy());
  local.on('close', () => remote.destroy());
  remote.on('close', () => local.destroy());
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[forward] 127.0.0.1:${PORT} -> ${WIN_HOST}:${PORT} 已启动`);
});
