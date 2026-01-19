# Propti UI/UX Design Prompts for Stitch AI

Use these prompts with Stitch AI to generate the user interface and design systems for the Propti property management application. Customize them based on your specific design preferences.

---

## 1. Overall App Design & Branding

### Prompt: Design System & Color Palette

```
Create a modern, professional design system for "Propti" - a property management application 
for landlords. The app should feel trustworthy, clean, and efficient.

Design Requirements:
- Color Palette: Use a primary color of blue (#2563EB) with complementary greens (#10B981) 
  for success states, reds (#EF4444) for alerts/overdue payments, and grays for neutral elements
- Typography: Modern sans-serif font (similar to Inter or Poppins)
- Component Library: Create buttons (primary, secondary, danger), cards, modals, and form inputs
- Spacing: Use consistent 8px grid system
- Visual Style: Minimalist with subtle shadows and rounded corners (8px border-radius)
- Dark Mode: Include a dark mode variant for evening usage

Target Users: Landlords aged 30-60 who manage multiple properties
Platform: Mobile-first responsive web application
Accessibility: WCAG 2.1 AA compliant with high contrast ratios
```

---

## 2. Authentication Screens

### Prompt: Login & Registration Screens

```
Design the authentication screens for Propti property management app.

Screens to create:
1. Login Screen
   - Email/phone number input field
   - Password input field
   - "Forgot Password?" link
   - "Sign Up" link
   - Login button
   - Firebase sign-in option (with Google icon)
   - Optional: Remember me checkbox

2. Registration/Sign-Up Screen
   - Full name input
   - Email input with validation
   - Phone number input
   - Password input with strength indicator
   - Confirm password input
   - Terms & Conditions checkbox
   - Register button
   - "Already have an account? Login" link

3. Password Reset Screen
   - Email input
   - "Send Reset Link" button
   - Back to login link

Design Style: Clean, welcoming, with property/home imagery in background
Trust Elements: Display security badges, company info
Mobile Responsive: Optimized for mobile-first usage
```

---

## 3. Dashboard & Navigation

### Prompt: Main Dashboard Layout

```
Create the main dashboard/home screen for Propti property management application.

Layout Components:
1. Top Navigation Bar
   - Propti logo/branding on left
   - Search bar (search properties/tenants)
   - Notification bell icon with badge counter
   - User profile dropdown (name, email, settings, logout)
   - Dark mode toggle

2. Sidebar Navigation (collapsible on mobile)
   - Dashboard (home icon)
   - Properties (building icon)
   - Rooms (door icon)
   - Tenants (people icon)
   - Rent Cycles (calendar icon)
   - Payments (wallet icon)
   - Reminders (bell icon)
   - Reports (chart icon)
   - Settings (gear icon)

3. Main Dashboard Content Area
   - Welcome message: "Welcome back, [Landlord Name]"
   - Key Metrics Cards (4 cards):
     * Total Properties: [X]
     * Active Tenants: [X]
     * Monthly Revenue: [Currency amount]
     * Pending Payments: [X] overdue, [Y] due soon
   
4. Quick Action Cards
   - Add New Property (button/icon)
   - Add Tenant (button/icon)
   - Record Payment (button/icon)
   - Generate Report (button/icon)

5. Recent Activity Widget
   - Recent payments
   - Tenant updates
   - New properties added

6. Upcoming Payments Widget
   - Table showing next 5 rent due dates
   - Sortable by date, property, tenant
   - Quick action to record payment

Color Indicators: Green for on-time, Yellow for due soon, Red for overdue
Responsive Design: Sidebar collapses on tablets/mobile
Interactive: Cards should be clickable to navigate to detailed views
```

---

## 4. Properties Management

### Prompt: Properties List & Detail Screens

```
Design the Properties management section for Propti.

Screens to Create:

1. Properties List View
   - Grid or list view toggle
   - Search/filter bar (by name, location, status)
   - Sort options (alphabetical, date added, rooms count, revenue)
   - "Add New Property" button
   
   Card/Row Display (per property):
   - Property image/photo (placeholder if none)
   - Property name
   - Location/address
   - Number of rooms
   - Occupancy rate (X/Y rooms occupied)
   - Monthly revenue
   - Status badge (Active/Inactive)
   - Action menu (view, edit, delete)
   - Click to view details

2. Property Detail Screen
   - Header with property image carousel
   - Property Information Section:
     * Name, Address, Created Date
     * Number of rooms, current occupancy
     * Total monthly revenue
     * Status toggle (Active/Inactive)
   
   - Rooms Section:
     * List of all rooms in property
     * Room number, rent amount, tenant name, payment status
     * "Add Room" button
     * Room pagination or scroll
   
   - Property Statistics:
     * Revenue chart (last 3-6 months)
     * Occupancy rate pie chart
     * Collection rate percentage
   
   - Actions:
     * Edit Property button
     * Delete Property button (with confirmation)
     * Generate Property Report button

3. Add/Edit Property Modal
   - Property name input (required)
   - Property address/location input
   - Property photo upload
   - Description textarea (optional)
   - Status toggle
   - Save/Cancel buttons
   - Validation messages

Design: Use cards for visual hierarchy
Interactive: Clicking room cards should show room details
Responsive: Grid on desktop (2-3 columns), single column on mobile
```

---

## 5. Rooms Management

### Prompt: Rooms Management Screen

```
Design the Rooms management interface for properties within Propti.

Context: Rooms belong to Properties. Each room has a rent amount, due date, and optional tenant.

Screens to Create:

1. Rooms List (within Property detail)
   - Table view with columns:
     * Room Number
     * Rent Amount (in local currency)
     * Due Date (day of month)
     * Assigned Tenant (name or "Vacant")
     * Payment Status (badge: Paid/Partial/Overdue)
     * Last Payment Date
     * Actions (edit, delete, view details)
   
   - Filters:
     * By status (Paid, Partial, Overdue, Vacant)
     * By tenant name
   
   - "Add Room" button at top

2. Add/Edit Room Modal
   - Room number input (required)
   - Rent amount input (required, with currency symbol)
   - Due date picker (day of month, 1-31)
   - Tenant assignment dropdown (searchable list)
   - Notes textarea (optional)
   - Save/Cancel buttons

3. Room Detail View
   - Room information header
   - Current tenant information (if assigned)
   - Rent cycle history (expandable table)
   - Payment history (last 6 months)
   - Quick actions:
     * Assign/Change Tenant
     * Record Payment
     * View Rent Cycles
     * Edit Room

Status Indicators:
- Green: Paid on time
- Yellow: Partial payment
- Red: Overdue
- Gray: Vacant

Responsive: Card view on mobile, table on desktop
Accessibility: Good color contrast for status badges
```

---

## 6. Tenants Management

### Prompt: Tenants Management Screen

