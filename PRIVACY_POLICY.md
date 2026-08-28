# 🛡️ 個人資料私隱政策與合規聲明 / Personal Data Privacy Policy & Compliance Notice

**文件管控編號 / Document ID**: `JO-SED-POL-2026-V1`  
**生效日期 / Effective Date**: 2026-08-28  

---

## 1. 政策聲明 / Policy Statement

東淦工程有限公司（以下簡稱「本公司」）深知個人資料之重要性，並全力遵守香港特別行政區法例第486章《個人資料（私隱）條例》（PDPO）及相關國際資料保護實踐。本「東淦入職安全訓練評估系統」（以下簡稱「本系統」）之運作秉持**「由設計保障私隱」（Privacy-by-Design）**及**「最小化資料收集」（Data Minimization）**原則。

Jumbo Orient Development Limited ("the Company") is fully committed to protecting personal data privacy in compliance with the Personal Data (Privacy) Ordinance (Cap. 486 of the Laws of Hong Kong) and international data governance best practices. The "JO SED Onboarding Safety Assessment System" is designed in strict adherence to the principles of **Privacy-by-Design** and **Data Minimization**.

---

## 2. 收集之資料類別與目的 / Types and Purposes of Data Collected

本系統僅收集評估入職安全訓練所必需之最少資料：

| 收集項目 / Item | 目的 / Purpose | 法規依據 / Regulatory Basis |
| :--- | :--- | :--- |
| **姓名 (Full Name)** | 識別受訓員工身份 / Identity Verification | PDPO DPP 1 / ISO 45001 Clause 7.2 |
| **工人註冊證 (Worker Registration No.)** | 記錄地盤法定從業資格 / Statutory Verification | 香港建造業工人註冊條例 (Cap. 583) |
| **所屬組別 (Department)** | 安全檔案組別歸檔 / Departmental Archiving | ISO 9001 Clause 7.5 |
| **測驗答案與時間 (Quiz Answers & Timestamp)** | 評估職安健知識水平 / Safety Competency Record | ISO 45001 Clause 7.2 |

*註：本系統絕不收集香港身份證號碼、生物特徵、通訊地址或任何非業務必要之敏感個人資料。*  
*Note: This system does NOT collect HKID numbers, biometric data, home addresses, or any non-essential sensitive personal data.*

---

## 3. 資料留存政策（零資料留存架構） / Zero-Data-Retention Architecture

* **無伺服器端資料庫 (No Server-side Database)**：本系統不設永久性資料庫，亦不將員工個人資料儲存於託管平台（Streamlit Community Cloud / GitHub）。
* **記憶體即時處理 (In-Memory Processing)**：所有輸入資料僅於瀏覽器連線期間存在於臨時記憶體（Session State）中，生成 PDF 報告並完成發送後，記憶體即自動釋放重置。
* **文件化受控存檔 (Documented Archiving)**：由系統生成之受控 PDF 文件（`JO-SED-REC-2026-V1`）直接傳輸至本公司專用安全郵箱 (`krystallin@jumboorient.com.hk`) 進行內部封閉存檔。

---

## 4. 資訊安全與技術防護措施 / Security Measures (ISO/IEC 27001 Aligned)

1. **傳輸加密 (Encryption in Transit)**：全站強制採用 TLS 1.3 / HTTPS 傳輸協定。
2. **金鑰隔離 (Secrets Isolation)**：系統通行碼（Access Code）、SMTP 發信憑證與題庫答案均由雲端環境變數（Secrets）保管，原始碼庫零機密暴露。
3. **輸入消毒 (Input Sanitization)**：嚴格限制輸入字元長度並自動過濾惡意控制字元，防止注入（Injection）攻擊。
4. **防暴力破解 (Brute-Force Protection)**：內建登入錯誤次數限制機制。

---

## 5. 資料主體權利 / Data Subject Rights

依據香港《個人資料（私隱）條例》，員工有權查閱及更正其存檔之入職訓練紀錄。如有查詢，請聯絡安全及環保組（SED）。  
Under the PDPO, employees have the right to request access to and correction of their recorded safety training records by contacting the Safety & Environmental Department (SED).
