import os
import shutil
from nivalis.cli.commands.new.svelte import SVELTE_TEMPLATE_DIR
from nivalis.cli.commands.new.svelte.models import DependencyObj


def resolve_typecheck(path: str, typecheck: DependencyObj):
    typecheck.func(path)

def resolve_javascript(path: str):
    BASE_JAVASCRIPT_DIR = os.path.join(SVELTE_TEMPLATE_DIR, "typecheck", "javascript")

    src_paths = {
        "js_config": os.path.join(BASE_JAVASCRIPT_DIR, "jsconfig.json"),
        "lib_index": os.path.join(BASE_JAVASCRIPT_DIR, "index.js"),
        "svelte_layout": os.path.join(BASE_JAVASCRIPT_DIR, "+layout.js"),
        "vite_config": os.path.join(BASE_JAVASCRIPT_DIR, "vite.config.js"),
    }

    dst_paths = {
        "js_config": os.path.join(path, "jsconfig.json"),
        "lib_index": os.path.join(path, "src", "lib", "index.js"),
        "svelte_layout": os.path.join(path, "src", "routes", "+layout.js"),
        "vite_config": os.path.join(path, "vite.config.js"),
    }

    for key, value in dst_paths.items():
        shutil.copy2(src_paths[key], value)


def resolve_typescript(path: str):
    BASE_TYPESCRIPT_DIR = os.path.join(SVELTE_TEMPLATE_DIR, "typecheck", "typescript")

    src_paths = {
        "ambient_types": os.path.join(BASE_TYPESCRIPT_DIR, "app.d.ts"),
        "svelte_config": os.path.join(BASE_TYPESCRIPT_DIR, "svelte.config.js"),
        "ts_config": os.path.join(BASE_TYPESCRIPT_DIR, "tsconfig.json"),
        "lib_index": os.path.join(BASE_TYPESCRIPT_DIR, "index.ts"),
        "svelte_layout": os.path.join(BASE_TYPESCRIPT_DIR, "+layout.ts"),
        "vite_config": os.path.join(BASE_TYPESCRIPT_DIR, "vite.config.ts"),
    }

    dst_paths = {
        "ambient_types": os.path.join(path, "src", "app.d.ts"),
        "svelte_config": os.path.join(path, "svelte.config.js"),
        "ts_config": os.path.join(path, "tsconfig.json"),
        "lib_index": os.path.join(path, "src", "lib", "index.ts"),
        "svelte_layout": os.path.join(path, "src", "routes", "+layout.ts"),
        "vite_config": os.path.join(path, "vite.config.ts"),
    }

    for key, value in dst_paths.items():
        shutil.copy2(src_paths[key], value)

class TypecheckEnum:
    TYPESCRIPT = DependencyObj("Typescript", "ts", resolve_typescript, packages={"typescript": "^5.0.0",
		"typescript-eslint": "^8.20.0"})
    
    JSDOCS = DependencyObj("JSDoc comments", "js", resolve_javascript, packages={})
    JAVASCRIPT = DependencyObj("Vanilla Javascript", "js", resolve_javascript, packages={})