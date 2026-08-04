import os
import json
import textwrap
import urllib.parse
from datetime import datetime, timezone, timedelta
import streamlit as st
from fpdf import FPDF

# 頁面設定
st.set_page_config(page_title="東淦入職安全訓練評估系統", page_icon="📝")

# ---------------------------------------------------------
# 1. 前端門禁驗證 (從 Secrets 讀取 ACCESS_CODE)
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 東淦入職安全訓練評估系統")
    st.markdown("🏢 [東淦工程有限公司 (Jumbo Orient) 官方網站](https://www.jumboorient.com.hk/)", unsafe_allow_html=True)
    st.write("")
    
    if "ACCESS_CODE" not in st.secrets:
        st.error("⚠️ 系統尚未設定 ACCESS_CODE，請管理員於 Streamlit Secrets 設定後再試。")
        st.stop()

    user_code = st.text_input("請輸入員工通行碼以開始測驗：", type="password")
    if st.button("確認"):
        if user_code == st.secrets["ACCESS_CODE"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("通行碼錯誤！請重新輸入或聯絡 HR / 安環組。")
    st.stop()

# ---------------------------------------------------------
# 2. Session State 流程控管
# ---------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = {}

if "pdf_downloaded" not in st.session_state:
    st.session_state.pdf_downloaded = False

# ---------------------------------------------------------
# 3. 讀取測驗題庫 (預設 5 條安環試題)
# ---------------------------------------------------------
DEFAULT_QUESTIONS = [
    {
        "id": 1,
        "type": "single",
        "question": "1. 在什麼情況下需要配戴安全帽連帽帶？",
        "options": ["A. 進入地盤後任何時間", "B. 根據個人喜好", "C. 在室外地方才需要"],
        "answer": "A. 進入地盤後任何時間"
    },
    {
        "id": 2,
        "type": "single",
        "question": "2. 在何種情況下需要使用護眼罩？",
        "options": ["A. 任何情況都必須使用眼罩", "B. 任何情況都不須使用眼罩", "C. 當工序會產生火花或碎片時就需要使用"],
        "answer": "C. 當工序會產生火花或碎片時就需要使用"
    },
    {
        "id": 3,
        "type": "single",
        "question": "3. 在任何高空工作或任何離地工作及樓邊和升降槽內工作而沒有安全工作台是否需要使用全身式安全帶連雙尾扣？",
        "options": ["A. 是", "B. 否", "C. 按個人需要"],
        "answer": "A. 是"
    },
    {
        "id": 4,
        "type": "single",
        "question": "4. 如在地盤發生意外,你須怎樣處理？",
        "options": ["A. 立即報警求助", "B. 立即向所屬上司或當區安全人員報告", "C. 自行求醫"],
        "answer": ["B. 立即向所屬上司或當區安全人員報告"]
    },
    {
        "id": 5,
        "type": "single",
        "question": "5. 如在地盤發現不安全情況,你須怎樣處理？",
        "options": ["A. 不須理會,做妥自己工作便可", "B. 不須理會,其他人發現時會處理", "C. 立即向所屬上司或當區管工報告"],
        "answer": "C. 立即向所屬上司或當區管工報告"
    }
]

@st.cache_data
def get_questions():
    if "QUESTIONS_JSON" in st.secrets:
        try:
            return json.loads(st.secrets["QUESTIONS_JSON"])
        except Exception:
            return DEFAULT_QUESTIONS
    return DEFAULT_QUESTIONS

questions = get_questions()

DEPT_OPTIONS = [
    "請選擇組別", "管理層", "寫字樓", "人力資源組", "行政組", "計量組", 
    "規劃驗證組", "發判組", "項目組", "施工組", "工程組", 
    "安全及環保組 (SED)", "營運審計組", "會計組", "物控組", "倉管組", "其他"
]

def clean_text(val):
    if not val:
        return "無"
    cleaned = str(val).replace("\r\n", " ").replace("\n", " ").replace("\r", " ").strip()
    return cleaned if cleaned else "無"

# ---------------------------------------------------------
# 4. PDF 生成函數 (純考核版)
# ---------------------------------------------------------
def generate_pdf(basic_info, quiz_result, user_answers, submit_time_str):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    font_path = "NotoSansTC-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font("NotoSansTC", "", font_path)
        pdf.set_font("NotoSansTC", size=11)
    else:
        pdf.set_font("Helvetica", size=11)

    # Header
    pdf.set_font_size(9)
    pdf.cell(0, 5, txt="Jumbo Orient Development Limited - IMS Controlled Record", ln=1, align="R")
    pdf.cell(0, 5, txt="Document ID: JO-SED-REC-2026-V1 | Confidential", ln=1, align="R")
    pdf.ln(3)

    # 標題
    pdf.set_font_size(16)
    pdf.cell(0, 10, txt="入職訓練評估報告", ln=1, align="C")
    pdf.ln(5)
    
    # 個人基本資料 & 得分
    pdf.set_font_size(11)
    status_str = "合格 (PASS)" if quiz_result['is_pass'] else "不合格 (FAIL)"
    pdf.cell(0, 7, txt=f"姓名：{basic_info['name']}", ln=1)
    pdf.cell(0, 7, txt=f"職員編號：{basic_info['emp_id']}", ln=1)
    pdf.cell(0, 7, txt=f"組別：{basic_info['dept']}", ln=1)
    pdf.cell(0, 7, txt=f"考核時間：{submit_time_str}", ln=1)
    pdf.cell(0, 7, txt=f"測驗得分：{quiz_result['score']} / {quiz_result['total']} - {status_str}", ln=1)
    pdf.ln(5)

    # 答題明細
    pdf.set_font_size(12)
    pdf.cell(0, 8, txt="考核答題紀錄：", ln=1)
    pdf.set_font_size(10)

    for i, q in enumerate(questions, 1):
        ans = user_answers.get(q["id"], "未作答")
        pdf.cell(0, 6, txt=f"Q{i}. {q['question']}", ln=1)
        pdf.cell(0, 6, txt=f"   提交答案：{ans}", ln=1)
        pdf.ln(2)

    pdf.ln(10)
    pdf.set_font_size(8)
    lines = textwrap.wrap("聲明：本文件為內部培訓紀錄，由員工本人確認獨立完成填答。個人資料僅供內部安全管理用途。", width=45)
    for line in lines:
        pdf.cell(0, 5, txt=line, ln=1)

    return bytes(pdf.output())

def mark_as_downloaded():
    st.session_state.pdf_downloaded = True

# =========================================================
# 第一階段：回答 5 條選擇題
# =========================================================
if st.session_state.step == 1:
    st.title("📝 東淦入職安全訓練評估系統")
    st.markdown("🏢 [東淦工程有限公司 (Jumbo Orient) 官方網站](https://www.jumboorient.com.hk/)", unsafe_allow_html=True)
    st.write("")
    
    with st.form("step1_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("姓名 *")
        with col2:
            emp_id = st.text_input("職員編號 *")
        with col3:
            dept = st.selectbox("組別 *", DEPT_OPTIONS)
            
        st.divider()
        st.subheader("入職訓練評估試題（最少答對 3 條合格）")
        
        user_answers = {}
        for q in questions:
            user_answers[q["id"]] = st.radio(q["question"], q["options"], key=f"q_{q['id']}")

        st.divider()
        declaration = st.checkbox("本人確認上述資料正確，並由本人獨立完成測驗。 *")

        submit_step1 = st.form_submit_button("提交測驗並檢視成績 ➔")

    if submit_step1:
        if not name or not emp_id or dept == "請選擇組別":
            st.warning("請先完整填寫姓名、職員編號並選擇組別！")
        elif not declaration:
            st.warning("請先勾選個人確認聲明方可提交！")
        else:
            score = 0
            total_items = len(questions)
            
            for q in questions:
                user_ans = user_answers[q["id"]]
                correct_ans = q.get("answer", "")
                
                if isinstance(correct_ans, list):
                    if user_ans in correct_ans or [user_ans] == correct_ans:
                        score += 1
                else:
                    if user_ans == correct_ans:
                        score += 1

            is_pass = score >= 3
            
            hk_tz = timezone(timedelta(hours=8))
            now_hk = datetime.now(hk_tz)
            submit_time_str = now_hk.strftime("%Y-%m-%d %H:%M:%S")

            st.session_state.quiz_data = {
                "basic_info": {"name": name, "emp_id": emp_id, "dept": dept},
                "quiz_result": {"score": score, "total": total_items, "is_pass": is_pass},
                "user_answers": user_answers,
                "submit_time": submit_time_str
            }
            st.session_state.step = 2
            st.rerun()

# =========================================================
# 第二階段：顯示成績、下載 PDF 及寄送郵件
# =========================================================
elif st.session_state.step == 2:
    b_info = st.session_state.quiz_data["basic_info"]
    q_res = st.session_state.quiz_data["quiz_result"]
    u_ans = st.session_state.quiz_data["user_answers"]
    sub_time = st.session_state.quiz_data.get("submit_time", "")
    
    status_str = "合格 (PASS)" if q_res["is_pass"] else "不合格 (FAIL)"
    
    st.title("🎉 考核完成！")
    st.markdown("🏢 [東淦工程有限公司 (Jumbo Orient) 官方網站](https://www.jumboorient.com.hk/)", unsafe_allow_html=True)
    st.write("")
    
    st.info(f"👤 員工：{b_info['name']} ({b_info['emp_id']}) | 組別：{b_info['dept']}")
    
    if q_res['is_pass']:
        st.balloons()
        st.success(f"🎯 測驗得分：{q_res['score']} / {q_res['total']}（{status_str}）— 恭喜通過入職培訓考核！")
    else:
        st.error(f"⚠️ 測驗得分：{q_res['score']} / {q_res['total']}（{status_str}）— 未達 3 分合格標準，請重新進行測驗。")
        
    pdf_bytes = generate_pdf(b_info, q_res, u_ans, sub_time)
    
    st.divider()
    st.subheader("📥 步驟 1：下載 PDF 報告檔 (必須先下載)")
    
    st.download_button(
        label=f"點此下載「入職培訓紀錄_{b_info['name']}.pdf」",
        data=pdf_bytes,
        file_name=f"入職培訓紀錄_{b_info['name']}.pdf",
        mime="application/pdf",
        on_click=mark_as_downloaded
    )
    
    st.divider()
    
    if not st.session_state.pdf_downloaded:
        st.warning("🔒 步驟 2 解鎖條件：請先點擊上方「步驟 1」按鈕下載 PDF 報告檔！")
    else:
        st.success("✅ 已順利下載 PDF 報告！請選擇下方提交方式發送給安環組：")
        st.subheader("步驟 2：選擇提交方式發送至安環組電郵")
        
        email_to = st.secrets.get("HR_EMAIL", "未設定安環組電郵")
        email_subject = f"【入職培訓結果】{b_info['dept']} - {b_info['name']} ({b_info['emp_id']})"
        email_body = f"""Dear SED,

我是 {b_info['dept']} 的 {b_info['name']} ({b_info['emp_id']})。
我已於 {sub_time} 完成新員工入職培訓考核（得分：{q_res['score']}/{q_res['total']}，{status_str}）。

（已下載並附上「入職培訓紀錄_{b_info['name']}.pdf」報告檔案）"""

        mailto_url = f"mailto:{email_to}?subject={urllib.parse.quote(email_subject)}&body={urllib.parse.quote(email_body)}"
        
        st.markdown(
            f'<a href="{mailto_url}" target="_blank" style="text-decoration:none;">'
            f'<button style="background-color:#0078D4; color:white; padding:12px 20px; border:none; border-radius:6px; font-size:16px; font-weight:bold; cursor:pointer; width:100%; margin-bottom:8px;">'
            f'📧 點此自動開啟 Outlook 寄至 {email_to}'
            f'</button></a>',
            unsafe_allow_html=True
        )
        
        st.caption(f"💡 若點擊按鈕未彈出 Outlook，請複製電郵地址 ({email_to}) 手動寄信並附加 PDF。")
        st.code(email_to, language=None)

    st.write("")
    if st.button("🔄 重新進行測驗"):
        st.session_state.step = 1
        st.session_state.quiz_data = {}
        st.session_state.pdf_downloaded = False
        st.rerun()
