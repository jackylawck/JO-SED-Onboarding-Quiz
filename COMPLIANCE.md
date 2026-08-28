# 📋 綜合合規與治理架構說明書 / Comprehensive Compliance & Governance Framework

**專案名稱 / Project Name**: 東淦入職安全訓練評估系統 (jo-sed-onboarding-quiz)  
**受控編號 / Control Document ID**: `JO-SED-GOV-2026-V1`  
**所屬體系 / Management System**: Jumbo Orient Integrated Management System (IMS)

---

## 1. 全球與本地法規合規適用性評估 / Regulatory Applicability Matrix

本系統經法規與風險評估，各主要國際標準與法規適用性界定如下：


```

+-----------------------------------------------------------------------------------+
| 法規 / 標準規範 (Standard / Law)       | 適用狀態 (Status) | 治理與合規對應措施 (Compliance Measures)             |
+-----------------------------------------------------------------------------------+
| 香港個人資料(私隱)條例 (Cap. 486 PDPO)  | ✅ 完全適用        | 符合保障資料原則 (DPP 1-4)，資料最小化與告知聲明。  |
| ISO 45001:2018 (職安健管理體系)        | ✅ 完全適用        | 符合 Clause 7.2 人員安全能力驗證與培訓紀錄歸檔。     |
| ISO 9001:2015 (品質管理體系)           | ✅ 完全適用        | 符合 Clause 7.5 受控文件識別碼 (JO-SED-REC-2026-V1)。|
| ISO/IEC 27001:2022 (資訊安全管理)      | ✅ 完全適用        | A.9 存取控制、Secrets 機密隔離、輸入消毒防護。        |
| 歐盟 GDPR (EU 2016/679) 參照           | 🌐 原則對標        | 落實 Privacy by Design 與 Zero Data Retention。    |
| 歐盟人工智能法案 (EU AI Act)            | ❌ 不適用 (N/A)   | 本系統屬確定性規則邏輯，無任何 AI/ML 模型或演算法。   |
| ISO/IEC 42001:2023 (人工智能管理體系)  | ❌ 不適用 (N/A)   | 無 AI 生命週期或自主決策系統，免除 AIMS 治理要求。   |
+-----------------------------------------------------------------------------------+

```

---

## 2. 治理與架構技術合規要點 / Technical Governance Points

### 2.1 零資料留存原則 (Zero-Data-Retention)
本系統作為輕量級前端 Web 介面，不架設任何外置儲存庫（No SQL / No NoSQL / No Cloud Storage Bucket）。所有資料流轉僅於記憶體中執行單次 PDF 渲染並即時發送，保障員工私隱不受雲端託管端洩漏威脅。

### 2.2 審計追蹤與不可否認性 (Auditability & Non-Repudiation)
* 每份 PDF 報告自動標註香港標準時間戳（UTC+8 HKT）。
* 每份報告完整列印受試者之每題實際提交答案與得分判定。
* 包含受試者個人誠信獨立填答聲明，滿足 IMS 內部審計與勞工處/公營機構之地盤安全稽核標準。

### 2.3 變更與維護管控 (Change Management)
題庫與合格標準統一由安環組主管（SED Manager）於後台環境設定檔（`QUESTIONS_JSON`）維護，程式原始碼倉庫（Source Code Repository）嚴禁硬編碼任何業務機密，符合安全開發生命週期（SDLC）規範。

---

## 3. 合規審計簽核 / Compliance Sign-off

* **體系主責部門 / Lead Department**: 安全及環保組 (SED)
* **稽核參照標準 / Audit References**: ISO 9001 / ISO 14001 / ISO 45001 / ISO 27001
* **受控存檔期限 / Retention Period**: 依公司安全管理政策及建造業法定培訓紀錄保存年限執行。
