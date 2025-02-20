import json
import shutil
from pathlib import Path
from . import TEMPLATE_DIR
from typing import Dict, Any, List
from ...models import DependencyObj, FeaturePath

BASE_TYPESCRIPT_DIR = Path(TEMPLATE_DIR) / "typecheck" / "typescript"
BASE_JAVASCRIPT_DIR = Path(TEMPLATE_DIR) / "typecheck" / "javascript"

class TypecheckEnum:
    TYPESCRIPT = DependencyObj(title="Typescript", value="ts", 
                               packages={"typescript": "~5.7.2", "typescript-eslint": "^8.22.0",}, extras={})
    

    JSDOCS = DependencyObj(title="JSDoc comments", value="js",
                            packages={}, extras={})
    

    JAVASCRIPT = DependencyObj(title="Vanilla Javascript", value="js",
                                packages={}, extras={})


def resolve(path: str, typecheck: DependencyObj, features: List[DependencyObj]):
    use_typecheck = typecheck.value != "js"

    extras = {}
    dependencies = {}
    filepaths: Dict[str, FeaturePath] = {}

    if use_typecheck:
        dependencies.update(TypecheckEnum.TYPESCRIPT.packages)
        filepaths.update({
            "App.tsx": FeaturePath(BASE_TYPESCRIPT_DIR / "App.tsx", Path(path) / "src" / "App.tsx"),
            "main.tsx": FeaturePath(BASE_TYPESCRIPT_DIR / "main.tsx", Path(path) / "src" / "main.tsx"),
            "tsconfig.json": FeaturePath(BASE_TYPESCRIPT_DIR / "tsconfig.json", Path(path) / "tsconfig.json"),
            "tsconfig.app.json": FeaturePath(BASE_TYPESCRIPT_DIR / "tsconfig.app.json", Path(path) / "tsconfig.app.json"),
            "tsconfig.node.json": FeaturePath(BASE_TYPESCRIPT_DIR / "tsconfig.node.json", Path(path) / "tsconfig.node.json"),
            "vite-env.d.ts": FeaturePath(BASE_TYPESCRIPT_DIR / "vite-env.d.ts", Path(path) / "src" / "vite-env.d.ts"),
            "vite.config.ts": FeaturePath(BASE_TYPESCRIPT_DIR / "vite.config.ts", Path(path) / "vite.config.ts"),
            "index.html": FeaturePath(BASE_TYPESCRIPT_DIR / "index.html", Path(path) / "index.html"),
        })
    else:
        dependencies.update(TypecheckEnum.JAVASCRIPT.packages)
        filepaths.update({
            "App.jsx": FeaturePath(BASE_JAVASCRIPT_DIR / "App.jsx", Path(path) / "src" / "App.jsx"),
            "main.jsx": FeaturePath(BASE_JAVASCRIPT_DIR / "main.jsx", Path(path) / "src" / "main.jsx"),
            "vite.config.js": FeaturePath(BASE_JAVASCRIPT_DIR / "vite.config.js", Path(path) / "vite.config.js"),
            "index.html": FeaturePath(BASE_JAVASCRIPT_DIR / "index.html", Path(path) / "index.html"),
        })
        

    for filepath in filepaths.values():
        filepath.dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(filepath.src, filepath.dst)

    json_path = Path(path) / "package.json"
    with open(json_path, 'r') as file:
        config: Dict[str, Any] = json.load(file)

    config["name"] = path if path != "." else "My app"
    config["devDependencies"].update(dependencies)

    with open(json_path, 'w') as file:
        json.dump(config, file, indent=2)


