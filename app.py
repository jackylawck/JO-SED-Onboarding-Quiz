import os
import json
import re
import html
import textwrap
import smtplib
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, timezone, timedelta
import streamlit as st
from fpdf import FPDF

# 頁面設定
st.set_page_config(page_title="東淦入職安全訓練評估系統", page_icon="📝", layout="centered")

# ---------------------------------------------------------
# 1. 前端門禁驗證 (支援 URL 參數 ?key=... 免密直入與輸入框驗證)
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

valid_access_code = str(st.secrets.get("ACCESS_CODE", "")).strip()

# 檢查 URL 參數是否帶有金鑰 (?key=sed)
query_params = st.query_params
passed_key = str(query_params.get("key", "")).strip()

if valid_access_code and passed_key == valid_access_code:
    st.session_state.authenticated = True

if not st.session_state.authenticated:
    st.title("🔒 東淦入職安全訓練評估系統")
    st.markdown("🏢 [東淦工程有限公司 (Jumbo Orient) 官方網站](https://www.jumboorient.com.hk/)", unsafe_allow_html=True)
    st.write("")
    
    if not valid_access_code:
        st.error("⚠️ 系統尚未設定 ACCESS_CODE，請管理員於 Streamlit Secrets 設定後再試。")
        st.stop()

    user_code = st.text_input("請輸入員工通行碼以開始測驗：", type="password")
    if st.button("確認進入"):
        if user_code.strip() == valid_access_code:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("通行碼錯誤！請重新輸入或聯絡安環組 (SED)。")
    st.stop()

# ---------------------------------------------------------
# 2. Session State 流程與狀態控管
# ---------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = {}

if "email_sent" not in st.session_state:
    st.session_state.email_sent = False

# ---------------------------------------------------------
# 3. 讀取測驗題庫 (完全由 Secrets 保密)
# ---------------------------------------------------------
@st.cache_data
def get_questions():
    if "QUESTIONS_JSON" not in st.secrets:
        st.error("⚠️ 系統 Secrets 尚未設定 QUESTIONS_JSON 題庫，請聯絡系統管理員。")
        st.stop()
    try:
        return json.loads(st.secrets["QUESTIONS_JSON"])
    except Exception as e:
        st.error(f"⚠️ 題庫 JSON 格式解析失敗：{e}")
        st.stop()

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

def print_safe_text(pdf, text, max_chars=45):
    lines = textwrap.wrap(clean_text(text), width=max_chars)
    if not lines:
        pdf.cell(0, 6, txt="無", ln=1)
    else:
        for line in lines:
            pdf.cell(0, 6, txt=line, ln=1)

# ---------------------------------------------------------
# 4. PDF 生成函數 (符合 ISO 受控文件標準)
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
        print_safe_text(pdf, f"Q{i}. {q['question']}")
        print_safe_text(pdf, f"   提交答案：{ans}")
        pdf.ln(1)

    pdf.ln(8)
    pdf.set_font_size(8)
    print_safe_text(pdf, "聲明：本文件為內部培訓紀錄，由員工本人確認獨立完成填答。個人資料僅供內部安全管理用途。", max_chars=45)

    return bytes(pdf.output())

# ---------------------------------------------------------
# 5. 後端自動寄送電郵函數 (Python SMTP)
# ---------------------------------------------------------
def send_email_direct(b_info, q_res, status_str, pdf_bytes, submit_time_str):
    smtp_server = st.secrets.get("SMTP_SERVER", "smtp.office365.com")
    smtp_port = int(st.secrets.get("SMTP_PORT", 587))
    sender_email = st.secrets.get("SMTP_USER", "")
    sender_password = st.secrets.get("SMTP_PASSWORD", "")
    receiver_email = st.secrets.get("HR_EMAIL", "krystallin@jumboorient.com.hk")

    if not sender_email or not sender_password:
        raise ValueError("系統尚未設定 SMTP 發信帳號或密碼，請檢查 Secrets 配置。")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"【入職培訓結果】{b_info['dept']} - {b_info['name']} ({b_info['emp_id']})"

    body = f"""Dear SED,

員工已透過系統完成新員工入職安全訓練評估考核，詳情如下：
• 姓名：{b_info['name']}
• 職員編號：{b_info['emp_id']}
• 組別：{b_info['dept']}
• 測驗得分：{q_res['score']} / {q_res['total']} ({status_str})
• 提交時間：{submit_time_str}

詳細考核報告 PDF 檔案已隨信附上，請查閱存檔。

(本郵件由東淦入職安全訓練評估系統自動發送)"""

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 加入 PDF 附件
    safe_filename = re.sub(r'[\\/*?:"<>|]', "", b_info['name'])
    filename = f"入職培訓紀錄_{safe_filename}.pdf"
    part = MIMEApplication(pdf_bytes, Name=filename)
    part['Content-Disposition'] = f'attachment; filename="{filename}"'
    msg.attach(part)

    with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

