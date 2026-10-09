# FinSight — Frontend Architecture & UI/UX Specification

## 1. Overview & Vision

FinSight is a modern, high-trust Personal Finance & Budgeting platform designed for students, young professionals, and data-conscious individuals. The frontend interfaces with a dual-database FastAPI backend (PostgreSQL for transactional ledger truth and MongoDB for analytics and AI insights).

### Core Goals
- **High Visual Trust**: Clean, polished FinTech aesthetic inspired by modern financial platforms (e.g., Stripe, Mercury, Revolut).
- **Action-Oriented UX**: Fast, frictionless recording of transactions, instant inter-account transfers, and intuitive budgeting.
- **Data Density & Clarity**: Informative dashboards with interactive charts without clutter or visual fatigue.
- **Dual Engine Visibility**: Direct surface for both deterministic ledger data (balances, transactions) and AI/ML features (auto-categorization, breach predictions, anomaly detection).

---

## 2. Design System & Visual Guidelines

### 2.1 Theme & Color Palette
FinSight uses a modern dark-slate aesthetic by default (with seamless light-mode compatibility):

| Token | Class / Hex | Usage |
|---|---|---|
| **Base Background** | `slate-950` (`#020617`) | Main application canvas background |
| **Card Surface** | `slate-900` (`#0f172a`) | Elevated component cards and containers |
| **Borders & Dividers** | `slate-800` (`#1e293b`) | Subtle section separators and card borders |
| **Primary Accent** | `emerald-500` (`#10b981`) | Inflow, positive balances, primary buttons, savings progress |
| **Expense / Debit** | `rose-500` (`#f43f5e`) | Outflow, expense transactions, negative delta |
| **Budget Warning** | `amber-500` (`#f59e0b`) | Budget utilization at 75%–99% |
| **Critical / Breached** | `red-600` (`#dc2626`) | Budget utilization ≥ 100%, severe fraud alerts |
| **AI / Machine Learning** | `indigo-500` / `violet-500` | Auto-categorization pills, anomaly badges, AI advisory cards |
| **Transfer / Neutral Info** | `sky-500` (`#0ea5e9`) | Account-to-account transfers, system notices |

### 2.2 Typography & Formatting
- **Font**: Inter or system sans-serif stack (`font-sans`).
- **Currency Display**: Always format currency according to user preference (Default `INR` / `₹`).
  - Example: `₹1,24,500.00` (Indian comma notation for INR).
  - Positive amounts: `+ ₹45,000.00` (styled in `text-emerald-400`).
  - Negative amounts: `- ₹1,250.00` (styled in `text-rose-400`).
- **Date/Time**: Relative timestamps (`"2 hours ago"`) on activity feeds, explicit dates (`"18 Sep 2026, 04:30 PM"`) on ledger detail views.

### 2.3 Layout Shell
- **Collapsible Sidebar (Left)**: Logo, navigation links, wallet summary, user role badge (`USER`, `ADMIN`, `SUPER_ADMIN`), and theme switch.
- **Top Bar (Sticky)**: Current net worth ticker, global search bar (`Cmd + K`), notification bell (budget warnings & fraud alerts), and persistent `+ New Transaction` primary CTA.
- **Main Viewport**: Responsive 12-column grid with consistent padding (`px-6 py-8`).

---

## 3. Technology Stack

- **Framework**: React 18 + Vite (Lightning-fast HMR and bundling)
- **Styling**: Tailwind CSS + `clsx` / `tailwind-merge` for conditional class management
- **Routing**: React Router DOM (v6+) with protected routes and role-based guards
- **Data Fetching & State Management**: Axios with JWT interceptors (automatic token refresh) + TanStack React Query (v5) for server-state caching
- **Data Visualizations**: Recharts (ResponsiveContainer, AreaChart, BarChart, PieChart/Donut)
- **Icons**: Lucide React (`lucide-react`)
- **Modals & UI Primitives**: Headless UI or Radix UI primitives for accessible dialogs, dropdowns, and tabs
- **Notifications**: Sonner or React Hot Toast for crisp action toasts

---

## 4. Screen-by-Screen Breakdown

### 4.1 Authentication & Onboarding (`/login`, `/register`)
- **Layout**: Clean two-panel layout (Left: FinSight hero branding and live feature highlights; Right: Auth form card).
- **Register Form**:
  - Full Name, Email, Password (with strength indicator).
  - Default Currency selector (`INR`, `USD`, `EUR`).
  - Monthly estimated income (for initial budget seeding).
