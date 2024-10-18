## Unreleased

## 0.7.0.dev20240913646 (2024-09-13)

## 0.7.0.dev20240913635 (2024-09-13)

## 0.7.0.dev20240913608 (2024-09-13)

## 0.7.0.dev20240913595 (2024-09-13)

### Fix

- **psycopg**: remove "c" extra and use "binary" always

## 0.7.0.dev20240913583 (2024-09-13)

## 0.7.0.dev20240910001 (2024-09-10)

### Feat

- **allauth**: add socialaccount_providers variable
- **fuel**: add new app with basic models
- **views**: neapolitan and other views; mostly working invoice

## 0.6.0 (2024-06-05)

### Feat

- **properties**: starting the process of adding some propety management models

### Refactor

- **django-rubble**: rename django-utils to django-rubble

## 0.5.2 (2024-05-22)

### Fix

- **containerattachment-permission**: containerattachment_add -> add_containerattachment

## 0.5.1 (2024-05-22)

### Fix

- **requests-update**: dealing with CVE of yanked version; "fix" storage

## 0.5.0 (2024-05-22)

### Feat

- **forms**: so many forms and screwing around with them; also container attachments instead of single field

## 0.4.0 (2024-05-22)

### Feat

- **aws-s3-storage**: use django-storages to properly store production media

### Fix

- **permissions**: add some permissions to bins views

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