```
Design the Tenants management interface for Propti.

Screens to Create:

1. Tenants List View
   - Search/filter bar (by name, phone, property, email)
   - Sort options (by name, date added, balance)
   - View toggle (Grid/List)
   - "Add Tenant" button
   
   Card/Row Display (per tenant):
   - Tenant photo/avatar (default avatar if none)
   - Full name
   - Phone number
   - Email
   - Assigned room/property
   - Current balance (color-coded: green if positive, red if balance owed)
   - Status badge (Active/Archived)
   - Action menu (view, edit, archive)

2. Tenant Detail Screen
   - Header with tenant photo and basic info
   
   Personal Information Section:
   - Full name, phone, email
   - Faculty (if student), year of study
   - Guardian name, phone, location
   - ID card number
   - Assigned room/property with link
   
   Financial Summary:
   - Current balance
   - Total paid (lifetime)
   - Total owed (lifetime)
   - Payment status gauge
   
   Rent Cycles & Payments:
   - Table of all rent cycles
   - Payment history (last 12 months)
   - Payment breakdown chart
   
   Actions:
   - Edit Tenant button
   - Archive Tenant button
   - Record Payment button
   - Send Reminder button
   - View Full History button

3. Add/Edit Tenant Modal
   Form Sections:
   
   A. Basic Information
   - Full name (required)
   - Phone number (required)
   - Email (optional)
   
   B. Academic Information (optional)
   - Faculty
   - Year of study
   
   C. Guardian Information
   - Guardian name
   - Guardian phone
   - Guardian location
   
   D. Identification
   - ID card number
   - Photo upload
   
   - Save/Cancel buttons
   - Form validation with error messages

4. Archive Tenant Confirmation
   - Confirmation message
   - Show current balance
   - Option to download tenant history
   - Confirm/Cancel buttons

Design Elements:
- Use avatars with first letter initials (colored backgrounds)
- Color-code balance (green for zero/positive, red for owed)
- Show occupancy timeline if tenant has multiple rooms
- Responsive: Grid on desktop, list on mobile
```

---

## 7. Rent Cycles & Payments

### Prompt: Rent Cycles and Payments Management

```
Design the Rent Cycles and Payments tracking interface for Propti.

Context: Rent Cycles define periods when a tenant owes rent. Payments record what the tenant has paid.

Screens to Create:

1. Rent Cycles List
   - Filter by:
     * Property
     * Tenant
     * Status (Active, Completed, Past Due)
     * Date range
   
   - Sort by: Start date, end date, amount, status
   
   Table Columns:
   - Rent Cycle ID (short)
   - Room Number
   - Tenant Name
   - Start Date
   - End Date
   - Amount Due
   - Amount Paid
   - Balance Remaining (color-coded)
   - Status Badge
   - Actions (view, edit, delete)
   
   - "Create Rent Cycle" button

2. Rent Cycle Detail View
   - Cycle information header
   - Timeline showing:
     * Start date, end date, due date
     * Payment status indicator
   
   - Financial Summary:
     * Amount due
     * Amount paid
     * Balance remaining
     * Payment percentage (progress bar)
   
   - Payments Section:
     * All payments for this cycle (table)
     * Payment date, method, amount, notes
     * "Add Payment" button
   
   - Actions:
     * Edit cycle
     * Delete cycle
     * Record payment

3. Create/Edit Rent Cycle Modal
   - Room selection dropdown (required)
   - Tenant auto-populated from room
   - Start date picker
   - End date picker
   - Amount input (required)
   - Notes textarea
   - Due date (auto-calculated)
   - Save/Cancel buttons

4. Record Payment Screen
   - Cycle/Tenant selector at top
   - Payment Details Form:
     * Amount paid input
     * Payment method dropdown (Cash, Mobile Money, Bank)
     * Payment date picker
     * Reference number (for bank/mobile money)
     * Notes textarea
     * Attach receipt (file upload, optional)
   
   - Display:
     * Original amount due
     * Previous payments
     * New balance after payment
   
   - Actions:
     * Submit Payment button
     * Save as Draft button
     * Cancel button

5. Payments History/Calendar View
   - Month view calendar
   - Payments highlighted on calendar
   - Color coding:
     * Green: Paid
     * Yellow: Partial
     * Red: Overdue/Missed
     * Gray: Upcoming
   
   - Click on date to see payments
   - Toggle to list view

Design Elements:
- Progress bars showing payment completion
- Color-coded status badges
- Clear financial calculations shown
- Responsive tables with horizontal scroll on mobile
- Keyboard shortcuts for quick payment entry
```

---

## 8. Reports & Analytics

### Prompt: Reports and Analytics Dashboard

```
Design the Reports and Analytics section for Propti.

Screens to Create:

1. Reports Dashboard
   - Quick report buttons (generate one-click reports):
     * Monthly Revenue Report
     * Tenant Balances Report
     * Payment Status Report
     * Property Performance Report
   
   - Custom Report Builder:
     * Select date range
     * Select property/properties
     * Select metrics to include
     * Export format (PDF, Excel)
     * Generate button
   
   - Recent Reports List:
     * Report name, date generated, file size
     * Download button
     * Delete button
     * View button

2. Monthly Revenue Report
   Header:
   - Selected date range
   - Total revenue collected
   - Comparison with previous period (% change)
   
   Content:
   - Revenue by property (table or chart)
     * Property name, total collected, % of total revenue
   
   - Revenue trend chart (line graph)
     * Last 12 months revenue
   
   - Collection rate:
     * % of expected revenue collected
     * Visual gauge
   
   - Top performing properties
   
   Export: PDF, Excel buttons

3. Tenant Balances Report
   - Summary stats:
     * Total amount owed by all tenants
     * Number of tenants with balance owed
     * Average balance per tenant
   
   - Table of all tenants:
     * Tenant name
     * Property/Room
     * Total owed
     * Age of oldest debt
     * Status
   
   - Visualization:
     * Balance distribution chart
     * Breakdown by age (0-30 days, 30-60 days, 60+ days)
   
   - Priority list: Most urgent balances to collect

4. Payment Status Report
   - Overview Dashboard:
     * Paid (on time): number and % of cycles
     * Paid (late): number and % of cycles
     * Partial: number and % of cycles
     * Overdue: number and % of cycles
     * Breakdown pie chart
   
   - Payment Methods Breakdown:
     * Cash, Mobile Money, Bank
     * Count and total amount per method
   
   - Tenant Payment Reliability:
     * Table ranking tenants by payment reliability
     * On-time payment %, average payment delay

5. Property Performance Report
   - Per-property breakdown:
     * Occupancy rate
     * Revenue generated
     * Collection rate
     * Number of tenants
     * Average rent per room
   
   - Comparative charts:
     * Properties ranked by revenue
     * Properties ranked by occupancy
     * Properties ranked by collection rate

Design Elements:
- Use charts (line, bar, pie) for data visualization
- Summary cards with key metrics
- Color-coded trends (green for up, red for down)
- Export buttons for PDF/Excel
- Responsive charts that work on mobile
- Printable layouts
```

---

## 9. Settings & User Profile

### Prompt: Settings and User Profile Screen

