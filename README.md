# 📝 東淦入職安全訓練評估系統 (jo-sed-onboarding-quiz)

An Automated Enterprise Onboarding Safety Assessment Web System for Jumbo Orient.  
專為東淦工程有限公司 (Jumbo Orient) 安全及環保組 (SED) 打造之新員工入職安全訓練評估與報告生成系統。

---

## 🌐 項目簡介 / System Overview

**jo-sed-onboarding-quiz** 是一個基於 Streamlit 開發的企業級入職安全訓練互動 Web 系統。系統專為安環組（SED）設計，整合了門禁驗證、5 題地盤安全知識考核及即時合規 PDF 報告生成功能，協助安環組高效完成新員工入職安全訓練驗收與檔案歸檔。

**jo-sed-onboarding-quiz** is an enterprise onboarding safety assessment web application developed for Jumbo Orient employees using Streamlit. Built to streamline Safety & Environmental Department (SED) workflows, it combines access security, real-time safety knowledge evaluation, and automated, compliant PDF report generation for internal safety management.

---

## 🛠️ 核心特色 / Key Features

* **兩階段引導式流程 (2-Step Guided Workflow)**
  * 採用 Session State 嚴謹控管「第一階段：安全考核測驗 ➔ 第二階段：成績檢視、報告導出及發送」，確保流程順暢且易於操作。
  * Enforces a structured step-by-step submission flow to ensure assessment integrity and a smooth user experience.

* **即時自動評分機制 (Real-time Automated Grading)**
  * 支援單選題考核，提交後即時計算得分與 60% 合格率狀態（滿分 5 分，最少答對 3 條判定為 PASS / FAIL）。
  * Dynamically evaluates multiple-choice safety responses, instantly calculating scores and pass status (Pass requirement: ≥3/5).

* **合規 PDF 報告生成 (Compliant PDF Report Generation)**
  * 自動擷取香港標準時間 (UTC+8)，將個人資料、答題成績及答題紀錄繪製成標準 PDF 文件 (`JO-SED-REC-2026-V1`)，內建 UTF-8 繁體中文字型與法規安全聲明。
  * Automatically embeds local timestamps (HKT) and detailed answer records into standard, printable PDF records for enterprise safety archiving.

* **快捷提交管道 (One-Click Email & Outlook Submission)**
  * 內建安全解鎖機制，確保員工先下載 PDF 報告後方可開啟提交按鈕；支援一鍵開啟 Outlook (`mailto:`) 並預填郵件範本，方便員工隨信附上 PDF 附件發送至安環組。
  * Features a conditional download lock to ensure users save their PDF before launching pre-formatted Outlook email links.

* **企業級安全與防護 (Enterprise Security & Secrets Management)**
  * 前端整合通行碼門禁驗證，系統通行碼與安環組電郵統一透過 Streamlit Secrets 安全管理，防止敏感資訊外洩。
  * Integrated access control with environment-level Secrets handling to protect corporate access codes and internal contacts.

---

## 🚀 系統流程 / Application Workflow

1. **第一階段：入職安全訓練評估 (Part I: Safety Assessment)**
   * 輸入員工通行碼、姓名、職員編號及組別。
   * 完成 5 條地盤安全評估試題（安全帽、護眼罩、安全帶、意外處理及不安全情況報告）並勾選獨立完成聲明。
2. **第二階段：下載與提交 (Part II: Download & Send)**
   * 即時檢視得分與合格狀態（≥3 分合格）。
   * 點擊下載生成之 PDF 報告檔 (`入職培訓紀錄_姓名.pdf`)。
   * 解鎖並點擊「開啟 Outlook」一鍵將報告發送至安環組 (`krystallin@jumboorient.com.hk`)。

---

## 📄 文件與數據規範 / Document Standards

* **管控編號 (Document ID)**: `JO-SED-REC-2026-V1`
* **管理部門 (Department)**: 安全及環保組 / Safety & Environmental Department (SED)
* **合格標準 (Pass Criteria)**: 最少答對 3 / 5 條 (≥ 60%)
* **個人資料聲明 (Data Privacy Statement)**: 本文件為內部培訓紀錄，由員工本人確認獨立完成填答。個人資料僅供內部安全管理用途。
* **合規標準 (Compliance)**: Integrated Management System (ISO 45001 / ISO 14001 / ISO 9001) Controlled Records
