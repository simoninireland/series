# Plug-in to convert Nikola categories into series or blogchains
#
# Copyright (c) 2024 Simon Dobson <simoninireland@gmail.com>
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software. If not, see <http://www.gnu.org/licenses/gpl.html>.

PLUGIN_NAME = series


# ---------- Files ----------

SOURCES = \
	series.py

META = \
	series.plugin

TEST_DIR = test


# ---------- Tools ----------

# Tools
PYTHON = python
NIKOLA = nikola
PIP = PIP
CHDIR = cd
RM = rm -fr
CP = cp -r
MKDIR = mkdir -p

# Venv
VENV = venv3
REQUIREMENTS = requirements.txt

# Derived tools
ACTIVATE = $(CHDIR) test && . $(VENV)/bin/activate


# ---------- Top-level targets ----------

env: $(TEST_DIR)/$(VENV)
	$(CHDIR) $(TEST_DIR) && $(PYTHON) -m venv venv3
	$(ACTIVATE) && $(PIP) install -U pip wheel && $(PIP) install -r requirements.txt

.PHONY: test
test: $(SOURCES) $(META)
	make clean
	$(MKDIR) $(TEST_DIR)/plugins/$(PLUGIN_NAME)
	$(CP) $(SOURCES) $(META) $(TEST_DIR)/plugins/$(PLUGIN_NAME)
	NIKOLA_SHOW_TRACEBACKS=1 make live

live:
	$(ACTIVATE) && $(NIKOLA) auto

clean:
	$(RM) $(TEST_DIR)/output

reallyclean: clean
	$(RM) $(TEST_DIR)/$(VENV)
