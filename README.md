# ***Transaction Reconciliation System***

***A Django-based web application to reconcile partner settlement and statement Excel files, identify mismatches, and generate reconciliation insights.***

---

## ***📌 Project Overview***

The **Transaction Reconciliation System** is designed to automate the reconciliation process between:

- **Partner Settlement File**
- **Partner Statement (Transaction Report) File**

The system compares transactions using **PartnerPin**, validates settlement amounts, identifies variances, and presents a clear reconciliation summary through a web interface.

This project simulates a **real-world financial reconciliation workflow** commonly used in fintech and enterprise systems.

---

## ***⚙️ Key Features***

- Upload **Settlement** and **Statement** Excel files
- Filter transactions marked as **"Should Reconcile"**
- Match records using **PartnerPin**
- Categorize transactions into:
  - **Present in Both**
  - **Present in Settlement File but not in Partner Statement File**
  - **Not Present in Settlement File but Present in Partner Statement File**
- Compare settlement amounts for matched records
- Identify **variances**
- Display reconciliation summary on UI
- Clean, user-friendly Django interface

---

## ***🛠️ Tech Stack***

- **Backend:** Python, Django
- **Data Processing:** Pandas
- **Frontend:** HTML, CSS
- **File Handling:** Excel (`.xlsx`)
- **Version Control:** Git & GitHub

---

## ***🛠️ Deployment Link***

