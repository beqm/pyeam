import os
import shutil
from typing import List
from nivalis.cli.commands.new.svelte import SVELTE_TEMPLATE_DIR
from nivalis.cli.commands.new.svelte.models import DependencyObj

def resolve_features(path: str, features: List[DependencyObj], typecheck: DependencyObj):
    
    callables = {feature.value: feature.func
                for feature in FeaturesEnum.__dict__.values()
                if isinstance(feature, DependencyObj) and feature in features}
    
    for callable in callables.values():
        callable(path, typecheck.value)


def resolve_eslint(path: str, _):
    BASE_ESLINT_DIR = os.path.join(SVELTE_TEMPLATE_DIR, "feats", "eslint")

    src_paths = {
        "eslint": os.path.join(BASE_ESLINT_DIR, "eslint.config.js"),
    }

    dst_paths = {
        "eslint": os.path.join(path, "eslint.config.js"),
    }

    for key, value in dst_paths.items():
        shutil.copy2(src_paths[key], value)

def resolve_prettier(path: str, _):
    BASE_PRETTIER_DIR = os.path.join(SVELTE_TEMPLATE_DIR, "feats", "prettier")

    src_paths = {
        "prettier": os.path.join(BASE_PRETTIER_DIR, ".prettierrc"),
        "prettier_ignore": os.path.join(BASE_PRETTIER_DIR, ".prettierignore"),
    }

    dst_paths = {
        "prettier": os.path.join(path, ".prettierrc"),
        "prettier_ignore": os.path.join(path, ".prettierignore"),
    }

    for key, value in dst_paths.items():
        shutil.copy2(src_paths[key], value)

def resolve_tailwindcss(path: str, typecheck: str):
    BASE_TAILWIND_DIR = os.path.join(SVELTE_TEMPLATE_DIR, "feats", "tailwindcss")

    src_paths = {
        "prettier": os.path.join(BASE_TAILWIND_DIR, ".prettierrc"),
        "css": os.path.join(BASE_TAILWIND_DIR, "app.css"),
        "tailwind_config": os.path.join(BASE_TAILWIND_DIR, "tailwind.config.js"),
        "vite_config": os.path.join(BASE_TAILWIND_DIR, "vite.config.js"),
        "svelte_page": os.path.join(BASE_TAILWIND_DIR, "+page.svelte"),
    }

    dst_paths = {
        "prettier": os.path.join(path, ".prettierrc"),
        "css": os.path.join(path, "src", "app.css"),
        "tailwind_config": os.path.join(path, "tailwind.config.js"),
        "vite_config": os.path.join(path, f"vite.config.{typecheck}"),
        "svelte_page": os.path.join(path, "src", "routes", "+page.svelte"),
    }

    for key, value in dst_paths.items():
        shutil.copy2(src_paths[key], value)

class FeaturesEnum:
    PRETTIER = DependencyObj("Prettier (Code formatter)", "PRETTIER", resolve_prettier, packages={"prettier": "^3.4.2",
		"prettier-plugin-svelte": "^3.3.3",
		"prettier-plugin-tailwindcss": "^0.6.11",})
    
    ESLINT = DependencyObj("ESLint (Code Linter)", "ESLINT", resolve_eslint, packages={"@eslint/compat": "^1.2.5",
		"@eslint/js": "^9.18.0", "eslint": "^9.18.0",
		"eslint-config-prettier": "^10.0.1",
		"eslint-plugin-svelte": "^2.46.1",})
    
    TAILWINDCSS = DependencyObj("Tailwindcss", "TAILWINDCSS", resolve_tailwindcss, packages={"tailwindcss": "^4.0.0", "@tailwindcss/vite": "^4.0.0",})