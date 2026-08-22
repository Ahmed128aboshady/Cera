import os
import shutil
import subprocess

repo_dir = r"C:\Users\Video Editor\.gemini\antigravity\scratch\cera_github_repo"
scripts_dir = os.path.join(repo_dir, "scripts")
docs_dir = os.path.join(repo_dir, "docs")

os.makedirs(scripts_dir, exist_ok=True)
os.makedirs(docs_dir, exist_ok=True)

src_scratch = r"C:\Users\Video Editor\.gemini\antigravity\brain\8fd5d34c-5bb2-41a0-b7fe-a3deb14e778c\scratch"
for f in os.listdir(src_scratch):
    if f.endswith('.py'):
        shutil.copy2(os.path.join(src_scratch, f), os.path.join(scripts_dir, f))
        print(f"Copied script: {f}")

brain_dir = r"C:\Users\Video Editor\.gemini\antigravity\brain\8fd5d34c-5bb2-41a0-b7fe-a3deb14e778c"
for doc in ["walkthrough.md", "implementation_plan.md"]:
    src_doc = os.path.join(brain_dir, doc)
    if os.path.exists(src_doc):
        shutil.copy2(src_doc, os.path.join(docs_dir, doc))
        print(f"Copied doc: {doc}")

readme_content = """# CERA Store Multi-Company Odoo Migration & Recovery Suite 🚀

مستودع شامل لجميع السكربتات والأدوات المستخدمة لإعادة هيكلة وضبط فروع وشركات **CERA Store** على نظام **Odoo 19 Enterprise SaaS**.

---

## 📌 نبذة عامة عن المشروع (Project Overview)

تم تنفيذ عملية إعادة هيكلة شاملة لفروع وشركات CERA Store:
1. **فرع أسيوط 2 (`CERA Store Asyut C002`)**:
   - استعادة ودمج كافة العمليات التاريخية من الباك آب القديم (18,642 طلباً) + معاملات الفترة الحديثة من 3 إلى 21 أغسطس (674 طلباً) = **19,316 طلباً**.
   - عزل كتالوج المنتجات ليظهر منتجات أسيوط الأصلية فقط (**6,505 أصناف**) ومطابقة الباك آب.
   - استيراد ومطابقة أرصدة المخزون من الباك آب ليصبح بالمخزن (**2,114 صنفاً متوفراً برصيد 26,460 قطعة**).
   - تجهيز نقطة البيع والكاشير ودفاتر الحسابات وقوائم الأسعار بالكامل.
2. **عزل وحماية باقي الفروع**:
   - فرع القاهرة (`First Store Cairo`): 2,460 طلباً.
   - فرع المنيا (`CERA Store Minya C003`): 36 طلباً بعد إصلاح مشكلة فتح الدرج.
   - المخزن الرئيسي (`Cerameda Warehouse`): معزول ومحمي.
3. **تأمين البيانات**:
   - سحب نسخة احتياطية كاملة (JSON) لجميع الحركات من 3 إلى 22 أغسطس.

---

## 📁 محتويات المستودع (Repository Structure)

```text
├── docs/
│   ├── walkthrough.md               # التقرير الشامل لجميع المراحل والعمليات
│   └── implementation_plan.md       # خطة العمل الفنية المفصلة
│
├── scripts/
│   ├── export_all_transactions.py      # تصدير ونسخ جميع المعاملات من 3 إلى 22 أغسطس
│   ├── apply_c002_replicate.py         # ضبط طلبات أسيوط 2 وتوزيع العمليات التاريخية
│   ├── sync_full_c002_inventory.py     # استيراد أرصدة المخزون بالكامل من الباك آب
│   ├── sync_stage2_inventory.py        # استكمال ومطابقة باقي أصناف المخزن
│   ├── restore_rule_71.py              # ضبط قواعد حماية وقراءة المنتجات المتعددة الشركات
│   ├── audit_c002_completeness.py      # فحص شامل لجاهزية الفرع والكاشيرات والدفاتر
│   ├── check_c002_duplicates.py        # تحليل وفحص التكرارات في المنتجات والأكواد
│   └── assign_cairo_warehouse_prods.py # تخصيص منتجات الفروع والمخزن الرئيسي
│
└── README.md
```

---

## ⚙️ متطلبات التشغيل (Prerequisites)

- Python 3.10+
- مكتبات Python القياسية: `urllib`, `json`, `http.cookiejar`, `collections`, `os`
- صلاحيات وصول Admin على قاعدة بيانات Odoo.

---

## 👨‍💻 بيانات الاعتماد والاتصال (Connection Config)

تستخدم السكربتات بروتوكول `JSON-RPC` للتواصل المباشر والآمن مع Odoo:
- **Live Database**: `https://cera-store.odoo.com`
- **Backup Database**: `https://cera-store-20260803.odoo.com`
- **Authentication**: `draboueldahab@cerastoreeg.com`
"""

with open(os.path.join(repo_dir, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme_content)
print("Created README.md")
