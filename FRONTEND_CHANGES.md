# Frontend Changes

This document covers the frontend changes made in `frontend-gateway/public/index.html`.

## Storefront UI

- Added responsive product cards with product name, price, quantity input, stock status, and purchase controls.
- Improved spacing and alignment across product cards, order rows, and action controls.
- Added visible borders and subtle shadows to product cards, the List a product card, active orders, and completed orders.
- Added responsive behavior for smaller screens.

## Product Inventory

- Added stock-aware quantity limits to product quantity inputs.
- Prevented customers from placing an order for more items than are currently in stock.
- Added stock status labels:
  - `In stock` when inventory is above 10.
  - `Low stock` when inventory is between 1 and 10.
  - `Out of stock` when inventory reaches 0.
- Disabled ordering controls when a product is out of stock.
- Added an Add stock button to every product card.
- Added a centered Add stock popup with validation, close behavior, and live product refresh after an update.

## Orders

- Displayed product names instead of only product IDs.
- Added order quantity editing and order deletion controls.
- Added total price calculation for each order.
- Added a Complete action for active orders.
- Added a separate Completed orders section.
- Added total, pending, and completed order counters in the Store at a glance panel.
- Updated the header Orders count to show total orders.
- Validated order quantities against current product stock before order creation, update, and completion.

## Add Product Popup

- Made the entire List a product card clickable.
- Replaced the inline product form with a centered popup.
- The popup is moved to the document body while open so it remains centered regardless of the card position or hover state.
- Added a darkened backdrop effect, close button, and popup entrance animation.
- Added spacing so the Add product title and close button share the same row.

## Branding

- Added a storefront warehouse logo before the GoodStock header name.
- Reused the logo as the browser tab favicon.
- Changed the browser tab title to `GoodStock`.
- Updated the visible brand name to `GoodStock`.

## Themes and Visual Styling

- Added a light-mode gradient that starts with a stronger light blue in the top-left and fades to white.
- Added a richer blue-navy gradient for dark mode.
- Added theme-aware graphite borders for dark mode so cards do not have harsh light edges.
- Added color-coded order summary values for total, pending, and completed orders.
- Preserved the existing theme toggle and reduced-motion support.

## Motion and Interaction

- Added staggered left-to-right entrance animations for product cards.
- Added a delayed slide-in animation for the Store at a glance panel.
- Added a pop-in animation for the List a product card.
- Added hover lift, thumbnail brightness, and accent-shape motion to product cards.
- Added hover feedback for the List a product card and order rows.
- Kept animations disabled through the existing `prefers-reduced-motion` media rule.

## Main Frontend File

- `frontend-gateway/public/index.html`