- **Login Form**:
  - Email, Password, "Remember Me" toggle.
  - Quick demo-account credential autofill buttons (e.g., Demo User, Demo Admin).
- **Security**: JWT Access Token (stored in memory/state) + Refresh Token (handled via HTTP-only cookie or secure storage).

---

### 4.2 Main Overview Dashboard (`/`)
The primary operational center for the user.

1. **Top Metric Cards (KPI Ribbon)**:
   - **Net Worth**: Cumulative balance across all bank accounts, cash wallets, and UPI IDs.
   - **Monthly Inflow**: Total income for the current calendar month with a `% vs last month` trend indicator.
   - **Monthly Outflow**: Total expenditure for the month with spending velocity comparison.
   - **Budget Health Indicator**: Circular ring or pill badge displaying aggregate spending vs monthly cap (e.g., *"68% spent — On Track"*).
2. **Visual Analytics Grid**:
   - **Cashflow Curve (Area Chart)**: 6-month historical income vs expense trend.
   - **Spending by Category (Donut Chart)**: Visual breakdown of expenses (Groceries, Rent, Utilities, Entertainment, Dining) with center total.
3. **Action & Attention Feeds**:
   - **Recent Activity Ledger**: Last 5–7 transactions with payee icon, category badge, and instant click-to-view drawer.
   - **AI Insights Banner**: Dynamic card displaying the latest insight generated from the MongoDB analytics collection (e.g., *"Dining expenses are 22% higher this week than your 3-month average"*).
   - **Fraud Alert Banner**: Appears only if transactions are flagged as `SUSPICIOUS` by the Isolation Forest model.

---

### 4.3 Accounts & Wallets Hub (`/accounts`)
Directly mapped to `/api/accounts` and `/api/transfers`.

- **Accounts Grid**:
  - Visual cards representing each account type:
    - **Bank Accounts** (e.g., HDFC, SBI with masked account number `•••• 4821`).
    - **UPI Wallets** (e.g., GPay, PhonePe, Paytm).
    - **Cash in Hand**.
    - **Credit Cards** (Balance used vs credit limit bar).
  - Card displays: Account Name, Type badge, Current Balance, and Quick Actions (Edit, Deactivate).
- **Quick Inter-Account Transfer Modal (`fn_transfer_funds`)**:
  - Source Account dropdown (shows current available balance).
  - Destination Account dropdown (prevents selecting the same account).
  - Amount input with real-time overdraft guard.
  - Transfer notes/reference.
- **Add / Edit Account Drawer**:
  - Form fields: Name, Type (`BANK`, `CASH`, `UPI`, `CREDIT`), Opening Balance, Currency.

---

### 4.4 Transaction Ledger & Explorer (`/transactions`)
Directly mapped to `/api/transactions`.

- **Filtering & Search Toolbar**:
  - Date Range Picker (Presets: "This Month", "Last 30 Days", "Custom Range").
  - Type Filter Pills: `All`, `Income`, `Expense`, `Transfer`.
  - Category Dropdown (multi-select).
  - Account Filter Dropdown.
  - Flag Status Filter: `All`, `Normal`, `Suspicious`, `Confirmed`, `Rejected`.
  - Amount Range slider (`min_amount` to `max_amount`).
  - Search input (searches payee name, notes, reference ID).
- **Transactions Data Table**:
  - **Date & Time**: Formatted timestamp.
  - **Payee / Description**: Merchant title with category subtext.
  - **Category**: Color-coded pill with auto-categorization badge (indicates if assigned by keyword rule or ML model).
  - **Account**: Badge identifying the account debited or credited.
  - **Receipt**: Icon indicating receipt attachment; clicking opens full-resolution preview modal (GridFS).
  - **Amount**: Bold green (`+`) or red (`-`) formatted currency.
  - **Status Badge**:
    - `NORMAL`: Subtle neutral badge.
    - `SUSPICIOUS`: High-visibility amber/red pulsing badge with "Review" CTA.
    - `CONFIRMED`: Verified safe badge.
  - **Row Actions**: View details, Edit transaction, Delete transaction.
- **Table Footer**: Pagination controls (`Page X of Y`, page size selector `20 / 50 / 100`) and **Export to CSV** button.

