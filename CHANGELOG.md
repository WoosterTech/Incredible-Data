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