```
Design the Settings and User Profile screens for Propti.

Screens to Create:

1. User Profile Screen
   - Profile Header:
     * User avatar (editable, upload new photo)
     * Full name (editable)
     * Email (display only)
     * Phone number (editable)
     * Member since date
   
   - Profile Completion:
     * Progress bar showing % complete
     * Suggestions for missing info
   
   - Edit Profile Section:
     * Full name input
     * Phone number input
     * Save Changes button
     * Cancel button

2. Notification & Reminder Settings
   - Payment Reminder Settings:
     * Enable/Disable payment reminders (toggle)
     * Reminder timing options:
       - 1 day before due date
       - On due date
       - Days after due date (overdue)
     * Reminder method checkboxes:
       - Email
       - SMS
       - In-app notification
   
   - Reminder Interval Preference:
     * Weekly/Monthly/Custom
     * Preferred day/time for digest
   
   - Other Notifications:
     * New tenant registration confirmations
     * Payment received notifications
     * System alerts and updates
   
   - Save Preferences button

3. Account & Security Settings
   - Change Password:
     * Current password input
     * New password input
     * Confirm password input
     * Password strength indicator
     * Change Password button
   
   - Two-Factor Authentication:
     * Status toggle (enabled/disabled)
     * Setup instructions if disabled
     * Backup codes display
     * Regenerate codes button
   
   - Active Sessions:
     * List of logged-in devices
     * Device name, location, last active
     * Logout from device button
     * "Logout from all devices" button
   
   - Login History:
     * Table of recent logins
     * Date, time, device, IP address

4. Subscription & Billing (if applicable)
   - Current Plan:
     * Plan name and features
     * Billing cycle
     * Next billing date
     * Upgrade/Downgrade buttons
   
   - Billing History:
     * Table of invoices
     * Date, amount, status, download link
   
   - Payment Method:
     * Current payment method
     * Add/Update payment method
     * Billing address

5. Help & Support
   - FAQ link
   - Contact Support button
   - User Guide link
   - Version information
   - Report a Bug link

6. Logout Confirmation
   - Confirmation message
   - Confirm/Cancel buttons

Design Elements:
- Toggle switches for on/off settings
- Clear section headers
- Info icons for explanations
- Save/Cancel buttons at section level
- Success messages after save
- Responsive form layout
- Password strength meter (visual indicator)
```

---

## 10. Mobile-Specific Screens

### Prompt: Mobile App Navigation & Quick Actions

```
Design mobile-specific screens and navigation for Propti mobile app.

Mobile-First Design Principles:
- Single-column layout
- Bottom navigation bar (5 main tabs)
- Touch-friendly buttons (min 44px height)
- Large, readable text
- Swipe gestures where appropriate

Screens to Create:

1. Bottom Navigation Bar
   Tabs (left to right):
   - Dashboard (home icon) - default active
   - Properties (building icon)
   - Tenants (people icon)
   - Payments (wallet icon)
   - Settings (gear icon)
   
   - Badges on icons for notifications/pending items

2. Mobile Dashboard
   - Simplified summary cards:
     * Total revenue (this month)
     * Overdue payments (count, tappable)
     * Upcoming due dates (count)
   
   - Quick action buttons (large, full-width):
     * Record Payment
     * Add Tenant
     * View Properties
   
   - Recent activity feed
   - Notifications list

3. Mobile Property List
   - Search bar at top
   - Property cards (full-width):
     * Property image
     * Name and location
     * Room count and occupancy %
     * Monthly revenue
     * Tap to view details
   
   - Add Property floating action button (FAB)

4. Mobile Tenant Quick View
   - Search/filter at top
   - Tenant cards:
     * Avatar and name
     * Phone number (tappable for call)
     * Current balance
     * Status
     * Swipe for quick actions (edit, archive)

5. Mobile Quick Payment Entry
   - Simplified payment form:
     * Tenant selector (searchable)
     * Amount input
     * Payment method (radio buttons)
     * Submit button
   
   - Success confirmation with auto-print receipt

6. Mobile Reports
   - Simplified report cards:
     * Revenue this month
     * Collection rate
     * Overdue amount
     * Tap for detailed view
   
   - One-touch PDF generation
   - Share report button

Design Considerations:
- Responsive touch targets (no small buttons)
- Minimize form fields per screen
- Use native mobile features (camera for receipts, phone call)
- Fast loading times (optimize images)
- Offline support for basic operations
- Deep linking between screens
```

---

## 11. Error States & Empty States

### Prompt: Error Handling and Empty State Screens

```
Design error messages and empty state screens for better UX.

Screens to Create:

1. Empty State Screens
   
   A. No Properties Yet
   - Empty state illustration (house/building icon)
   - Headline: "No properties yet"
   - Description: "Start managing your properties by adding your first one"
   - Large "Add Property" button
   
   B. No Tenants Yet
   - Empty state illustration (people icon)
   - Headline: "No tenants yet"
   - Description: "Add your first tenant to get started"
   - Large "Add Tenant" button
   
   C. No Payments Yet
   - Empty state illustration (wallet icon)
   - Headline: "No payment history"
   - Description: "Payments will appear here once you record them"
   - Link to "Record Payment"
   
   D. No Reports Generated
   - Empty state illustration (chart icon)
   - Headline: "No reports yet"
   - Description: "Generate your first report to get insights"
   - "Generate Report" button

2. Error State Screens
   
   A. Database Connection Error
   - Error icon
   - Headline: "Unable to Connect"
   - Message: "We're having trouble connecting to the server"
   - "Retry" button
   - "Offline Mode" button (if available)
   
   B. 404 Not Found
   - Error icon
   - Headline: "Page Not Found"
   - Message: "The page you're looking for doesn't exist"
   - "Go Back" button
   - "Go to Dashboard" button
   
   C. 403 Unauthorized
   - Error icon
   - Headline: "Access Denied"
   - Message: "You don't have permission to access this resource"
   - "Go Back" button
   
   D. Server Error (500)
   - Error icon
   - Headline: "Something Went Wrong"
   - Message: "Our servers are experiencing issues. Please try again later"
   - "Retry" button
   - "Contact Support" button

3. Validation Error Messages
   - Display inline with form fields
   - Red border on field
   - Red error icon
   - Clear error message below field
   - Examples:
     * "Email is required"
     * "Invalid email format"
     * "Password must be at least 8 characters"
     * "Phone number must be 10 digits"

4. Toast Notifications (top/bottom of screen)
   
   A. Success Toast
   - Green icon
   - Message: "Payment recorded successfully"
   - Auto-dismiss in 3 seconds
   - Close button
   
   B. Error Toast
   - Red icon
   - Message with error details
   - Stays until user closes
   - Retry button if applicable
   
   C. Warning Toast
   - Yellow icon
   - Message: "This action cannot be undone"
   - Action buttons
   
   D. Info Toast
   - Blue icon
   - Informational message
   - Auto-dismiss

5. Loading States
   - Skeleton screens for data loading
   - Animated loading spinner
   - Progress bar for file uploads
   - "Loading..." text for accessibility

6. Confirmation Dialogs
   
   A. Delete Confirmation
   - Icon: warning triangle
   - Headline: "Are you sure?"
   - Message: "This action cannot be undone"
   - Red "Delete" button
   - Gray "Cancel" button
   
   B. Archive Confirmation
   - Icon: archive icon
   - Message: "Archive this tenant?"
   - Info about what archiving means
   - "Archive" and "Cancel" buttons

Design Elements:
- Use appropriate icons for each state
- Clear, friendly messaging
- Action buttons with proper CTA
- Avoid technical jargon
- Responsive layouts
- Accessible color contrasts
```

