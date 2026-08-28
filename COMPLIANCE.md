# 🛡️ Compliance, Governance & Regulatory Assessment
# 合規、治理架構與法規適用性評估報告

**Document Control ID / 受控文件編號**: `JO-SED-GOV-2026-V1`  
**System Name / 系統名稱**: 東淦入職安全訓練評估系統 (jo-sed-onboarding-quiz)  
**Governing Unit / 管控部門**: 安全及環保組 (SED)  
**Effective Date / 生效日期**: 2026-08-28  

---

## 1. Executive Summary / 執行摘要

This document defines the regulatory compliance, privacy architecture, and risk governance posture of the **jo-sed-onboarding-quiz** system deployed by Jumbo Orient Development Limited. The system operates under a **Zero Server Retention (ZSR)** and **Privacy-by-Design (PbD)** paradigm to deliver internal occupational safety evaluations.

本文件闡明東淦工程有限公司「入職安全訓練評估系統」之法規遵循、私隱架構與風險治理方針。系統採用「零伺服器資料留存 (ZSR)」與「由設計保障私隱 (PbD)」機制，專為內部職業安全健康培訓考核而設計。

---

## 2. Regulatory Applicability Matrix / 法規與治理標準適用性矩陣

| Regulatory Framework / 標準規範 | Jurisdiction / 管轄範圍 | Applicability / 適用性 | Justification & Governance Measure / 治理與處置依據 |
| :--- | :--- | :--- | :--- |
| **Hong Kong PDPO (Cap. 486)** | Hong Kong | **Full (全面適用)** | Strict adherence to DPP1-DPP6; explicit consent declaration; data minimization (Worker ID, Name, Dept only). |
| **EU GDPR** | European Union / Global | **Proportional (按比例遵循)** | Art. 25 (Data protection by design/default); Art. 5(1)(c) (Data minimisation); No persistent storage on host servers. |
| **EU Artificial Intelligence Act** | European Union | **Non-Applicable (不適用)** | System is deterministic, hardcoded rule-based scoring. No autonomous ML/AI logic, GPAI, or High-Risk AI deployment. |
| **ISO/IEC 42001:2023 (AIMS)** | International | **Exempt / Aligned (免除/對齊)** | Non-AI Determination filed. Adheres to organizational AI transparency and automated decision safeguards. |
| **ISO/IEC 27001:2022 (ISMS)** | International | **Full (全面適用)** | Clause A.9 (Access Control), A.10 (Cryptography/Secrets), A.8.20 (Network Security) via Streamlit Secrets and HTTPS. |
| **ISO 45001:2018 (OHSMS)** | International | **Full (全面適用)** | Clause 7.2 (Competence & Training records verification); generates immutable audit trails for on-site personnel. |
| **ISO 9001:2015 (QMS)** | International | **Full (全面適用)** | Clause 7.5 (Documented Information); standardized record format (`JO-SED-REC-2026-V1`). |
| **US EAR / ITAR / Dual-Use** | United States / Global | **Non-Applicable (不適用)** | EAR99 compliant. Uses standard open-source Python libraries (Streamlit, FPDF) with no proprietary military cryptography. |

---

## 3. Data Protection & Privacy-by-Design (PbD)
## 數據保護與由設計保障私隱架構

* **Principle of Data Minimisation (資料最小化原則)**:
  * The system collects only: Worker Registration ID (工人註冊證), Name, Department, and Assessment Timestamp.
  * No biometric data, sensitive financial records, or high-risk identifiers are processed or held.
* **Zero Server Retention (ZSR) (零伺服器資料留存)**:
  * Application memory is transient within the Python session state.
  * PDF records are generated dynamically in-memory (`bytes`) and immediately transferred via TLS encrypted SMTP to designated authorized SED inboxes.
  * No underlying SQL/NoSQL databases are maintained on cloud infrastructure.
* **Integrity and Access Control (存取控制與機密隔離)**:
  * Application access requires runtime authorization (`ACCESS_CODE`).
  * Questions, answers, and SMTP transmission credentials are fundamentally decoupled from public source code repositories via Environment-level Secrets (`st.secrets`).

---

## 4. Non-AI Determination Statement / 非人工智能系統判定聲明

Pursuant to the definitions in the EU AI Act (Regulation (EU) 2024/1689) and ISO/IEC 22989:
* The **jo-sed-onboarding-quiz** is classified as a **Deterministic Automated Logic Evaluation Engine**.
* It does NOT utilize generative neural architectures, dynamic probabilistic inference, continuous adaptive machine learning, or automated human-profiling algorithms.
* Consequently, requirements for High-Risk AI Conformity Assessments, Post-Market Monitoring, and AI Foundation Model Registries under EU AI Act and ISO/IEC 42001 are explicitly documented as **Non-Applicable (不適用)**.