# =========================================================
# 第一部分：入職培訓測驗 (Part I: Onboarding Quiz)
# =========================================================
if st.session_state.step == 1:
    st.title("📝 東淦入職安全訓練評估系統")
    st.markdown("🏢 [東淦工程有限公司 (Jumbo Orient) 官方網站](https://www.jumboorient.com.hk/)", unsafe_allow_html=True)
    st.write("")
    st.subheader("第一部分：入職安全訓練評估測驗")
    
    with st.form("step1_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("姓名 *", max_chars=20)
        with col2:
            emp_id = st.text_input("職員編號 *", max_chars=20)
        with col3:
            dept = st.selectbox("組別 *", DEPT_OPTIONS)
            
        st.divider()
        st.subheader("入職訓練評估試題（最少答對 3 條合格）")
        
        user_answers = {}
        for q in questions:
            user_answers[q["id"]] = st.radio(q["question"], q["options"], key=f"q_{q['id']}")

        st.divider()
        declaration = st.checkbox("本人確認上述資料正確，並由本人獨立完成測驗。 *")

        submit_step1 = st.form_submit_button("提交測驗並檢視得分 ➔")

    if submit_step1:
        if not name.strip() or not emp_id.strip() or dept == "請選擇組別":
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
                "basic_info": {"name": clean_text(name), "emp_id": clean_text(emp_id), "dept": dept},
                "quiz_result": {"score": score, "total": total_items, "is_pass": is_pass},
                "user_answers": user_answers,
                "submit_time": submit_time_str
            }
            st.session_state.step = 2
            st.session_state.email_sent = False
            st.rerun()

# =========================================================
# 第二部分：一鍵提交與備份 (Part II: Submit & Archiving)
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
    st.subheader("📤 第一步：一鍵送出報告至 SED 電郵")
    
    if not st.session_state.email_sent:
        if st.button("🚀 點此一鍵自動送出報告至 SED 電郵 (自動附加 PDF 報告)", type="primary", use_container_width=True):
            with st.spinner("系統正在自動打包 PDF 並寄出至安環組電郵 ..."):
                try:
                    send_email_direct(b_info, q_res, status_str, pdf_bytes, sub_time)
                    st.session_state.email_sent = True
                    st.success("🎉 提交成功！考核報告已直接寄達安環組 (krystallin@jumboorient.com.hk)。")
                    st.rerun()
                except Exception as e:
                    st.error(f"⚠️ 自動發送失敗，請使用下方按鈕手動下載備份。錯誤資訊：{e}")
    else:
        st.success("✅ 考核報告已成功寄送至安環組電郵！您無需重複操作。")

    st.divider()
    st.subheader("📥 第二步：備份與下載 (選填)")
    
    safe_filename = re.sub(r'[\\/*?:"<>|]', "", b_info['name'])
    st.download_button(
        label=f"💾 下載「入職培訓紀錄_{safe_filename}.pdf」自行存檔",
        data=pdf_bytes,
        file_name=f"入職培訓紀錄_{safe_filename}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    with st.expander("💬 備用通訊管道 (WhatsApp 通知 SED)"):
        wa_phone = "85295423912"
        wa_msg = f"Dear SED,\n我是 {b_info['dept']} 的 {b_info['name']} ({b_info['emp_id']})。我已完成新員工入職安全訓練考核（得分：{q_res['score']}/{q_res['total']}，{status_str}）。"
        wa_url = f"https://wa.me/{wa_phone}?text={urllib.parse.quote(wa_msg)}"
        st.markdown(
            f'<a href="{wa_url}" target="_blank" style="text-decoration:none;">'
            f'<button style="background-color:#25D366; color:white; padding:10px 16px; border:none; border-radius:6px; font-size:14px; font-weight:bold; cursor:pointer; width:100%; margin-top:8px;">'
            f'💬 透過 WhatsApp 通知安環組'
            f'</button></a>',
            unsafe_allow_html=True
        )

    st.write("")
    if st.button("🔄 重新進行測驗"):
        st.session_state.step = 1
        st.session_state.quiz_data = {}
        st.session_state.email_sent = False
        st.rerun()
