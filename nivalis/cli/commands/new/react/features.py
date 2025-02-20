import json
import shutil
from pathlib import Path
from . import TEMPLATE_DIR
from jinja2 import Template
from typing import List, Dict, Any
from ...models import DependencyObj, FeaturePath

BASE_TAILWIND_DIR = Path(TEMPLATE_DIR) / "feats" / "tailwindcss"
BASE_ESLINT_DIR = Path(TEMPLATE_DIR) / "feats" / "eslint"
BASE_PRETTIER_DIR = Path(TEMPLATE_DIR) / "feats" / "prettier"

class FeaturesEnum:
    PRETTIER = DependencyObj(title="Prettier (Code formatter)", value="PRETTIER", 
                             packages={
                                "prettier": "^3.4.2",
                                }, extras={})
    

    ESLINT = DependencyObj(title="ESLint (Code Linter)", value="ESLINT", 
                           packages={
                                    "eslint": "^9.19.0",
                                    "eslint-plugin-react": "^7.37.4",
                                    "eslint-plugin-react-hooks": "^5.0.0",
                                    "eslint-plugin-react-refresh": "^0.4.18",
                                }, extras={})
    

    TAILWINDCSS = DependencyObj(title="Tailwindcss", value="TAILWINDCSS", 
                                packages={"tailwindcss": "^4.0.0", "@tailwindcss/vite": "^4.0.0",}, 
                                extras={"prettier": "prettier-plugin-tailwindcss"})


def resolve(name: str, typecheck: DependencyObj, features: List[DependencyObj]):
    use_tailwind = any(feature.value == FeaturesEnum.TAILWINDCSS.value for feature in features)
    use_eslint = any(feature.value == FeaturesEnum.ESLINT.value for feature in features)
    use_prettier = any(feature.value == FeaturesEnum.PRETTIER.value for feature in features)

    extras = {}
    dependencies = {}
    filepaths: Dict[str, FeaturePath] = {}

    path = Path(name).resolve()

    if use_tailwind:
        ext_name = "tsx" if typecheck.value == "ts" else "jsx"

        dependencies.update(FeaturesEnum.TAILWINDCSS.packages)
        filepaths.update({
            "tailwind.config": FeaturePath(BASE_TAILWIND_DIR / "tailwind.config.js", Path(path) / "tailwind.config.js"),
            "index.css": FeaturePath(BASE_TAILWIND_DIR / "index.css", Path(path) / "src" / "index.css"),
            "vite.config.js": FeaturePath(BASE_TAILWIND_DIR / "vite.config.js", Path(path) / f"vite.config.{typecheck.value}"),
            "App.css": FeaturePath(BASE_TAILWIND_DIR / "App.css", Path(path) / "src" / "App.css"),
            "App.tsx": FeaturePath(BASE_TAILWIND_DIR / "App.tsx", Path(path) / "src" / f"App.{ext_name}"),
        })

    if use_eslint:
        dependencies.update(FeaturesEnum.ESLINT.packages)
        filepaths.update({
            "eslint.config": FeaturePath(BASE_ESLINT_DIR / "eslint.config.js", Path(path) / "eslint.config.js"),
        })

    if use_prettier:
        dependencies.update(FeaturesEnum.PRETTIER.packages)
        filepaths.update({
            ".prettierrc": FeaturePath(BASE_PRETTIER_DIR / ".prettierrc", Path(path) / ".prettierrc"),
            ".prettierignore": FeaturePath(BASE_PRETTIER_DIR / ".prettierignore", Path(path) / ".prettierignore"),
        })
            
        if use_eslint:
            dependencies["eslint-config-prettier"] = "^10.0.1"

    for filepath in filepaths.values():
        filepath.dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(filepath.src, filepath.dst)

    if use_prettier and use_tailwind:
        prettier_file_path = filepaths.get(".prettierrc")
        resolve_prettier_file(prettier_file_path, use_tailwind)
    
    json_path = Path(path) / "package.json"
    with open(json_path, 'r') as file:
        config: Dict[str, Any] = json.load(file)

    config["name"] = name if name != "." else "My app"
    config["devDependencies"].update(dependencies)

    with open(json_path, 'w') as file:
        json.dump(config, file, indent=2)


def resolve_prettier_file(path: FeaturePath, tailwind: bool):
	with open(path.dst, 'r', encoding='utf-8') as file:
		template_content = file.read()

	template = Template(template_content)
	rendered_content = template.render(tailwind=tailwind)

	with open(path.dst, 'w', encoding='utf-8') as file:
		file.write(rendered_content)
