# Implementation Plan: Export Live Transactions (Aug 3-22) & Reorganize CERA Store Asyut Data

This plan outlines the steps to safely export and backup all recent transactions (from August 3, 2026 to August 22, 2026) across all companies, analyze the historical data from `cera-store-20260803.dump.zip`, and restore the historical branch data into `CERA Store Asyut C002` (Company 5).

---

## User Review Required

> [!IMPORTANT]
> **Safety First**:
> 1. All live transactions from **Aug 3, 2026 to Aug 22, 2026** will be completely extracted and backed up to local structured files (JSON and CSV) across all companies before any data modification.
> 2. The backup archive `cera-store-20260803.dump.zip` (containing `dump.sql`) will be used to extract the exact historical records for Asyut branch.

---

## Proposed Phases & Execution

### Phase 1: Full Transaction Export (Aug 3 - Aug 22) across All Companies
- Connect to `cera-store.odoo.com` via JSON-RPC API.
- Export all records created or modified since `2026-08-03 00:00:00` for:
  - **POS**: `pos.session`, `pos.order`, `pos.order.line`, `pos.payment`
  - **Accounting**: `account.move`, `account.move.line`, `account.payment`
  - **Inventory**: `stock.picking`, `stock.move`, `stock.move.line`, `stock.quant`
  - **Sales & Purchases**: `sale.order`, `sale.order.line`, `purchase.order`, `purchase.order.line`
- Group the exported data by Company ID and Company Name.
- Save everything into `C:\Users\Video Editor\.gemini\antigravity\scratch\cera_exports_aug03_to_aug22\`.

### Phase 2: Analysis of Backup Data vs Live Data
- Inspect the tables in `dump.sql` for `res_company`, `pos_order`, `pos_session`, `account_move`, `stock_quant`.
- Compare IDs and company relationships between `CERA Store Asyut C001` (ID: 1) and `CERA Store Asyut C002` (ID: 5).

### Phase 3: Setup & Data Alignment for CERA Store Asyut C002
- Clean up any orphaned / mismatched records in `C002`.
- Load the historical Asyut branch data into `C002`.
- Verify POS configurations, journals, and warehouses for `C002`.

### Phase 4: Verification & Filtering
- Reconcile transaction counts and balances.
- Prepare separate filtered transaction files for each company for the period Aug 3 - Aug 22.

---

## Verification Plan

### Automated Verification
- Count records in export files vs records in Odoo to guarantee 100% data preservation.
- Verify total amounts and line counts for all exported POS orders and Accounting moves.
