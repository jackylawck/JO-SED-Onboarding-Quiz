import os
import json
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, timezone, timedelta
import streamlit as st
from fpdf import FPDF

# 頁面設定
st.set_page_config(page_title="東淦入職安全訓練評估系統", page_icon="📝", layout="centered")

# ---------------------------------------------------------
# 1. 前端門禁驗證 (加入錯誤嘗試計數與防暴力重試)
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0

if not st.session_state.authenticated:
    st.title("🔒 東淦入職安全訓練評估系統")
    st.markdown("🏢 [東淦工程有限公司 (Jumbo Orient) 官方網站](https://www.jumboorient.com.hk/)")
    st.write("")
    
    if "ACCESS_CODE" not in st.secrets:
        st.error("⚠️ 系統安全組態未就緒 (ACCESS_CODE Missing)，請聯絡安環組管理員。")
        st.stop()

    if st.session_state.login_attempts >= 5:
        st.error("🚫 登入失敗次數過多，為維護系統安全，請重新整理頁面或稍後再試。")
        st.stop()

    user_code = st.text_input("請輸入員工通行碼以開始測驗：", type="password", max_chars=20)
    if st.button("確認"):
        if user_code == st.secrets["ACCESS_CODE"]:
            st.session_state.authenticated = True
            st.session_state.login_attempts = 0
            st.rerun()
        else:
            st.session_state.login_attempts += 1
            remaining = 5 - st.session_state.login_attempts
            st.error(f"通行碼錯誤！剩餘嘗試次數：{remaining}")
    st.stop()

# ---------------------------------------------------------
# 2. Session State 流程控管
# ---------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = {}

# ---------------------------------------------------------
# 3. 從 Secrets 動態載入測驗題庫
# ---------------------------------------------------------
@st.cache_data
def get_questions():
    if "QUESTIONS_JSON" not in st.secrets:
        st.error("⚠️ 題庫組態未載入，請聯絡系統管理員。")
        st.stop()
    try:
        return json.loads(st.secrets["QUESTIONS_JSON"])
    except Exception as e:
        st.error("⚠️ 題庫 JSON 格式解析失敗，請檢查系統後台配置。")
        st.stop()

questions = get_questions()

DEPT_OPTIONS = [
    "請選擇組別", "管理層", "寫字樓", "人力資源組", "行政組", "計量組", 
    "規劃驗證組", "發判組", "項目組", "施工組", "工程組", 
    "安全及環保組 (SED)", "營運審計組", "會計組", "物控組", "倉管組", "其他"
]

def sanitize_input(val: str, max_len: int = 50) -> str:
    """清理輸入字串，去除換行與惡意注入字元"""
    if not val:
        return "無"
    cleaned = re.sub(r"[\r\n\t]", " ", str(val)).strip()
    return cleaned[:max_len] if cleaned else "無"

# ---------------------------------------------------------
# 4. 合規 PDF 生成函數
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

    # Header - IMS 管控資訊
    pdf.set_font_size(9)
    pdf.cell(0, 5, txt="Jumbo Orient Development Limited - IMS Controlled Record", ln=1, align="R")
    pdf.cell(0, 5, txt="Document ID: JO-SED-REC-2026-V1 | Confidential", ln=1, align="R")
    pdf.ln(3)

    # 標題
    pdf.set_font_size(16)
    pdf.cell(0, 10, txt="入職訓練評估報告", ln=1, align="C")
    pdf.ln(5)
    
    # 員工基本資料 & 得分
    pdf.set_font_size(11)
    status_str = "合格 (PASS)" if quiz_result['is_pass'] else "不合格 (FAIL)"
    pdf.cell(0, 7, txt=f"姓名：{basic_info['name']}", ln=1)
    pdf.cell(0, 7, txt=f"工人註冊證編號：{basic_info['emp_id']}", ln=1)
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

# ---------------------------------------------------------
# 5. SMTP 後端自動發信函數
# ---------------------------------------------------------
def send_email_with_pdf(basic_info, quiz_result, pdf_bytes, submit_time_str):
    if "SMTP_USER" not in st.secrets or "SMTP_PASSWORD" not in st.secrets:
        return False, "未設定 SMTP 寄件帳號或密碼，無法自動發信。"
    
    smtp_server = st.secrets.get("SMTP_SERVER", "smtp.office365.com")
    smtp_port = int(st.secrets.get("SMTP_PORT", 587))
    sender_email = st.secrets["SMTP_USER"]
    sender_password = st.secrets["SMTP_PASSWORD"]
    receiver_email = st.secrets.get("HR_EMAIL", "krystallin@jumboorient.com.hk")
    
    status_str = "合格 (PASS)" if quiz_result["is_pass"] else "不合格 (FAIL)"
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = f"【入職培訓結果】{basic_info['dept']} - {basic_info['name']} ({basic_info['emp_id']})"
    
    body = f"""Dear SED,

新員工入職安全訓練考核紀錄如下：
• 姓名：{basic_info['name']}
• 工人註冊證編號：{basic_info['emp_id']}
• 所屬組別：{basic_info['dept']}
• 考核時間：{submit_time_str}
• 考核得分：{quiz_result['score']} / {quiz_result['total']} ({status_str})

詳細考核報告 PDF 檔已隨信附上，請查閱存檔。

(本郵件由東淦入職安全訓練評估系統自動發送)"""

    msg.attach(MIMEText(body, "plain", "utf-8"))
    
    # 附加 PDF
    pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
    safe_filename = re.sub(r'[\\/*?:"<>|]', "", basic_info['name'])
    pdf_attachment.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', f"入職培訓紀錄_{safe_filename}.pdf"))
    msg.attach(pdf_attachment)
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True, "考核報告 PDF 已成功自動寄送至安環組郵箱！"
    except Exception as e:
        return False, f"自動發信失敗：{str(e)}"

