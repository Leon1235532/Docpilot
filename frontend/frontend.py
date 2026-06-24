import streamlit as st
import requests
import base64
from pathlib import Path
import os

# ── Helper: 将本地图片转为 base64（用于嵌入 HTML）──
def get_base64_of_bin_file(bin_file: str) -> str:
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ── Configuration ──
BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="DocPilot 智能文档助手", layout="wide")

# 💡 UI 优化：强行压缩 Streamlit 默认的顶部大白边
# ==========================================
st.markdown("""
    <style>
    /* 将主容器的顶部间距从默认的 6rem 压缩到 2rem */
    .block-container {
        padding-top: 2rem !important; 
    }
    </style>
""", unsafe_allow_html=True)

# ── Session state initialisation ──
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "show_login_toast" not in st.session_state:
    st.session_state.show_login_toast = False
if "summary_content" not in st.session_state:
    st.session_state.summary_content = None
if "editing_doc" not in st.session_state:
    st.session_state.editing_doc = None
if "current_doc_id" not in st.session_state:
    st.session_state.current_doc_id = None
if "doc_created_msg" not in st.session_state:
    st.session_state.doc_created_msg = None


# ── Helper: build dynamic auth headers ──
def auth_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


# ── Load documents from backend ──
def load_documents():
    try:
        resp = requests.get(
            f"{BASE_URL}/docs/get_all",
            params={"page": 1, "page_size": 50},
            headers=auth_headers(),
            timeout=30,
        )
        result = resp.json()
        if result.get("data") is not None:
            return result["data"]
        return []
    except Exception:
        return []


