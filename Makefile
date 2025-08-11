ALIAS_DIR := $(USERPROFILE)\bin
ALIAS_NAME := manage
BAT_FILE := $(ALIAS_DIR)\$(ALIAS_NAME).bat

install-alias:
	@echo "This doesn't work!!!"
	@echo "Installing CMD alias for $(ALIAS_NAME)..."
	@mkdir "$(ALIAS_DIR)" 2>nul || echo "Alias dir exists"
	@echo @echo off > "$(BAT_FILE)"
	@echo uv run python "%~dp0\..\manage.py" %%* >> "$(BAT_FILE)"
	@setx PATH "%PATH%;$(ALIAS_DIR)" >nul
	@echo "Alias installed! Restart CMD to use '$(ALIAS_NAME)'."

uninstall-alias:
	@echo "Removing CMD alias for $(ALIAS_NAME)..."
	@if exist "$(BAT_FILE)" (
		@del "$(BAT_FILE)"
		@echo "Alias removed!"
	) else (
		@echo "Alias not found!"
	)
