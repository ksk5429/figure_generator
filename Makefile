# figure_generator — DAG build system
#
# Conventions:
#   Each figure lives in figures/<id>/ and is built by running figures/<id>/<id>.py.
#   Sources: the .py script + config.yaml + any referenced files under data/.
#   Outputs: <id>.png, <id>.svg, <id>.pdf.

PY          ?= python
PIP         ?= pip
FIG_DIR     := figures
GALLERY_DIR := gallery
MKDOCS_CFG  := $(GALLERY_DIR)/mkdocs.yml
SITE_DIR    := $(GALLERY_DIR)/site
TEMPLATE    := scripts/_template_figure.py

FIG_IDS     := $(notdir $(patsubst %/,%,$(wildcard $(FIG_DIR)/*/)))

.PHONY: help setup figure figures figures-for gallery gallery-pages serve test clean metadata lint format new-figure publish publish-dry publish-paper publish-paper-dry witness witness-all refresh-all pipeline pipeline-ci pipeline-stage critic compliance validate-pdf iter-gallery

help:
	@echo "figure_generator targets:"
	@echo "  make setup              Install package in editable mode"
	@echo "  make figure FIG=<id>    Build a single figure"
	@echo "  make figures            Build all figures"
	@echo "  make figures-for PAPER=<code>  Rebuild every figure tagged paper: <code>"
	@echo "  make gallery            Regenerate docs pages + build MkDocs Material site"
	@echo "  make gallery-pages      Regenerate docs pages only (no mkdocs build)"
	@echo "  make serve              Live-preview gallery at http://localhost:8000"
	@echo "  make publish [PAPER=<code>]    Copy figures into research-notes/docs/figures/"
	@echo "  make publish-dry [PAPER=<code>] Preview publish without writing"
	@echo "  make publish-paper PAPER=<code>     Render manuscript .qmd into research-notes/docs/papers/"
	@echo "  make publish-paper-dry PAPER=<code> Preview manuscript publish without writing"
	@echo "  make refresh-all                     Republish every registered paper"
	@echo "  make witness PAPER=<code>           Evaluate claim witnesses for a paper"
	@echo "  make witness-all                     Evaluate claim witnesses for every paper"
	@echo "  make test               Run pytest (+ pytest-mpl)"
	@echo "  make metadata FIG=<id>  Print embedded metadata from outputs"
	@echo "  make new-figure FIG=<id>  Scaffold a new figure folder from template"
	@echo "  make clean              Remove generated figure outputs and site/"
	@echo "  make lint               Run ruff"
	@echo "  make format             Run ruff format"
	@echo "  make pipeline FIG=<id> [ASK=\"...\"]   Run the full 5-agent pipeline (LLM+vision)"
	@echo "  make pipeline-ci FIG=<id>             Deterministic, offline run (no LLM, no vision)"
	@echo "  make pipeline-stage FIG=<id> STAGE=<plan|geotech|compile|witness|critic|compliance>"
	@echo "  make critic FIG=<id>                  Run the critic alone"
	@echo "  make claim-witness FIG=<id>           Run the claim-witness agent alone"
	@echo "  make compliance FIG=<id>              Run the journal-compliance linter"
	@echo "  make validate-pdf FIG=<id>            pdffonts + identify checks"
	@echo "  make iter-gallery FIG=<id>            Build figures/<id>/build/iterations.html"

setup:
	$(PIP) install -e .[dev]

figure:
ifndef FIG
	$(error FIG is not set. Usage: make figure FIG=<figure_id>)
endif
	@test -d $(FIG_DIR)/$(FIG) || (echo "No such figure folder: $(FIG_DIR)/$(FIG)" && exit 1)
	$(PY) $(FIG_DIR)/$(FIG)/$(FIG).py

figures:
	@for id in $(FIG_IDS); do \
	    echo ">> building $$id"; \
	    $(PY) $(FIG_DIR)/$$id/$$id.py || { echo "FAILED: $$id"; exit 1; }; \
	done

figures-for:
ifndef PAPER
	$(error PAPER is not set. Usage: make figures-for PAPER=<code>)
endif
	@$(PY) -c "import sys, yaml; \
from pathlib import Path; \
ids = [d.name for d in Path('$(FIG_DIR)').iterdir() if d.is_dir() and not d.name.startswith('.') \
       and (d / 'config.yaml').exists() \
       and (yaml.safe_load((d / 'config.yaml').read_text(encoding='utf-8')) or {}).get('paper') == '$(PAPER)']; \
print('\n'.join(ids))" | while read id; do \
	    [ -z "$$id" ] && continue; \
	    echo ">> building $$id"; \
	    $(PY) $(FIG_DIR)/$$id/$$id.py || { echo "FAILED: $$id"; exit 1; }; \
	done

gallery-pages:
	$(PY) $(GALLERY_DIR)/build_gallery.py

gallery: gallery-pages
	mkdocs build -f $(MKDOCS_CFG)

serve: gallery-pages
	mkdocs serve -f $(MKDOCS_CFG) -a 127.0.0.1:8000

publish:
ifdef PAPER
	$(PY) scripts/publish_to_notes.py --paper $(PAPER)
else
	$(PY) scripts/publish_to_notes.py
endif

publish-dry:
ifdef PAPER
	$(PY) scripts/publish_to_notes.py --paper $(PAPER) --dry-run
else
	$(PY) scripts/publish_to_notes.py --dry-run
endif

publish-paper:
ifndef PAPER
	$(error PAPER is not set. Usage: make publish-paper PAPER=<code>)
endif
	$(PY) scripts/publish_paper.py --paper $(PAPER)

publish-paper-dry:
ifndef PAPER
	$(error PAPER is not set. Usage: make publish-paper-dry PAPER=<code>)
endif
	$(PY) scripts/publish_paper.py --paper $(PAPER) --dry-run

refresh-all:
	@$(PY) -c "import yaml; \
cfg = yaml.safe_load(open('configs/paths.yaml', encoding='utf-8')) or {}; \
print('\n'.join(sorted((cfg.get('manuscripts') or {}).keys())))" | while read p; do \
	    [ -z "$$p" ] && continue; \
	    echo '>> republishing ' $$p; \
	    $(PY) scripts/publish_paper.py --paper $$p || { echo 'FAILED: ' $$p; exit 1; }; \
	done

witness:
ifndef PAPER
	$(error PAPER is not set. Usage: make witness PAPER=<code>)
endif
	$(PY) -m figgen.witness --paper $(PAPER)

witness-all:
	@for d in papers/*/; do \
	    p=$$(basename $$d); \
	    [ -d papers/$$p/figure_inputs/claims ] || continue; \
	    echo '>> witness ' $$p; \
	    $(PY) -m figgen.witness --paper $$p; \
	done

test:
	$(PY) -m pytest tests/

metadata:
ifndef FIG
	$(error FIG is not set. Usage: make metadata FIG=<figure_id>)
endif
	$(PY) -c "from figgen.metadata import print_metadata; print_metadata('$(FIG_DIR)/$(FIG)')"

new-figure:
ifndef FIG
	$(error FIG is not set. Usage: make new-figure FIG=<figure_id>)
endif
	@test -d $(FIG_DIR)/$(FIG) && (echo "Figure $(FIG) already exists." && exit 1) || true
	@mkdir -p $(FIG_DIR)/$(FIG)
	@cp $(TEMPLATE) $(FIG_DIR)/$(FIG)/$(FIG).py
	@echo "figure_id: $(FIG)" > $(FIG_DIR)/$(FIG)/config.yaml
	@echo "journal: thesis" >> $(FIG_DIR)/$(FIG)/config.yaml
	@echo "# $(FIG)" > $(FIG_DIR)/$(FIG)/CAPTION.md
	@echo "Scaffolded $(FIG_DIR)/$(FIG). Edit $(FIG).py and config.yaml, then run: make figure FIG=$(FIG)"

clean:
	@find $(FIG_DIR) -type f \( -name '*.png' -o -name '*.svg' -o -name '*.pdf' \) -delete
	@rm -rf $(SITE_DIR)
	@rm -rf $(GALLERY_DIR)/docs/figures/*/
	@find $(GALLERY_DIR)/docs/figures -maxdepth 1 -name '*.md' -delete 2>/dev/null || true
	@echo "Cleaned generated figure outputs and gallery site/."

lint:
	ruff check src tests scripts gallery

format:
	ruff format src tests scripts gallery

pipeline:
ifndef FIG
	$(error FIG is not set. Usage: make pipeline FIG=<figure_id> [ASK="..."])
endif
	$(PY) scripts/run_pipeline.py --figure $(FIG) $(if $(ASK),--ask "$(ASK)",)

pipeline-ci:
ifndef FIG
	$(error FIG is not set. Usage: make pipeline-ci FIG=<figure_id>)
endif
	$(PY) scripts/run_pipeline.py --figure $(FIG) --ci

pipeline-stage:
ifndef FIG
	$(error FIG is not set. Usage: make pipeline-stage FIG=<figure_id> STAGE=<plan|geotech|compile|critic|compliance>)
endif
ifndef STAGE
	$(error STAGE is not set. Usage: make pipeline-stage FIG=<figure_id> STAGE=<plan|geotech|compile|critic|compliance>)
endif
	$(PY) scripts/run_pipeline.py --figure $(FIG) --stage $(STAGE)

critic:
ifndef FIG
	$(error FIG is not set. Usage: make critic FIG=<figure_id>)
endif
	$(PY) scripts/run_pipeline.py --figure $(FIG) --stage critic

claim-witness:
ifndef FIG
	$(error FIG is not set. Usage: make claim-witness FIG=<figure_id>)
endif
	$(PY) scripts/run_pipeline.py --figure $(FIG) --stage witness

compliance:
ifndef FIG
	$(error FIG is not set. Usage: make compliance FIG=<figure_id>)
endif
	$(PY) scripts/journal_lint.py $(FIG_DIR)/$(FIG)

validate-pdf:
ifndef FIG
	$(error FIG is not set. Usage: make validate-pdf FIG=<figure_id>)
endif
	$(PY) scripts/validate_pdf.py $(FIG_DIR)/$(FIG)/*.pdf

iter-gallery:
ifndef FIG
	$(error FIG is not set. Usage: make iter-gallery FIG=<figure_id>)
endif
	$(PY) scripts/iteration_gallery.py $(FIG_DIR)/$(FIG)
