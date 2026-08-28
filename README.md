# 📝 東淦入職安全訓練評估系統 (jo-sed-onboarding-quiz)

An Automated Enterprise Onboarding Safety Assessment Web System for Jumbo Orient.  
專為東淦工程有限公司 (Jumbo Orient) 安全及環保組 (SED) 打造之新員工入職安全訓練評估與報告自動歸檔系統。

---

## 🌐 項目簡介 / System Overview

**jo-sed-onboarding-quiz** 是一個基於 Streamlit 開發的企業級入職安全訓練互動 Web 系統。系統專為安環組（SED）設計，整合了 URL 免密直達門禁、動態載入地盤安全考核題庫、後端 SMTP 一鍵自動發送報告，以及即時合規 PDF 報告生成功能，協助安環組高效完成新員工入職安全訓練驗收與無紙化歸檔。

**jo-sed-onboarding-quiz** is an enterprise onboarding safety assessment web application developed for Jumbo Orient employees using Streamlit. Built to streamline Safety & Environmental Department (SED) workflows, it combines URL-based access security, dynamic quiz data loading, real-time safety knowledge evaluation, automated backend email delivery, and compliant PDF report generation for internal safety management.

---

## 🛠️ 核心特色 / Key Features

* **兩階段引導式流程 (2-Step Guided Workflow)**
  * 採用 Session State 嚴謹控管「第一部分：安全考核測驗 ➔ 第二部分：一鍵提交與存檔」，確保流程順暢且具備防重複提交機制。
  * Enforces a structured step-by-step submission flow to ensure assessment integrity and prevent duplicate submissions.

* **即時自動評分機制 (Real-time Automated Grading)**
  * 支援地盤安全考核單選題，提交後即時計算得分與合格狀態（滿分 5 分，最少答對 3 條判定為 PASS / FAIL）。
  * Dynamically evaluates safety responses, instantly calculating scores and pass status (Pass requirement: ≥3/5).

* **後端一鍵自動直寄 (One-Click Automated Email Delivery)**
  * 整合 Python 後端 SMTP 模組，員工點擊後系統於背景直接將成績與 PDF 附件打包發送至 SED 電郵，徹底解決員工遺漏附件或忘記寄信的問題。
  * Integrates backend Python SMTP to automatically package and deliver PDF reports to the SED inbox with a single click, eliminating manual attachment errors.

* **合規 PDF 報告生成 (Compliant PDF Report Generation)**
  * 自動擷取香港標準時間 (UTC+8)，將個人資料、答題成績及答題紀錄繪製成標準受控 PDF 文件 (`JO-SED-REC-2026-V1`)，內建 UTF-8 繁體中文字型與法規安全聲明。
  * Automatically embeds local timestamps (HKT) and detailed answer records into standard, printable PDF records for enterprise safety archiving.

* **企業級資安與動態題庫管理 (Enterprise Security & Dynamic Secrets Management)**
  * 支援 URL 免密參數（`?key=...`）直達與手動通行碼驗證；系統通行碼、SMTP 發信憑證及 JSON 題庫/答案統一透過 Streamlit Secrets 安全管理，原始碼零機密洩漏。
  * Features URL key parameter authentication and environment-level Secrets management for access codes, SMTP credentials, and JSON quiz data, preventing source code exposure.

---

## 🚀 系統流程 / Application Workflow

1. **第一部分：入職安全訓練評估 (Part I: Safety Assessment)**
   * 透過專屬連結或輸入員工通行碼進入系統。
   * 填寫姓名、職員編號、選擇組別，完成 5 條地盤安全評估試題並勾選獨立完成聲明。
2. **第二部分：一鍵提交與備份 (Part II: Submit & Archiving)**
   * 即時檢視考核得分與合格狀態（≥3 分合格）。
   * 點擊 **「🚀 點此一鍵自動送出報告至 SED 電郵」**，後端即時打包 PDF 報告發送至安環組。
   * 提供 **「💾 下載 PDF 報告」** 供員工自行備份，並附有 **WhatsApp 備用通訊管道**。

---

## 📄 文件與數據規範 / Document Standards

* **管控編號 (Document ID)**: `JO-SED-REC-2026-V1`
* **管理部門 (Department)**: 安全及環保組 / Safety & Environmental Department (SED)
* **收件對象 (SED Email)**: `k********@jumboorient.com.hk` (由 Secrets 配置)
* **合格標準 (Pass Criteria)**: 最少答對 3 / 5 條 (≥ 60%)
* **個人資料聲明 (Data Privacy Statement)**: 本文件為內部培訓紀錄，由員工本人確認獨立完成填答。個人資料僅供內部安全管理用途。
* **合規體系認證 (ISO Compliance)**: 
  * **ISO 45001 (職業健康安全)**: Clause 7.2 Competence 培訓與能力驗證文件化紀錄。
  * **ISO 9001 (品質管理)**: Integrated Management System (IMS) Controlled Records 文件管控。
  * **ISO 27001 (資訊安全)**: A.9 Access Control 門禁控制、金鑰隔離與零資料留存 (Zero-Data-Retention)。