# =========================================================
# 第一階段：回答選擇題並提交
# =========================================================
if st.session_state.step == 1:
    st.title("📝 東淦入職安全訓練評估系統")
    st.markdown("🏢 [東淦工程有限公司 (Jumbo Orient) 官方網站](https://www.jumboorient.com.hk/)")
    st.write("")
    
    with st.form("step1_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name_raw = st.text_input("姓名 *", max_chars=20)
        with col2:
            emp_id_raw = st.text_input("工人註冊證編號 *", max_chars=20)
        with col3:
            dept = st.selectbox("組別 *", DEPT_OPTIONS)
            
        st.divider()
        st.subheader("入職訓練評估試題（最少答對 3 條合格）")
        
        user_answers = {}
        for q in questions:
            user_answers[q["id"]] = st.radio(q["question"], q["options"], key=f"q_{q['id']}")

        st.divider()
        declaration = st.checkbox("本人確認上述資料正確，並由本人獨立完成測驗。 *")

        submit_step1 = st.form_submit_button("提交測驗並自動發送報告 ➔")

    if submit_step1:
        name = sanitize_input(name_raw, 20)
        emp_id = sanitize_input(emp_id_raw, 20)

        if not name_raw.strip() or not emp_id_raw.strip() or dept == "請選擇組別":
            st.warning("請先完整填寫姓名、工人註冊證編號並選擇組別！")
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

            basic_info = {"name": name, "emp_id": emp_id, "dept": dept}
            quiz_result = {"score": score, "total": total_items, "is_pass": is_pass}
            
            # 生成 PDF
            pdf_bytes = generate_pdf(basic_info, quiz_result, user_answers, submit_time_str)
            
            # 背景自動發信
            with st.spinner("正在自動發送報告至安環組，請稍候..."):
                mail_ok, mail_msg = send_email_with_pdf(basic_info, quiz_result, pdf_bytes, submit_time_str)

            st.session_state.quiz_data = {
                "basic_info": basic_info,
                "quiz_result": quiz_result,
                "user_answers": user_answers,
                "submit_time": submit_time_str,
                "pdf_bytes": pdf_bytes,
                "mail_status": (mail_ok, mail_msg)
            }
            st.session_state.step = 2
            st.rerun()

# =========================================================
# 第二階段：顯示成績與自動發送狀態 (一鍵直出)
# =========================================================
elif st.session_state.step == 2:
    b_info = st.session_state.quiz_data["basic_info"]
    q_res = st.session_state.quiz_data["quiz_result"]
    pdf_bytes = st.session_state.quiz_data.get("pdf_bytes")
    mail_ok, mail_msg = st.session_state.quiz_data.get("mail_status", (False, "未執行發信"))
    
    status_str = "合格 (PASS)" if q_res["is_pass"] else "不合格 (FAIL)"
    
    st.title("🎉 考核完成！")
    st.markdown("🏢 [東淦工程有限公司 (Jumbo Orient) 官方網站](https://www.jumboorient.com.hk/)")
    st.write("")
    
    st.info(f"👤 員工：{b_info['name']} ({b_info['emp_id']}) | 組別：{b_info['dept']}")
    
    if q_res['is_pass']:
        st.balloons()
        st.success(f"🎯 測驗得分：{q_res['score']} / {q_res['total']}（{status_str}）— 恭喜通過入職培訓考核！")
    else:
        st.error(f"⚠️ 測驗得分：{q_res['score']} / {q_res['total']}（{status_str}）— 未達 3 分合格標準，請重新進行測驗。")
        
    st.divider()
    
    st.subheader("📧 報告發送狀態")
    if mail_ok:
        st.success(f"✅ {mail_msg}")
        st.caption(f"考核紀錄 PDF 已直接送達安環組郵箱 ({st.secrets.get('HR_EMAIL', 'krystallin@jumboorient.com.hk')})，您無需進行其他操作。")
    else:
        st.warning(f"⚠️ {mail_msg}")
        st.info("請點擊下方按鈕自行下載 PDF 報告，並手動補寄給安環組。")
    
    # 備用下載按鈕 (供員工個人保存備份)
    safe_filename = re.sub(r'[\\/*?:"<>|]', "", b_info['name'])
    st.download_button(
        label=f"📥 下載個人考核紀錄備份 (PDF)",
        data=pdf_bytes,
        file_name=f"入職培訓紀錄_{safe_filename}.pdf",
        mime="application/pdf"
    )

    st.write("")
    if st.button("🔄 重新進行測驗"):
        st.session_state.step = 1
        st.session_state.quiz_data = {}
        st.rerun()
