## Visual Studio Code Set up

You can basically download the settings file [here](utils/settings.json) and chance the blue path to yours, or create  the file following the steps below.

To configure blue and isort format in vscode just add in your `.vscode\settings.json` file:

```json
{
    "editor.formatOnSave": true,
    "files.autoSave": "afterDelay",
    "python.formatting.provider": "black",
    "python.formatting.blackPath": "your_path/Scripts/blue",
    "[python]": {
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        },
    },
    
}
```

If you want to auto format your code on auto save, install the extension [Run on Save](https://marketplace.visualstudio.com/items?itemName=pucelle.run-on-save) and make sure to add in your `.vscode\settings.json` file:

```json
{
  "runOnSave.commands": [
          {
              "match": ".py",
              "command": "editor.action.organizeImports",
              "runIn": "vscode"
          },
          {
              "match": ".py",
              "command": "editor.action.formatDocument",
              "runIn": "vscode"
          }
      ],
}
```

In addition you can setup the tests in your `.vscode\settings.json` file:

```json
{
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true
}
```

Finally, to get tips from mypy while writing your code add the bellow configurations in your `.vscode\settings.json` file:

```json
{
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.pylintEnabled": false,
    "python.languageServer": "Pylance",
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.diagnosticSeverityOverrides": {
        "reportMissingModuleSource": "none"
    }
}
```

To config `.vscode\launch.json` :

```json
{
  "version": "0.1.0",
  "configurations": [
    {
      "name": "Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "justMyCode": true
    },
    {
      "name": "Blue",
      "type": "python",
      "request": "launch",
      "module": "blue",
      "justMyCode": true,
      "args": [
        "--check",
        "cronus_eater"
      ]
    },
    {
      "name": "Isort",
      "type": "python",
      "request": "launch",
      "module": "isort",
      "justMyCode": true,
      "args": [
        "--check",
        "cronus_eater"
      ]
    },
    {
      "name": "Python: Module",
      "type": "python",
      "request": "launch",
      "module": "cronus_eater",
      "justMyCode": true
    }
  ],
  "compounds": [
    {
      "name": "All tests",
      "configurations": [
        "Tests",
        "Blue",
        "Isort"
      ],
      "stopAll": true,
      "presentation": {
        "hidden": false,
        "group": "",
        "order": 1,
      }
    }
  ]
}
```
