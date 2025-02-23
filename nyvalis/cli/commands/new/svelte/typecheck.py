import json
import shutil
from pathlib import Path
from . import TEMPLATE_DIR
from nyvalis.tools import log
from typing import Dict, Any, List
from ...models import DependencyObj, FeaturePath

logger = log.get(log.LIB_NAME)

BASE_TYPESCRIPT_DIR = Path(TEMPLATE_DIR) / "typecheck" / "typescript"
BASE_JAVASCRIPT_DIR = Path(TEMPLATE_DIR) / "typecheck" / "javascript"

class TypecheckEnum:
    TYPESCRIPT = DependencyObj(title="Typescript", value="ts", 
                               packages={"typescript": "^5.0.0", "typescript-eslint": "^8.20.0",}, extras={})
    

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
            "app.d.ts": FeaturePath(BASE_TYPESCRIPT_DIR / "app.d.ts", Path(path) / "src" /"app.d.ts"),
            "svelte.config.js": FeaturePath(BASE_TYPESCRIPT_DIR / "svelte.config.js", Path(path) / "svelte.config.js"),
            "tsconfig.json": FeaturePath(BASE_TYPESCRIPT_DIR / "tsconfig.json", Path(path) / "tsconfig.json"),
            "index.ts": FeaturePath(BASE_TYPESCRIPT_DIR / "index.ts", Path(path) / "src" / "lib" / "index.ts"),
            "+layout.ts": FeaturePath(BASE_TYPESCRIPT_DIR / "+layout.ts", Path(path) / "src" / "routes" / "+layout.ts"),
            "vite.config.ts": FeaturePath(BASE_TYPESCRIPT_DIR / "vite.config.ts", Path(path) / "vite.config.ts"),
        })
    else:
        dependencies.update(TypecheckEnum.JAVASCRIPT.packages)
        filepaths.update({
            "jsconfig.json": FeaturePath(BASE_JAVASCRIPT_DIR / "jsconfig.json", Path(path) / "jsconfig.json"),
            "index.js": FeaturePath(BASE_JAVASCRIPT_DIR / "index.js", Path(path) / "src" / "lib" /"index.js"),
            "+layout.js": FeaturePath(BASE_JAVASCRIPT_DIR / "+layout.js", Path(path) / "src" / "lib" / "+layout.js"),
            "vite.config.js": FeaturePath(BASE_JAVASCRIPT_DIR / "vite.config.js", Path(path) / "vite.config.js"),
        })
        
    logger.info("Copying typecheck files")
    for filepath in filepaths.values():
        filepath.dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(filepath.src, filepath.dst)

    logger.info("Writing package.json")
    json_path = Path(path) / "package.json"
    with open(json_path, 'r') as file:
        config: Dict[str, Any] = json.load(file)

    config["name"] = path if path != "." else "My app"
    config["devDependencies"].update(dependencies)
    
    with open(json_path, 'w') as file:
        json.dump(config, file, indent=2)

    logger.info("package.json ready")