---

### 4.5 Budgets & Spending Limits (`/budgets`)
Directly mapped to `/api/budgets` and PostgreSQL view `v_budget_vs_actual`.

- **Global Budget Utilization**:
  - Header bar showing total budget allocated vs total spent in the current month.
- **Category Budget Cards**:
  - Card for each category containing:
    - Category name & icon.
    - Allocated Budget vs Actual Spent (e.g., `₹8,500 / ₹10,000`).
    - Progress Bar with dynamic color thresholds:
      - `< 75%`: Green (`bg-emerald-500`)
      - `75% – 99%`: Amber (`bg-amber-500`)
      - `≥ 100%`: Crimson (`bg-rose-600`) with "Breached" flag.
    - **Breach Prediction Badge**: Calculated based on daily spending velocity (e.g., *"At current rate, projected breach in 6 days"*).
- **Set / Modify Budget Modal**:
  - Category selector, monthly amount cap, notification threshold percentage slider (e.g., warn at 80%).

---

### 4.6 Savings Goals & Auto-Sweep (`/goals`)
Directly mapped to `/api/goals` and stored procedure `fn_auto_sweep`.

- **Goal Cards**:
  - Examples: *"Emergency Reserve"*, *"MacBook Pro M-Series"*, *"Europe Travel Fund"*.
  - Radial progress ring or bar displaying Target vs Current Saved Amount.
  - Target Completion Date and remaining time counter (e.g., *"3 months left"*).
  - Monthly required contribution metric to meet deadline.
- **Actions**:
  - **Contribute Funds Modal**: Instant transfer from any active account into the goal.
  - **Auto-Sweep Trigger**:
    - Explanation banner: *"Automatically sweeps idle checking balances above your set threshold into prioritized savings goals."*
    - Manual "Run Auto-Sweep Now" button invoking the backend stored procedure.

---

### 4.7 Analytics & Deep-Dive Reports (`/analytics`)
Directly mapped to `/api/analytics`, `/api/reports`, and SQL views (`v_monthly_summary`, `v_top_payees`).

- **Interactive Visualizations (Recharts)**:
  - **Budget vs Actual Comparison**: Grouped vertical bar chart comparing budgeted allowance against actual spending across categories.
  - **Top Payees / Merchants**: Horizontal ranked bar chart showing top spending destinations (e.g., Swiggy, Amazon, Uber, Electricity Board).
  - **Month-over-Month Rollup**: Comparative bar chart of monthly expenditures over the past 12 months.
- **Reports & Export Section**:
  - Monthly summary statement generator.
  - One-click CSV export of categorized transactions for personal accounting or tax filing.

---

### 4.8 AI Insights & Anomaly Center (`/insights`)
Directly mapped to `/api/insights` and the ML fraud detection layer.

- **AI Insights Feed**:
  - Cards generated from MongoDB analytics and ML models:
    - *Spike Detection*: "Entertainment expenses are 45% higher than your weekend average."
    - *Recurring Subscriptions*: "Detected recurring charge of ₹999 for Netflix on the 15th."
    - *Savings Recommendation*: "You have ₹22,000 idle cash; moving ₹10,000 to your Emergency Fund will achieve your Q4 goal."
- **Fraud & Suspicious Transaction Review Drawer**:
  - Lists all transactions flagged by the Isolation Forest model (anomaly score > 0.70).
  - Detailed anomaly explanation (e.g., unusual time of transaction, abnormal amount compared to historical payee baseline).
  - Interactive resolution buttons:
    - **Mark as Confirmed / Legitimate** (updates backend flag status to `CONFIRMED`).
    - **Dispute / Reject** (updates flag status to `REJECTED`).

---

### 4.9 Admin & System Console (`/admin`) *(Role Protected: ADMIN, SUPER_ADMIN)*
Directly mapped to `/api/admin`.

- **Platform Overview Metrics**:
  - Total users registered, active sessions, platform transaction volume.
- **Audit Logs Explorer (`audit_logs`)**:
  - Live table of system events: Timestamp, User Email, Action (`LOGIN_SUCCESS`, `CREATE_ACCOUNT`, `TRANSFER_EXECUTE`, `PASSWORD_RESET`), Client IP, Status code.
  - Filterable by user, action type, and date.