---

## 12. Advanced Features: Notifications & Reminders UI

### Prompt: Notifications Center and Reminder Management

```
Design the Notifications Center and Reminder Management interface.

Screens to Create:

1. Notifications Center (Bell Icon Dropdown)
   - Notification count badge on bell icon
   - Dropdown panel showing recent notifications:
     * Notification icon
     * Message text
     * Time elapsed (e.g., "2 hours ago")
     * Unread indicator (dot)
     * Quick action or link
   
   - Pagination/scroll for more notifications
   - "Mark all as read" button
   - "Clear all" button
   - "Go to Notifications" link (full screen)

2. Full Notifications Screen
   - Filter tabs:
     * All
     * Unread
     * Payments
     * Tenants
     * System
   
   - Sort by: Newest first, oldest first
   
   - Notification list with:
     * Icon per notification type
     * Full message
     * Time and date
     * Read/unread status
     * Delete button
     * Archive button
   
   - Search notifications
   - Bulk actions (select multiple, delete, mark read)

3. Reminders Dashboard
   - Upcoming Reminders:
     * Cards showing:
       - Reminder type icon
       - Tenant/Property name
       - Due date and time
       - "Dismiss" or "Mark Complete" button
   
   - Scheduled Reminders List:
     * Table with:
       - Reminder title
       - Scheduled for (date/time)
       - Frequency (one-time, daily, weekly, monthly)
       - Recipients (tenant, landlord)
       - Status (Active, Paused, Completed)
       - Action buttons (edit, delete, pause)
   
   - "Create Reminder" button

4. Create/Edit Reminder Modal
   - Reminder Type:
     * Payment reminder
     * Custom message
     * Inspection reminder
   
   - Target Selection:
     * Specific tenant
     * Specific property
     * Specific room
   
   - Schedule:
     * One-time or recurring
     * Date and time picker
     * Recurrence options (daily, weekly, monthly, custom)
     * End date for recurring (optional)
   
   - Message:
     * Customizable message template
     * Preview how it looks
   
   - Notification Methods:
     * Email checkbox
     * SMS checkbox
     * In-app notification checkbox
   
   - Save/Cancel buttons

5. Notification Preferences (in Settings)
   - Notification Types Toggles:
     * Payment reminders
     * Overdue alerts
     * New tenant notifications
     * System updates
     * Marketing emails
   
   - Notification Frequency:
     * Real-time
     * Hourly digest
     * Daily digest
     * Weekly digest
   
   - Quiet Hours:
     * Enable/disable
     * Start time and end time
     * Still show critical alerts toggle
   
   - Save Preferences button

Design Elements:
- Color-coded notification types (icons and badges)
- Time indicators (relative time like "2 hours ago")
- Unread notification indicator
- Swipe to dismiss (mobile)
- Notification badges on navigation items
- Animation for incoming notifications
- Sound/vibration options
```

---

## General Design Guidelines

### Tone & Voice
- **Professional yet approachable**: Use clear, jargon-free language
- **Action-oriented**: Buttons use strong action verbs ("Record Payment", "Add Property")
- **Helpful**: Provide context and guidance in empty states and errors
- **Reassuring**: Security and data protection messaging when needed

### Accessibility Requirements
- **Color Contrast**: Minimum WCAG AA (4.5:1 for text)
- **Text Alternatives**: All icons have labels or alt text
- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **Screen Readers**: Proper semantic HTML and ARIA labels
- **Motion**: Reduce animation options for users with vestibular disorders
- **Font Sizes**: Minimum 16px for body text on mobile

### Performance Considerations
- **Fast Load Times**: Lazy load images, optimize assets
- **Smooth Animations**: 60 FPS animations
- **Responsive Images**: Different sizes for different devices
- **Offline Capability**: Cache critical data for offline access

### Visual Hierarchy
- **Clear Primary Actions**: Most important buttons are prominent
- **Scannable Content**: Use headings, short paragraphs, white space
- **Visual Balance**: Not too cluttered, not too sparse
- **Consistent Styling**: Cohesive design across all screens

---

## Tips for Using These Prompts with Stitch AI

1. **Customize for Your Brand**: Replace color codes and styling preferences with your brand guidelines
2. **Prioritize Screens**: Start with authentication and dashboard, then expand to other screens
3. **Iterate**: Use multiple prompt runs to refine design details
4. **Combine Prompts**: Merge related prompts for comprehensive section designs
5. **Request Variants**: Ask for light/dark mode variants and mobile/desktop versions
6. **Export Options**: Request design files in your preferred format (Figma, XD, etc.)
7. **Component Specs**: Ask for component specifications including spacing, sizing, and interactions

---

## 13. MASTER INTEGRATION PROMPT: Complete App Cohesion & System Design

### Prompt: Propti Complete Design System Integration & User Experience Flow

