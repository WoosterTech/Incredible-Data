## 0.3.0 (2024-05-22)

### Feat

- **homepage**: add card to homepage and qr-code to container detail
- **capitalized-id**: use shortuuid to generate ids using only capital letters with no ambiguity
- **expense-category**: add expense category with default values, add test of creation of receipt and receipt items form sample data

### Fix

- **container-detail**: improvements to layout, particularly for mobile, of container detail page
- **render**: make web autoDeploy false
- **correct-render.yaml**: web.envVars.CELERY_BROKER_URL was indented incorrectly
- **merge-items**: merge items from each "document" to handle multi-page receipts better

### Refactor

- **username-title**: add allauth for detail page title
- **allauth-tags**: use allauth template tags to show user name or email on info page

## 0.2.1 (2024-04-23)

### Fix

- **receipts**: functional celery task for analyzing receipts

### Refactor

- **basenumberedmodel**: create and start using basenumberedmodel

## 0.2.0 (2024-04-17)

### Feat

- **business**: refactor some utility models, add business app, general fixes
- **receipts**: add models and signals for receipts, including merchants and very simple items
- **receipt-analysis**: starting to write task for receipts
- **SimplePercentageField**: add percentage field and form field
- **helpers**: copy helpers from seas_purchase_system, clean up
- **assets**: add assets, refactor bins app
- **bins-and-assets**: bins is functional, assets is completely empty

### Fix

- **missed-format**: didn't format before last commit
- **remove-assets-app**: assets is built in to "bins"