- **User Management**:
  - User list with role indicators (`USER`, `ADMIN`, `SUPER_ADMIN`) and active status toggles.

---

## 5. Key Modals & Micro-Interactions

1. **Add / Edit Transaction Modal**:
   - Tabbed type switcher (`Expense` | `Income` | `Transfer`).
   - Large numeric amount input with currency prefix.
   - Account picker (shows live account balances).
   - Category picker with auto-suggest based on payee input.
   - Date-time picker (defaults to present time).
   - Drag-and-drop receipt image upload (with thumbnail preview).
2. **Transfer Funds Modal**:
   - Visual transfer diagram: `[From Account Card]` ➔ `[Arrow]` ➔ `[To Account Card]`.
   - Real-time balance validation preventing overdrafts.
3. **Receipt Viewer Modal**:
   - Clean lightbox display for uploaded receipt images fetched from MongoDB GridFS.

---

## 6. Frontend File & Directory Architecture

```
frontend/
├── Dockerfile
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── index.html
└── src/
    ├── main.jsx                   # React root mount
    ├── App.jsx                    # Router configuration & query client provider
    ├── index.css                  # Tailwind directives and custom scrollbar styles
    │
    ├── api/                       # API clients & backend endpoints
    │   ├── client.js              # Axios instance with JWT interceptors
    │   ├── auth.js                # Auth endpoints (login, register, refresh)
    │   ├── accounts.js            # Account CRUD & transfers
    │   ├── transactions.js        # Transaction CRUD, filters, receipt upload
    │   ├── budgets.js             # Budgeting endpoints
    │   ├── goals.js               # Savings goals & auto-sweep
    │   ├── analytics.js           # Chart metrics & SQL view data
    │   ├── insights.js            # AI insights & anomaly flags
    │   └── admin.js               # Audit logs & platform aggregates
    │
    ├── context/                   # Global React contexts
    │   ├── AuthContext.jsx        # User state, tokens, login/logout functions
    │   └── UIContext.jsx          # Sidebar toggle, active modals, theme
    │
    ├── hooks/                     # Custom React Query & utility hooks
    │   ├── useAuth.js             # Auth hook
    │   ├── useAccounts.js         # Account queries & mutation invalidations
    │   ├── useTransactions.js     # Paginated and filtered transaction queries
    │   ├── useBudgets.js          # Budget status and mutation hooks
    │   └── useAnalytics.js        # Dashboard summary and chart data hooks
    │
    ├── components/
    │   ├── layout/                # Main shell components
    │   │   ├── Sidebar.jsx        # Navigation links & profile summary
    │   │   ├── Navbar.jsx         # Header bar, quick stats, notification trigger
    │   │   ├── ProtectedRoute.jsx # Route authentication guard
    │   │   └── RoleGuard.jsx      # RBAC route guard (ADMIN / SUPER_ADMIN)
    │   │
    │   ├── ui/                    # Reusable atomic UI elements
    │   │   ├── Button.jsx         # Variants (primary, secondary, danger, ghost)
    │   │   ├── Card.jsx           # Surface card with border styling
    │   │   ├── Modal.jsx          # Accessible dialog overlay
    │   │   ├── Badge.jsx          # Status and category badges
    │   │   ├── Input.jsx          # Form inputs with validation errors
    │   │   ├── Select.jsx         # Styled dropdown selects
    │   │   ├── ProgressBar.jsx    # Threshold-colored progress indicator
    │   │   └── EmptyState.jsx     # Friendly zero-data placeholder
    │   │
    │   ├── charts/                # Recharts wrappers
    │   │   ├── CashflowTrend.jsx  # Area chart for income vs expenses
    │   │   ├── CategoryDonut.jsx  # Pie/Donut chart for spending share
    │   │   ├── BudgetBarChart.jsx # Grouped bar chart (budget vs actual)
    │   │   └── TopPayeesBar.jsx   # Horizontal bar chart for top merchants
    │   │
    │   └── modals/                # Contextual user action modals
    │       ├── TransactionModal.jsx # Add/Edit transaction with receipt dropzone
    │       ├── TransferModal.jsx    # Inter-account transfer modal
    │       ├── BudgetModal.jsx      # Set/Edit category budget limit
    │       ├── GoalModal.jsx        # Create/Contribute to savings goal
    │       └── ReceiptViewerModal.jsx # Full-size image preview
    │
    ├── pages/                     # Routed page views
    │   ├── Login.jsx              # Sign-in page
    │   ├── Register.jsx           # Sign-up page
    │   ├── Dashboard.jsx           # Primary dashboard overview
    │   ├── Accounts.jsx           # Account cards and transfer actions
    │   ├── Transactions.jsx       # Transaction ledger, filters & export
    │   ├── Budgets.jsx            # Budget cards and breach status
    │   ├── Goals.jsx              # Savings goals and auto-sweep
    │   ├── Analytics.jsx          # Extended analytics & reports
    │   ├── Insights.jsx           # AI suggestions and fraud review queue
    │   ├── Admin.jsx              # Audit logs and system metrics
    │   └── NotFound.jsx           # 404 handler
    │
    └── utils/                     # Formatting and calculation utilities
        ├── formatters.js          # Currency (`formatCurrency(amount)`), dates
        └── constants.js           # Category icons, color mappings, route definitions
```