```
You have already generated all the UI screens for Propti (authentication, dashboard, properties, 
rooms, tenants, rent cycles, payments, reports, settings, mobile views, error/empty states, and 
notifications). Now create a comprehensive design system integration document that binds all these 
screens together into a seamless, unified product experience.

OVERVIEW:
This is the final integration layer that ensures every screen, component, and interaction works 
cohesively. The app should feel like a single, well-crafted product rather than disconnected screens.

====================================================================================
SECTION 1: DESIGN SYSTEM STANDARDIZATION
====================================================================================

1.1 COLOR SYSTEM ACROSS ALL SCREENS
   - Primary Blue (#2563EB): Used consistently for:
     * Primary buttons across all screens
     * Navigation highlights
     * Active states
     * Links and CTAs
     * Focus indicators
   
   - Success Green (#10B981): Used consistently for:
     * Paid payment badges
     * Successful operations (toast notifications)
     * Active/positive status indicators
     * Occupied room indicators
     * Up/positive trend indicators
   
   - Warning Yellow (#F59E0B): Used consistently for:
     * Partial payment badges
     * Upcoming/due soon indicators
     * Warning toasts
     * Cautionary information
     * Pending status
   
   - Danger Red (#EF4444): Used consistently for:
     * Overdue badges
     * Delete/destructive buttons
     * Error states
     * Error toasts
     * Vacancy indicators
     * Down/negative trends
   
   - Neutral Grays: Used consistently for:
     * Inactive/disabled states
     * Secondary text
     * Dividers and borders
     * Neutral badges
     * Background colors
   
   - Ensure these colors are applied identically across:
     * All list views (properties, tenants, rooms, payments, rent cycles)
     * All detail views
     * All status badges throughout the app
     * All chart/graph legends
     * All form validation states

1.2 TYPOGRAPHY SYSTEM ACROSS ALL SCREENS
   - Font Family: Inter or Poppins (consistent across all screens)
   
   - Heading Hierarchy (consistent across dashboard, detail views, modals):
     * H1 (32px, bold, 140% line-height): Page titles (Dashboard, Properties, Tenants)
     * H2 (24px, bold, 130% line-height): Section headers, modal titles
     * H3 (20px, semi-bold, 130% line-height): Card titles, sub-sections
     * H4 (16px, semi-bold, 120% line-height): Form labels, widget headers
     * Body (14px, regular, 150% line-height): Body text, descriptions
     * Small (12px, regular, 140% line-height): Secondary text, metadata
     * Caption (11px, regular, 140% line-height): Timestamps, helper text
   
   - Apply consistently to:
     * All page headers
     * All section headers
     * Form labels across authentication, property forms, tenant forms, payment forms
     * Card titles in list views
     * Table headers
     * Modal titles
     * Help text and descriptions
   
   - Maintain consistent font weights throughout:
     * Bold: Page titles, important labels
     * Semi-bold: Section headers, form labels
     * Regular: Body text, descriptions

1.3 SPACING SYSTEM (8px GRID) ACROSS ALL SCREENS
   - Base unit: 8px
   - Standard spacing values (consistent everywhere):
     * xs: 4px (very small gaps, icon spacing)
     * sm: 8px (small gaps, form field spacing)
     * md: 16px (standard spacing, card padding, section gaps)
     * lg: 24px (large gaps, major section separation)
     * xl: 32px (page-level spacing)
     * 2xl: 48px (hero sections, major breaks)
   
   - Apply consistently to:
     * Padding on all cards (16px or 24px)
     * Margins between list items (8px or 16px)
     * Form field spacing (16px gap between fields)
     * Section separation (24px or 32px)
     * Modal padding (24px or 32px)
     * Navigation spacing
     * Button padding (8px vertical, 16px horizontal minimum)
   
   - Maintain consistent spacing ratios in:
     * Table row heights (56px standard)
     * Card heights (proportional to 8px grid)
     * Input field heights (44px for mobile touch, 40px for desktop)

1.4 COMPONENT CONSISTENCY ACROSS ALL SCREENS
   
   A. Button System (consistent across ALL screens):
   - Primary Button:
     * Blue background (#2563EB)
     * White text
     * 44px height (mobile), 40px (desktop)
     * 16px horizontal padding
     * Used for: Main CTAs, Record Payment, Create Property, Add Tenant, Save, etc.
     * Hover: Darker blue (#1D4ED8)
     * Active: Even darker (#1E40AF)
     * Disabled: Gray with reduced opacity
   
   - Secondary Button:
     * White/Gray background with blue border
     * Blue text
     * Same sizing as primary
     * Used for: Cancel, Back, View More, etc.
     * Hover: Light blue background
   
   - Danger Button:
     * Red background (#EF4444)
     * White text
     * Same sizing
     * Used for: Delete, Archive, Logout
     * Hover: Darker red (#DC2626)
   
   - Disabled State (all buttons):
     * Reduced opacity (50%)
     * No hover effects
     * Gray color scheme
     * Applied consistently across forms and lists
   
   - Button text: Clear, action-oriented verbs
     * "Record Payment", "Add Property", "Save Changes"
     * "Cancel", "Back", "Close"
     * "Delete", "Archive"
   
   - Button spacing: Consistent padding and corner radius (8px) everywhere

   B. Card Component (consistent across ALL list views):
   - Border: 1px light gray
   - Border-radius: 8px
   - Padding: 16px or 24px (consistent with spacing system)
   - Shadow: Subtle shadow (0 1px 3px rgba(0,0,0,0.1))
   - Hover: Slight elevation, shadow increase
   - Background: White (light mode), Dark gray (dark mode)
   - Used for: Property cards, tenant cards, room cards, payment cards, rent cycle cards
   - Card title styling: Consistent H3 or H4
   - Card metadata: Consistent small/caption text color

   C. Input Fields (consistent across ALL forms):
   - Height: 40px (desktop), 44px (mobile)
   - Border: 1px solid light gray
   - Border-radius: 6px
   - Padding: 8px 12px
   - Font-size: 14px
   - Placeholder color: Light gray
   - Focus: Blue border (#2563EB), subtle shadow
   - Error state: Red border, red error icon, red error message below
   - Disabled: Gray background, reduced opacity
   - Applied consistently in:
     * Login/registration forms
     * Property creation forms
     * Tenant forms
     * Payment forms
     * Search/filter bars
     * Settings forms

   D. Modal/Overlay System (consistent across ALL modals):
   - Overlay background: Black with 50% opacity
   - Modal background: White (light mode), Dark gray (dark mode)
   - Modal border-radius: 8px
   - Modal padding: 24px or 32px
   - Modal shadow: Strong shadow (0 20px 25px rgba(0,0,0,0.15))
   - Modal header: H2 font size, bold, 24px bottom margin
   - Modal body: Regular text, 14px
   - Modal footer: Buttons right-aligned, 16px gap between buttons
   - Close button: Top-right corner, X icon
   - Applied consistently for:
     * Add/Edit property modals
     * Add/Edit room modals
     * Add/Edit tenant modals
     * Create rent cycle modals
     * Confirmation dialogs
     * Settings modals

   E. Badge/Status Indicator System (consistent across ALL screens):
   - Badge sizing: 8px padding, 6px border-radius, 12px font size
   - Badge colors:
     * Green background, dark green text: Paid/Active/Success
     * Yellow background, orange text: Partial/Pending/Warning
     * Red background, dark red text: Overdue/Inactive/Error
     * Gray background, dark gray text: Neutral/Vacant/Disabled
   - Applied consistently to:
     * Payment status badges
     * Tenant status badges
     * Room occupancy badges
     * Property status badges
     * Account status badges

   F. Table System (consistent across ALL tables):
   - Header row: Bold font, light gray background, bottom border
   - Data rows: 56px height, alternating white/very light gray rows
   - Row hover: Light blue background
   - Cell padding: 16px
   - Border: 1px light gray dividers between rows
   - Text alignment: Left for names/text, right for numbers
   - Action column: Right-aligned, icon buttons or dropdown menu
   - Responsive: Horizontal scroll on mobile, full width on desktop
   - Applied consistently to:
     * Rooms list
     * Rent cycles list
     * Payments history
     * Tenants list
     * Notification list
     * Report tables

   G. Form Layout (consistent across ALL forms):
   - Form section headers: H4 font size, 24px top margin
   - Form field groups: 16px spacing between fields
   - Label positioning: Above input, bold, required indicator (*)
   - Helper text: Below input, small font, gray color
   - Error messages: Below input, red text, red icon
   - Checkbox/radio spacing: 8px gap between label and input
   - Form padding: 24px or 32px
   - Applied consistently in:
     * Authentication forms
     * Property forms
     * Tenant forms
     * Payment forms
     * Settings forms

====================================================================================
SECTION 2: NAVIGATION & FLOW CONSISTENCY
====================================================================================

2.1 SIDEBAR/NAVIGATION CONSISTENCY
   - Navigation items: Consistent icon + text layout
   - Active state: Blue background, white text
   - Hover state: Light blue background
   - Icon sizing: 20px, consistent across all nav items
   - Text sizing: 14px, consistent across all nav items
   - Item height: 44px, consistent spacing
   - Font: Semi-bold when active, regular when inactive
   - Applied to: Dashboard, Properties, Rooms, Tenants, Rent Cycles, Payments, Reminders, Reports, Settings
   - Collapsible on mobile: Same styling, hamburger menu animation consistent

2.2 BREADCRUMB NAVIGATION (where applicable)
   - Font-size: 12px
   - Text color: Gray for inactive, blue for active/current
   - Separator: "/" or ">"
   - Positioning: Top of page, below main header
   - Applied consistently when:
     * Viewing property details from properties list
     * Viewing tenant details from tenants list
     * Viewing room details from property view
     * Viewing payment details from payment history

2.3 BACK BUTTON CONSISTENCY
   - Icon: Left arrow
   - Text: "Back" or page name
   - Positioning: Top-left below header
   - Styling: Secondary button style (white/gray with border)
   - Applied consistently across:
     * All detail views
     * All modal close actions
     * All nested views

2.4 HEADER CONSISTENCY ACROSS PAGES
   - Top navigation bar layout: Logo | Search | Notifications | User Menu | Dark Mode
   - Height: 64px
   - Background: White (light mode), dark gray (dark mode)
   - Shadow: Subtle bottom shadow
   - Logo sizing: 32px height
   - Icons sizing: 20px
   - Search bar width: 300px (desktop), full width (mobile)
   - Applied consistently across:
     * Dashboard
     * Properties page
     * Tenants page
     * Payments page
     * Reports page
     * Settings page

2.5 USER FLOW CONSISTENCY
   - Create operations flow: List view → "Add" button → Modal form → Submit → Success toast → Back to list
   - Edit operations flow: List view → Click item → Detail view → "Edit" button → Modal form → Submit → Success toast → Back to detail
   - Delete operations flow: List view → Click item → "Delete" button → Confirmation modal → Success toast → Back to list
   - View operations flow: List view → Click item → Detail view with related information
   - Applied consistently for:
     * Properties CRUD
     * Rooms CRUD
     * Tenants CRUD
     * Rent Cycles CRUD
     * Payments CRUD

====================================================================================
SECTION 3: INTERACTIVE BEHAVIORS & ANIMATIONS
====================================================================================

3.1 TRANSITION & ANIMATION CONSISTENCY
   - Page transitions: Smooth fade in (200ms)
   - Modal appearances: Slide up from bottom (300ms)
   - Button interactions: Instant color change on hover, press feedback on click
   - List item hover: Subtle elevation (100ms transition)
   - Loading states: Skeleton screens fade in, spinners rotate continuously
   - Toast notifications: Slide in from top (300ms), slide out on dismiss (200ms)
   - Success animations: Brief checkmark animation (500ms)
   - Applied consistently across ALL interactive elements

3.2 HOVER STATES CONSISTENCY
   - Buttons: Color darkens, slight scale increase (1.02x)
   - Cards: Shadow increases, background lightens slightly
   - Links: Color darkens, underline appears
   - Table rows: Light background color change
   - Icons: Slight rotation or color change
   - Applied consistently to make all interactive elements discoverable

3.3 LOADING STATES CONSISTENCY
   - Page loading: Full-page skeleton with approximate layout
   - List loading: Card skeletons (3-5 visible)
   - Form loading: Grayed-out with spinner in button
   - Data refresh: Subtle loading indicator with "Refreshing..." text
   - Applied consistently across:
     * Dashboard data load
     * List views
     * Detail views
     * Form submissions
     * Report generation

3.4 LOADING INDICATOR STYLING
   - Spinner animation: Rotating circle, blue color, 24px size
   - Skeleton screens: Animated gradient (left to right)
   - Progress bars: Blue fill, gray background
   - Applied consistently with:
     * Same animation speed (1.5s)
     * Same color scheme (blue primary)
     * Same sizing relative to content

3.5 DROPDOWN & SELECT CONSISTENCY
   - Styling: Same as input fields (40px height, blue focus)
   - Icon: Chevron down, right-aligned
   - Options list: Blue highlight on hover
   - Applied consistently across:
     * Payment method selector
     * Property selector
     * Tenant selector
     * Room selector
     * Filter/sort dropdowns

3.6 CONFIRMATION & DESTRUCTIVE ACTION PATTERN
   - Pattern: Icon (warning triangle) → Headline → Description → Buttons
   - Headline: Clear, bold question (e.g., "Are you sure?")
   - Description: Explain consequences clearly
   - Buttons: Red for destructive, Gray for cancel
   - Applied consistently for:
     * Delete operations
     * Archive operations
     * Logout operations
     * Clear all operations

====================================================================================
SECTION 4: DARK MODE CONSISTENCY
====================================================================================

4.1 DARK MODE COLOR MAPPING
   - Background: #1F2937 (dark gray)
   - Surface (cards): #111827 (darker)
   - Text primary: #F3F4F6 (light gray)
   - Text secondary: #D1D5DB (medium gray)
   - Border: #374151 (medium gray)
   - Primary blue: #3B82F6 (lighter blue for visibility)
   - Apply consistently to:
     * All backgrounds
     * All cards
     * All text
     * All borders
     * All input fields
     * All modals

4.2 DARK MODE STATUS COLORS
   - Success green: #34D399 (lighter for dark mode)
   - Warning yellow: #FBBF24 (lighter for dark mode)
   - Error red: #F87171 (lighter for dark mode)
   - Applied consistently to all badges and status indicators

4.3 DARK MODE TRANSITIONS
   - Toggle transition: Smooth fade (300ms)
   - All elements change simultaneously
   - No visual glitches or partial updates
   - Applied consistently across all screens

4.4 IMAGE & ICON HANDLING IN DARK MODE
   - Icons: Use light colors (white or light gray)
   - Photos: Add subtle overlay or adjust contrast
   - Charts: Adjust colors for visibility
   - Applied consistently to maintain readability

====================================================================================
SECTION 5: RESPONSIVE DESIGN CONSISTENCY
====================================================================================

5.1 BREAKPOINTS (consistent across all screens)
   - Mobile: 320px - 640px (single column, bottom nav)
   - Tablet: 641px - 1024px (sidebar collapses, 2-column layout)
   - Desktop: 1025px+ (sidebar visible, full features)

5.2 NAVIGATION RESPONSIVE BEHAVIOR
   - Mobile: Hamburger menu, bottom tab navigation
   - Tablet: Collapsible sidebar, visible on toggle
   - Desktop: Always-visible sidebar
   - Applied consistently across all pages

5.3 LIST VIEW RESPONSIVE BEHAVIOR
   - Mobile: Card view, single column, full width
   - Tablet: Card view, 2 columns or table with scroll
   - Desktop: Table view with all columns visible
   - Applied consistently to:
     * Properties list
     * Tenants list
     * Rooms list
     * Payments list
     * Rent cycles list

5.4 FORM RESPONSIVE BEHAVIOR
   - Mobile: Full-width fields, stacked vertically
   - Tablet: Fields in 2 columns where appropriate
   - Desktop: Fields in 2-3 columns
   - Labels: Always above fields (mobile), can be beside (desktop)
   - Applied consistently to all forms

5.5 MODAL RESPONSIVE BEHAVIOR
   - Mobile: Full-screen or 90% viewport with margin
   - Tablet: 80% viewport width
   - Desktop: 50-60% viewport width
   - Applied consistently to all modals

5.6 CHART/GRAPH RESPONSIVE BEHAVIOR
   - Mobile: Single chart per view, vertical layout
   - Tablet: 1-2 charts per row
   - Desktop: 2-3 charts per row
   - Charts adapt to container width automatically

5.7 TOUCH TARGET SIZING
   - Mobile: Minimum 44px height for all interactive elements
   - Tablet: Minimum 40px
   - Desktop: Minimum 40px
   - Applied consistently to buttons, links, selects, checkboxes

====================================================================================
SECTION 6: FORM VALIDATION & ERROR HANDLING
====================================================================================

6.1 INPUT VALIDATION STYLING (consistent across ALL forms)
   - Default state: Gray border, normal text
   - Focus state: Blue border (#2563EB), blue outline glow
   - Filled state: Blue border, normal text
   - Error state: Red border, red error icon, red text message below
   - Success state: Green border, green checkmark icon
   - Disabled state: Gray background, gray border, reduced opacity
   - Applied consistently to:
     * Text inputs (email, password, name, etc.)
     * Number inputs (amount, phone number, etc.)
     * Dropdown selects
     * Date pickers
     * Textarea fields

6.2 ERROR MESSAGE DISPLAY (consistent pattern)
   - Message position: Below input field
   - Icon: Red X or alert icon (left)
   - Text: "Field name is required" or specific validation message
   - Font-size: 12px
   - Color: Red (#EF4444)
   - Applied consistently in:
     * Authentication forms
     * Property forms
     * Tenant forms
     * Payment forms
     * Settings forms

6.3 SUCCESS FEEDBACK (consistent pattern)
   - Toast notification: Green background, checkmark icon, message
   - Position: Top center or top-right
   - Duration: 3-5 seconds auto-dismiss
   - Message examples: "Property created successfully", "Payment recorded", "Settings saved"
   - Applied consistently after:
     * Successful form submissions
     * Successful CRUD operations
     * Settings updates

6.4 ERROR FEEDBACK (consistent pattern)
   - Toast notification: Red background, X icon, error message
   - Position: Top center or top-right
   - Duration: Sticky (user must close) for critical errors
   - Message: Clear, actionable description of issue
   - Retry button: If applicable
   - Applied consistently for:
     * API errors
     * Validation errors
     * Network errors
     * Permission errors

6.5 FORM SUBMISSION STATES
   - Default: Button text "Save", "Submit", "Record Payment"
   - Loading: Button disabled, spinner inside, text hidden
   - Error: Button highlighted red, error message displayed
   - Success: Brief confirmation, redirect or list refresh
   - Applied consistently across all forms

====================================================================================
SECTION 7: DATA VISUALIZATION CONSISTENCY
====================================================================================

7.1 CHART COLOR SCHEME (consistent across ALL charts)
   - Primary data: Blue (#2563EB)
   - Success/Positive: Green (#10B981)
   - Warning/Partial: Yellow (#F59E0B)
   - Error/Negative: Red (#EF4444)
   - Secondary data: Gray (#9CA3AF)
   - Applied consistently to:
     * Revenue charts
     * Payment status pie charts
     * Occupancy charts
     * Collection rate gauges
     * Trend lines

7.2 CHART STYLING CONSISTENCY
   - Font: Same as body text (Inter, 12px)
   - Legend: Bottom or right-aligned, clear labels
   - Axis labels: Clear, properly scaled
   - Grid lines: Light gray, subtle
   - Tooltip: Dark background, white text, rounded corners
   - Applied consistently across:
     * Line charts
     * Bar charts
     * Pie charts
     * Gauge charts
     * Area charts

7.3 TABLE DATA VISUALIZATION
   - Header background: Light gray (#F3F4F6)
   - Row alternating: White and very light gray (#F9FAFB)
   - Text alignment: Left for text, right for numbers
   - Number formatting: Currency with symbol, percentages with %
   - Date formatting: Consistent format (e.g., "Jan 15, 2025")
   - Applied consistently to all data tables

7.4 METRIC CARD CONSISTENCY
   - Title: Bold, H4 font size
   - Value: Large, bold, in primary color
   - Subtitle: Small, gray, context about the metric
   - Trend indicator: Up/down arrow with color (green for up, red for down)
   - Background: White or light gray
   - Applied consistently to:
     * Dashboard metrics
     * Report summaries
     * Property performance stats
     * Tenant balance cards

====================================================================================
SECTION 8: ACCESSIBILITY CONSISTENCY
====================================================================================

8.1 COLOR CONTRAST ACROSS ALL TEXT
   - Ensure WCAG AA minimum (4.5:1 for normal text, 3:1 for large text)
   - Applied consistently to:
     * All body text (dark text on light background)
     * All headings
     * All button text
     * All status badges
     * All error messages

8.2 FOCUS INDICATORS CONSISTENCY
   - Visible focus outline: 2px blue border with 2px offset
   - Applied to all interactive elements:
     * Buttons
     * Links
     * Form inputs
     * Checkboxes/radios
     * Dropdowns
   - No hidden focus states
   - Keyboard navigation clearly visible

8.3 ALT TEXT & LABELS
   - All icons have aria-labels or title attributes
   - All images have alt text
   - All form inputs have associated labels
   - All buttons have clear text or aria-labels
   - All tables have proper headers
   - Applied consistently throughout app

8.4 SEMANTIC HTML
   - Proper heading hierarchy (H1, H2, H3, etc.)
   - List elements for navigation and data lists
   - Form elements for data entry
   - Button elements for actions
   - Applied consistently across all pages

8.5 SCREEN READER SUPPORT
   - Announce loading states: "Loading properties..."
   - Announce errors: "Error: Email is required"
   - Announce success: "Payment recorded successfully"
   - Navigation landmarks: Main, nav, aside, footer
   - Live regions for dynamic content updates

====================================================================================
SECTION 9: NOTIFICATION & ALERT CONSISTENCY
====================================================================================

9.1 TOAST NOTIFICATION TYPES (consistent styling across all)
   
   A. Success Toast
   - Background: Green (#D1FAE5)
   - Border: Green (#10B981)
   - Icon: Green checkmark
   - Text: Dark green (#065F46)
   - Position: Top-right or top-center
   - Duration: 3 seconds auto-dismiss
   - Examples: "Payment recorded", "Property created", "Settings saved"
   
   B. Error Toast
   - Background: Red (#FEE2E2)
   - Border: Red (#EF4444)
   - Icon: Red X or alert
   - Text: Dark red (#7F1D1D)
   - Position: Top-right or top-center
   - Duration: Sticky (no auto-dismiss)
   - Examples: "Unable to record payment", "Network error"
   
   C. Warning Toast
   - Background: Yellow (#FEF3C7)
   - Border: Yellow (#F59E0B)
   - Icon: Yellow warning triangle
   - Text: Dark yellow (#92400E)
   - Position: Top-right or top-center
   - Duration: 5 seconds auto-dismiss
   - Examples: "This action cannot be undone"
   
   D. Info Toast
   - Background: Blue (#DBEAFE)
   - Border: Blue (#3B82F6)
   - Icon: Blue info circle
   - Text: Dark blue (#1E40AF)
   - Position: Top-right or top-center
   - Duration: 4 seconds auto-dismiss
   - Examples: "New reminder created"

9.2 NOTIFICATION CENTER CONSISTENCY
   - Notification badge: Red dot in top-right of bell icon
   - Badge number: Only show count if > 0
   - Notification items: Same styling across all notification types
   - Unread indicator: Bold text, blue left border
   - Read indicator: Normal text, gray left border
   - Applied consistently to payment notifications, tenant alerts, system updates

9.3 ALERT BANNER CONSISTENCY
   - Used for: System-wide announcements, maintenance notices
   - Background: Blue (#DBEAFE)
   - Border: Blue (#3B82F6)
   - Icon: Blue info circle
   - Text: Dark blue (#1E40AF)
   - Close button: Optional, X icon
   - Position: Top of page, below header
   - Applied consistently for important notices

====================================================================================
SECTION 10: EMPTY & ERROR STATE CONSISTENCY
====================================================================================

10.1 EMPTY STATE LAYOUT (consistent across all)
   - Position: Centered, vertically and horizontally
   - Icon: Large (64px), light gray color
   - Headline: H2 font, 24px, bold
   - Description: 14px, gray text, 2-3 lines
   - CTA Button: Primary blue button below description
   - Applied consistently to:
     * No properties yet
     * No tenants yet
     * No payments yet
     * No reports generated
     * No notifications
     * No search results

10.2 ERROR STATE LAYOUT (consistent across all)
   - Position: Centered, full screen or modal
   - Icon: Large error icon (64px), red color
   - Headline: H2 font, "Something went wrong" or specific error
   - Description: 14px, gray text, explain what happened
   - Actions: "Retry" or "Go Back" buttons
   - Applied consistently for:
     * 404 Not Found
     * 403 Unauthorized
     * 500 Server Error
     * Connection errors
     * Timeout errors

10.3 OFFLINE STATE
   - Banner: Yellow/warning color at top of page
   - Message: "You are offline. Some features may be limited."
   - Status: Show last sync time
   - Actions: Cache available data for offline use
   - Applied consistently when network connection lost

====================================================================================
SECTION 11: MICRO-INTERACTIONS & POLISH
====================================================================================

11.1 BUTTON PRESS FEEDBACK
   - Visual: Scale down slightly (0.98x) on click
   - Duration: 100ms
   - Applied to all buttons for tactile feel

11.2 FORM INPUT FOCUS
   - Subtle scale increase (1.01x)
   - Shadow increase on focus
   - Duration: 150ms smooth transition
   - Applied to all form inputs

11.3 LIST ITEM INTERACTION
   - Hover: Light background, shadow increase
   - Click: Brief highlight, scale 0.99x
   - Active: Persistent highlight
   - Applied to all list items and table rows

11.4 MODAL APPEARANCE
   - Overlay fade in: 300ms
   - Modal slide up: 300ms with ease-out
   - Applied consistently to all modals

11.5 NOTIFICATION ANIMATION
   - Slide in from top: 300ms ease-out
   - Slide out on dismiss: 200ms ease-in
   - Auto-dismiss: Smooth fade out (200ms)
   - Applied consistently to all toasts and alerts

11.6 SKELETON SCREEN ANIMATION
   - Gradient animation: Left to right, 1.5s loop
   - Subtle shimmer effect
   - Applied to all loading states

====================================================================================
SECTION 12: PRINT DESIGN & EXPORT CONSISTENCY
====================================================================================

12.1 PRINT STYLING
   - Hide navigation (sidebar, header, bottom nav)
   - Hide action buttons (except print button which hides)
   - Dark text on white background
   - No interactive elements
   - Page breaks: Before major sections
   - Applied consistently to:
     * Report pages
     * Tenant profiles
     * Payment records

12.2 PDF EXPORT CONSISTENCY
   - Logo at top
   - Title and date
   - Data tables with clear headers
   - Charts/graphs rendered properly
   - Footer with "Generated by Propti" and timestamp
   - Applied consistently to all exportable reports

12.3 EXPORT FORMAT CONSISTENCY
   - PDF: Professional layout, logo, branding
   - Excel: Data table format, colors, formatting
   - CSV: Data only, no styling
   - Applied consistently across all reports

====================================================================================
SECTION 13: PERFORMANCE & OPTIMIZATION CONSISTENCY
====================================================================================

13.1 IMAGE OPTIMIZATION
   - Responsive images: Multiple sizes for different viewports
   - Format: WebP with fallbacks to JPG/PNG
   - Lazy loading: Images below fold load on scroll
   - Placeholders: Skeleton or low-res placeholder while loading
   - Applied consistently to:
     * Property photos
     * Tenant photos
     * Icons and illustrations

13.2 LOADING STATE MESSAGING
   - Always show what's loading: "Loading properties..."
   - Estimated time if known: "Loading... 2 of 5"
   - Progress: Use progress bars for long operations
   - Applied consistently to all data loads

13.3 ANIMATION PERFORMANCE
   - Use CSS transforms for smooth 60fps animations
   - GPU-accelerated transitions
   - Reduce animations on low-power devices
   - Applied consistently to all animated elements

====================================================================================
FINAL INTEGRATION CHECKLIST
====================================================================================

□ All screens use same color palette (blue, green, yellow, red, gray)
□ All text uses consistent typography (Inter/Poppins, same sizes)
□ All spacing follows 8px grid system
□ All buttons look and behave identically
□ All form inputs styled consistently
□ All modals have same structure and styling
□ All status badges use same colors/sizing
□ All tables formatted consistently
□ All empty states follow same pattern
□ All error states follow same pattern
□ All dark mode colors applied consistently
□ All responsive breakpoints implemented consistently
□ All animations and transitions consistent (timing, easing)
□ All accessibility requirements met across entire app
□ All notifications follow same style and behavior
□ Navigation works same way across all pages
□ Keyboard navigation works throughout entire app
□ Loading states consistent and clear
□ Success/error feedback consistent
□ Focus indicators visible everywhere
□ Print/export formatting works for all reports
□ Mobile experience optimized throughout

====================================================================================
DELIVERABLES
====================================================================================

This integration ensures:
1. Visual Cohesion: Every screen looks like part of the same product
2. Behavioral Consistency: Every interaction behaves predictably
3. User Experience: Users can navigate and use app intuitively
4. Accessibility: App is usable by all users regardless of ability
5. Professionalism: High-quality, polished product feel
6. Maintainability: Developers can easily maintain and update design
7. Scalability: Easy to add new screens/features that fit design system

The result is a unified, professional property management application where every 
screen, component, and interaction reinforces a cohesive brand and user experience.
```

---

## Next Steps After Design

1. Create interactive prototypes
2. Conduct user testing with actual landlords
3. Gather feedback and iterate
4. Develop design system documentation
5. Hand off to development team with proper specifications