# ── Sidebar ──
with st.sidebar:
    st.markdown("### 🧠 DocPilot")
    st.markdown("智能文档助手")
    st.divider()

    # ── Login / User panel ──
    if st.session_state.token is None:
        # ── 登录 / 注册 页签 ──
        tab_login, tab_register = st.tabs(["🔐 登录", "📝 注册"])

        with tab_login:
            login_username = st.text_input("用户名", key="login_user")
            login_password = st.text_input("密码", type="password", key="login_pass")

            if st.button("登录", use_container_width=True):
                if not login_username or not login_password:
                    st.warning("请填写用户名和密码")
                else:
                    with st.spinner("登录中..."):
                        try:
                            resp = requests.post(
                                f"{BASE_URL}/auth/login",
                                data={"username": login_username, "password": login_password},
                                timeout=30,
                            )
                            result = resp.json()
                        except Exception as e:
                            st.error(f"登录请求失败：{e}")
                            st.stop()

                    if resp.status_code == 200 and result.get("access_token"):
                        st.session_state.token = result["access_token"]
                        st.session_state.username = login_username
                        st.session_state.show_login_toast = True
                        st.rerun()
                    else:
                        st.error(result.get("detail", "登录失败，请检查用户名和密码"))

        with tab_register:
            reg_username = st.text_input("用户名", key="reg_user")
            reg_password = st.text_input("密码", type="password", key="reg_pass")

            if st.button("注册账号", use_container_width=True):
                if not reg_username or not reg_password:
                    st.warning("请填写用户名和密码")
                else:
                    with st.spinner("注册中..."):
                        try:
                            resp = requests.post(
                                f"{BASE_URL}/auth/register",
                                json={"username": reg_username, "password": reg_password},
                                timeout=30,
                            )
                            result = resp.json()
                        except Exception as e:
                            st.error(f"注册请求失败：{e}")
                            st.stop()

                    if resp.status_code == 200 or result.get("code") == 200:
                        st.success("注册成功，请切换至登录页签进行登录")
                    else:
                        st.error(result.get("detail", result.get("message", "注册失败")))
    else:
        # ── 已登录面板 ──
        st.markdown(f"👋 欢迎, **{st.session_state.username}**")
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.chat_history = []
            st.rerun()

        with st.expander("🔑 修改密码"):
            ori_pwd = st.text_input("原密码", type="password", key="ori_pwd")
            new_pwd = st.text_input("新密码", type="password", key="new_pwd")

            if st.button("确认修改", use_container_width=True):
                if not ori_pwd or not new_pwd:
                    st.warning("请填写原密码和新密码")
                else:
                    with st.spinner("修改中..."):
                        try:
                            resp = requests.put(
                                f"{BASE_URL}/auth/modify",
                                json={"ori_pwd": ori_pwd, "new_pwd": new_pwd},
                                headers=auth_headers(),
                                timeout=30,
                            )
                            result = resp.json()
                        except Exception as e:
                            st.error(f"修改密码请求失败：{e}")
                            st.stop()

                    if resp.status_code == 200 or result.get("code") == 200:
                        st.success("密码修改成功，请重新登录")
                        st.session_state.token = None
                        st.session_state.username = None
                        st.session_state.chat_history = []
                        st.rerun()
                    else:
                        st.error(result.get("detail", result.get("message", "修改失败")))

        with st.expander("⚠️ 注销账号"):
            st.error("注销操作不可逆，此操作将永久删除您的账号及所有云端文档数据，是否继续？")
            delete_pwd = st.text_input("请输入当前密码确认注销", type="password", key="delete_pwd")

            if st.button("🚨 确认永久注销", use_container_width=True):
                if not delete_pwd:
                    st.warning("请输入密码")
                else:
                    with st.spinner("注销中..."):
                        try:
                            resp = requests.post(
                                f"{BASE_URL}/auth/close",
                                json={"pwd": delete_pwd},
                                headers=auth_headers(),
                                timeout=30,
                            )
                            result = resp.json()
                        except Exception as e:
                            st.error(f"注销请求失败：{e}")
                            st.stop()

                    if resp.status_code == 200:
                        st.success("注销成功！")
                        st.session_state.token = None
                        st.session_state.username = None
                        st.session_state.chat_history = []
                        st.session_state.editing_doc = None
                        st.session_state.current_doc_id = None
                        st.rerun()
                    else:
                        st.error(result.get("detail", result.get("message", "注销失败")))

        st.divider()

        # ── 文件上传与入库（仅登录后可见）──
        uploaded_file = st.file_uploader(
            "上传心脏外科护理 PDF 文档",
            type=["pdf"],
        )

        if st.button("开始入库", use_container_width=True):
            if uploaded_file is None:
                st.warning("请先选择一个 PDF 文件")
            else:
                with st.spinner("医疗文档切片入库中，请稍候..."):
                    try:
                        resp = requests.post(
                            f"{BASE_URL}/input/upload",
                            files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                            headers=auth_headers(),
                            timeout=120,
                        )
                        data = resp.json()
                    except Exception as e:
                        st.error(f"请求失败：{e}")
                        st.stop()

                if data.get("code") == 200:
                    chunks = data.get("chunks_saved", 0)
                    st.success(f"文档处理成功！已为您成功切片保存 {chunks} 个知识库分块。")
                else:
                    st.error(data.get("message", "未知错误"))

        st.divider()

        # ── ➕ 新建在线文档 ──
        with st.expander("➕ 新建在线文档"):
            new_title = st.text_input("文档标题", key="new_doc_title")
            new_content = st.text_area("文档内容", height=150, key="new_doc_content")

            if st.button("确认创建", use_container_width=True):
                if not new_title:
                    st.warning("请输入文档标题")
                else:
                    with st.spinner("创建中..."):
                        try:
                            resp = requests.post(
                                f"{BASE_URL}/docs/create",
                                json={"title": new_title, "content": new_content},
                                headers=auth_headers(),
                                timeout=30,
                            )
                            data = resp.json()
                        except Exception as e:
                            st.error(f"请求失败：{e}")
                            st.stop()

                    if resp.status_code in (200, 201):
                        st.session_state.doc_created_msg = f"✅ 文档「{new_title}」创建成功！"
                        st.rerun()
                    else:
                        detail = data.get("detail", data.get("message", "未知错误"))
                        st.error(f"创建失败：{detail}")

        # ── 📚 我的私人图书馆 ──
        st.markdown("#### 📚 我的私人图书馆")
        docs = load_documents()
        if docs:
            doc_titles = [doc.get("title", f"文档 {doc.get('id', '')}") for doc in docs]
            title_to_id = {doc.get("title", f"文档 {doc.get('id', '')}"): doc.get("id") for doc in docs}
            selected_title = st.selectbox("选择文档", doc_titles, key="doc_selector")

            if selected_title:
                selected_doc_id = title_to_id.get(selected_title)
                st.session_state.current_doc_id = selected_doc_id
                col_summary, col_edit, col_delete = st.columns(3)
                with col_summary:
                    if st.button("✨", help="AI 一键生成摘要", use_container_width=True):
                        with st.spinner("生成总结中..."):
                            try:
                                resp = requests.post(
                                    f"{BASE_URL}/docs/ai_Summary",
                                    params={"doc_id": selected_doc_id},
                                    headers=auth_headers(),
                                    timeout=60,
                                )
                                result = resp.json()
                                if result.get("summary"):
                                    st.session_state.summary_content = result["summary"]
                                    st.rerun()
                                else:
                                    st.error("总结生成失败")
                            except Exception as e:
                                st.error(f"请求失败：{e}")
                with col_edit:
                    if st.button("📖", help="查看与编辑文档", use_container_width=True):
                        with st.spinner("加载文档中..."):
                            try:
                                resp = requests.get(
                                    f"{BASE_URL}/docs/get_single",
                                    params={"doc_id": selected_doc_id},
                                    headers=auth_headers(),
                                    timeout=30,
                                )
                                doc_data = resp.json()
                                if doc_data.get("id") or doc_data.get("title"):
                                    st.session_state.editing_doc = doc_data
                                    st.rerun()
                                else:
                                    st.error("获取文档失败")
                            except Exception as e:
                                st.error(f"请求失败：{e}")
                with col_delete:
                    if st.button("🗑️", help="永久删除此文档", use_container_width=True):
                        with st.spinner("删除中..."):
                            try:
                                resp = requests.delete(
                                    f"{BASE_URL}/docs/delete",
                                    params={"doc_id": selected_doc_id},
                                    headers=auth_headers(),
                                    timeout=30,
                                )
                                if resp.status_code == 204:
                                    st.toast("文档已成功从云端知识库移除", icon="🗑️")
                                    st.rerun()
                                else:
                                    st.error("删除失败")
                            except Exception as e:
                                st.error(f"请求失败：{e}")
        else:
            st.info("暂无上传的文档")