---

## 7. API Integration Strategy

### 7.1 JWT Interceptor & Auto-Refresh
The frontend `api/client.js` maintains an Axios interceptor pipeline:
1. **Request Interceptor**: Injects `Authorization: Bearer <access_token>` into outbound requests.
2. **Response Interceptor**:
   - If response status is `401 Unauthorized`:
     - Pauses pending requests.
     - Calls `/api/auth/refresh` using the stored refresh token.
     - If successful, updates the access token and retries failed requests.
     - If refresh fails, clears session state and redirects to `/login`.

### 7.2 Backend Route Mapping Reference

| Frontend Feature | Backend API Endpoint | HTTP Method |
|---|---|---|
| User Login | `/api/auth/login` | `POST` |
| Token Refresh | `/api/auth/refresh` | `POST` |
| Current User Profile | `/api/auth/me` | `GET` |
| List Accounts | `/api/accounts` | `GET` |
| Create Account | `/api/accounts` | `POST` |
| Inter-Account Transfer | `/api/transfers` | `POST` |
| Filtered Transactions | `/api/transactions?page=1&size=20...` | `GET` |
| Create Transaction | `/api/transactions` | `POST` |
| Confirm Suspicious Transaction | `/api/transactions/{id}/confirm` | `POST` |
| Category Budgets & Status | `/api/budgets` | `GET` |
| Set Category Budget | `/api/budgets` | `POST` |
| List Savings Goals | `/api/goals` | `GET` |
| Auto-Sweep Trigger | `/api/goals/auto-sweep` | `POST` |
| Dashboard Statistics | `/api/analytics/dashboard` | `GET` |
| Category Spending Breakdown | `/api/analytics/spending-breakdown` | `GET` |
| Monthly Cashflow Trend | `/api/analytics/monthly-trend` | `GET` |
| Top Payees Chart | `/api/analytics/top-payees` | `GET` |
| AI Insights Feed | `/api/insights/latest` | `GET` |
| Audit Trail Logs | `/api/admin/audit-logs` | `GET` |
| Platform Aggregates | `/api/admin/aggregates` | `GET` |

---

## 8. Implementation Roadmap

1. **Phase 1: Project Scaffolding & Tooling**
   - Initialize `package.json`, Vite configuration with API proxy, and Tailwind CSS setup.
   - Setup Axios client with JWT interceptor and React Query provider.
2. **Phase 2: Authentication & Layout Shell**
   - Build `AuthContext`, login/registration pages, and token persistence.
   - Build layout shell: `Sidebar`, `Navbar`, and `ProtectedRoute`.
3. **Phase 3: Core Financial Ledger**
   - Implement `Accounts` page with account cards and `TransferModal`.
   - Implement `Transactions` page with filters, pagination, and `TransactionModal`.
4. **Phase 4: Budgets, Goals & Stored Procedures**
   - Implement `Budgets` page with color-coded progress bars and breach warnings.
   - Implement `Goals` page with radial progress and Auto-Sweep trigger button.
5. **Phase 5: Analytics & Visualizations**
   - Integrate Recharts components for cashflow trend, category donut, and top payees.
   - Assemble primary `Dashboard` page with KPI cards and charts.
6. **Phase 6: ML/AI Features & Admin Console**
   - Build `Insights` page displaying AI recommendations and suspicious transaction review queue.
   - Build `Admin` audit logs viewer and user management page for admin roles.
