// ===== 打卡树 · 前端与后端交互的公共方法 =====
// 前端和后端是同源(都由 FastAPI 提供)，所以这里不用配置跨域(CORS)

// 统一的请求函数：自动带上 token、解析 JSON、抛出后端的报错信息
async function api(path, { method = "GET", body, token } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["X-Auth-Token"] = token; // 后端从 X-Auth-Token 请求头读取登录凭证

  const res = await fetch(path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = {};
  try { data = await res.json(); } catch (e) { /* 后端可能返回空 */ }

  if (!res.ok) {
    // FastAPI 的报错通常在 detail 字段
    throw new Error(data.detail || `请求失败(${res.status})`);
  }
  return data;
}

// ---- token 存取：用户端与管理端用不同的 key，互不影响 ----
const TokenStore = {
  get(key) { return localStorage.getItem(key); },
  set(key, val) { localStorage.setItem(key, val); },
  clear(key) { localStorage.removeItem(key); },
};

// ---- 文件上传：打卡证据图片（multipart/form-data，不能用上面的 JSON 通道）----
async function uploadFile(file, token) {
  const form = new FormData();
  form.append("file", file);
  const headers = {};
  if (token) headers["X-Auth-Token"] = token;
  // 注意：FormData 不要手动设 Content-Type，浏览器会自动带 boundary
  const res = await fetch("/uploads/proof", { method: "POST", headers, body: form });
  let data = {};
  try { data = await res.json(); } catch (e) { /* 忽略空响应 */ }
  if (!res.ok) throw new Error(data.detail || `上传失败(${res.status})`);
  // data.data[0].url 为可访问的图片地址，存入 day_proof
  return data.data && data.data[0] ? data.data[0].url : null;
}

// ---- 打卡统计 ----
async function getStats(targetId, token) {
  return api(`/stats/target/${targetId}`, { token });
}

// ---- 轻提示 ----
function toast(msg) {
  let el = document.getElementById("toast");
  if (!el) {
    el = document.createElement("div");
    el.id = "toast";
    document.querySelector(".phone").appendChild(el);
  }
  el.textContent = msg;
  el.classList.add("show");
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove("show"), 2000);
}

// ---- 日期工具 ----
// 把 Date 转成 <input type="datetime-local"> 需要的字符串
function toLocalInput(d) {
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
}
// 把后端返回的时间字符串格式化成好看的样子
function fmt(s) {
  if (!s) return "—";
  return s.replace("T", " ").slice(0, 16);
}

const STATUS_TEXT = { pending: "待审核", approved: "已通过", rejected: "已驳回" };