# ── Main page ──
st.title("📄 DocPilot 智能文档助手")

# ── 跨 rerun 的登录 toast ──
if st.session_state.show_login_toast:
    st.toast(f"🎉 欢迎登录，{st.session_state.username}！", icon="👋")
    st.session_state.show_login_toast = False

# ── 跨 rerun 的文档创建成功提示 ──
if st.session_state.doc_created_msg:
    st.toast(st.session_state.doc_created_msg, icon="✅")
    st.session_state.doc_created_msg = None

if st.session_state.token is None:
    # ── Landing Page（未登录状态）──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>欢迎使用 DocPilot 智能文档助手 👋</h3>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color:#888; font-size:0.9rem;'>"
        "基于大语言模型与 RAG 技术的专科文献知识库与智能问答平台。</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            "##### &emsp;&emsp;&emsp;&emsp;🏥 专科知识沉淀\n\n"
            "支持 PDF 文献的极速切片入库，打造专属知识体系。"
        )
        st.info("上传即可自动解析、切片、向量化，构建您的私有知识库。")

    with col2:
        st.markdown(
            "##### &emsp;&emsp;&emsp;&emsp;🤖 &nbsp; 智能文献问答\n\n"
            "基于上下文的精准检索，结构化提取临床表现与护理措施。"
        )
        st.info("深度语义匹配，让每一份文献的价值被充分释放。")

    with col3:
        st.markdown(
            "##### &emsp;&emsp;&emsp;&emsp;⚡️一键核心摘要\n\n"
            "长篇文献一键生成 AI 总结，大幅提升科研效率。"
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("告别逐页阅读，核心信息尽收眼底。")

    st.divider()
    st.success("👈 请在左侧边栏登录或注册，开启您的智能科研之旅。")
else:
    # ── 已登录：显示聊天历史与输入框 ──

    # ── 文档编辑工作台 ──
    if st.session_state.editing_doc:
        doc = st.session_state.editing_doc
        with st.container():
            st.subheader("📝 文档详情与编辑")
            edit_title = st.text_input("文档标题", value=doc.get("title", ""))
            edit_content = st.text_area("文档内容", value=doc.get("content", ""), height=300)
            col_save, col_close = st.columns(2)
            with col_save:
                if st.button("💾 保存修改", use_container_width=True):
                    doc_id = doc.get("id")
                    if not doc_id:
                        st.error("文档 ID 缺失")
                    else:
                        with st.spinner("保存中..."):
                            try:
                                resp = requests.patch(
                                    f"{BASE_URL}/docs/update",
                                    params={"doc_id": doc_id},
                                    json={"title": edit_title, "content": edit_content},
                                    headers=auth_headers(),
                                    timeout=30,
                                )
                                if resp.status_code == 200 or resp.status_code == 204:
                                    st.toast("文档保存成功", icon="💾")
                                    st.session_state.editing_doc = None
                                    st.rerun()
                                else:
                                    st.error("保存失败")
                            except Exception as e:
                                st.error(f"请求失败：{e}")
            with col_close:
                if st.button("❌ 关闭编辑", use_container_width=True):
                    st.session_state.editing_doc = None
                    st.rerun()
        st.divider()

    # ── Chat input（放在显示前，但输入框自动渲染在页面底部）──
    prompt = st.chat_input("请输入你的文档需求…")
    if prompt:
        # 先写入用户消息到历史
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 防呆检查
        if not st.session_state.get("current_doc_id"):
            st.warning("请先在左侧选择一篇专属文献，再开始对话！")
            st.stop()

        # AI 思考与回复
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    resp = requests.post(
                        f"{BASE_URL}/input/ask",
                        json={"question": prompt, "doc_id": st.session_state.current_doc_id},
                        headers=auth_headers(),
                        timeout=60,
                    )
                    result = resp.json()
                except Exception as e:
                    st.error(f"请求失败：{e}")
                    st.stop()

            if result.get("code") == 200:
                payload = result.get("data", {})
                ui_type = payload.get("ui_type", "medical_card")

                if ui_type == "normal_chat":
                    content = payload.get("content", "抱歉，我没有听懂。")
                    st.markdown(content)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "ui_type": "normal_chat", "content": content}
                    )
                else:
                    medical_data = payload.get("data", {})
                    core_conclusion = medical_data.get("core_conclusion", "暂无结论")
                    key_details = medical_data.get("key_details", [])
                    warnings_or_notes = medical_data.get("warnings_or_notes", [])

                    st.success(f"💡 {core_conclusion}")
                    col_left, col_right = st.columns(2)
                    with col_left:
                        st.subheader("📝 详细解析")
                        if key_details:
                            for item in key_details:
                                st.markdown(f"- ✅ {item}")
                        else:
                            st.info("暂无数据")
                    with col_right:
                        st.subheader("⚠️ 注意事项与预警")
                        if warnings_or_notes:
                            for item in warnings_or_notes:
                                st.markdown(f"- 🚨 {item}")
                        else:
                            st.info("无特殊注意事项")

                    st.session_state.chat_history.append(
                        {"role": "assistant", "ui_type": "medical_card", "data": medical_data}
                    )
            else:
                err_msg = result.get("message", "后端返回错误")
                st.error(err_msg)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": f"❌ {err_msg}"}
                )

        st.rerun()

    # ── Display chat history
    if len(st.session_state.chat_history) == 0:
        # ── 空状态：显示欢迎语 + GIF ──
        try:
            gif_base64 = get_base64_of_bin_file("welcome.gif")
            img_html = img_html = f'<img src="data:image/gif;base64,{gif_base64}" style="display: block; margin: 15px auto 0 auto; width: 160px; height: auto;">'
        except Exception:
            img_html = ""

        st.markdown(
            f"""<div style="text-align: center; margin-top: 2.5vh; color: #555;">
<h1 style="font-weight: 500; letter-spacing: 2px;">👋I'm Mr.DocPilot</h1>

<div style="font-size: 1.2rem; color: #888; margin-top: 10px; margin-bottom: 12px; line-height: 1.6;">
作为你的专属医学文献助手，我已经准备好了。<br>  
你可以上传左侧的心外科护理文献，或者直接向我提问。
</div>

<div style="font-size: 2.3rem; font-weight: 600; color: #333;">
今天有什么我能帮你的吗？
</div>

{img_html}
</div>""",
            unsafe_allow_html=True
        )
    else:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                ui_type = msg.get("ui_type")
                if ui_type == "medical_card":
                    d = msg.get("data", {})
                    st.success(f"💡 {d.get('core_conclusion', '')}")
                    col_left, col_right = st.columns(2)
                    with col_left:
                        st.subheader("📝 详细解析")
                        kd = d.get("key_details", [])
                        if kd:
                            for item in kd:
                                st.markdown(f"- ✅ {item}")
                        else:
                            st.info("暂无数据")
                    with col_right:
                        st.subheader("⚠️ 注意事项与预警")
                        wn = d.get("warnings_or_notes", [])
                        if wn:
                            for item in wn:
                                st.markdown(f"- 🚨 {item}")
                        else:
                            st.info("无特殊注意事项")
                else:
                    st.markdown(msg.get("content", ""))

    # ── AI 文档总结展示 ──
    if st.session_state.summary_content:
        with st.chat_message("assistant"):
            st.markdown("#### 📝 AI 文档总结")
            st.info(st.session_state.summary_content)
        st.session_state.summary_content = None

