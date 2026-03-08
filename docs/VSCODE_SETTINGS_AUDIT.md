# VS Code / Cursor settings audit (venv 이중 활성화)

검사 일시: 2025-03-08. `source .venv/bin/activate` 이중 실행 원인 추적용으로 뒤진 설정 요약.

---

## 1. 워크스페이스 (learner-portfolio)

| 경로 | 내용 |
|------|------|
| `.vscode/settings.json` | `python.defaultInterpreterPath`, `python.terminal.activateEnvironment: false`, `terminal.integrated.env.linux` (VIRTUAL_ENV, PATH with `${workspaceFolder}/.venv`) |
| `.vscode/` | 위 파일만 존재. `tasks.json`, `launch.json`, `extensions.json` 등 없음. |

- `ide_state.json`에 과거 `.vscode/xsettings.json` 경로가 참조되어 있으나, 실제 파일은 없음.

---

## 2. Cursor 서버 (User 데이터)

| 경로 | 내용 |
|------|------|
| `~/.cursor-server/data/User/settings.json` | `terminal.integrated.allowWorkspaceConfiguration: true` 만 둠. (워크스페이스에서 `terminal.integrated.env.linux` 사용 허용) |
| `~/.cursor-server/data/User/workspaceStorage/` | 워크스페이스별 메타만 있고, `activateEnvironment` 등 터미널/파이썬 설정 없음. |
| `~/.cursor-server/data/User/History/` | `.vscode/settings.json` 편집 이력에 `python.terminal.activateEnvironment: true/false` 기록됨. |

- `terminal.integrated.env.*` 는 기본적으로 **application 스코프**만 허용. 워크스페이스에서 쓰려면 사용자 설정에 `terminal.integrated.allowWorkspaceConfiguration: true` 필요 (VS Code #123330).

---

## 3. 확장(Extensions)

| 확장 | 경로 | 관련 설정 |
|------|------|-----------|
| **ms-python.python** | `~/.cursor-server/extensions/ms-python.python-2023.6.0/` | 아래 참고. |
| **anysphere.cursorpyright** | `~/.cursor-server/extensions/anysphere.cursorpyright-1.0.10/` | Python 분석용. 터미널/venv 활성화와 무관. |
| ms-toolsai.jupyter | `~/.cursor-server/extensions/ms-toolsai.jupyter-.../` | 내부 `.vscode/settings.json`은 `files.exclude`, `python.formatting.provider` 만 있음. |

### MS Python 확장 (venv 활성화 관련)

- **`python.terminal.activateEnvironment`**  
  - 기본값: **`true`**  
  - 설명: "Activate Python Environment in **all Terminals created**."  
  - 새 터미널이 열릴 때마다 `source .../activate` 실행.

- **`python.terminal.activateEnvInCurrentTerminal`**  
  - 기본값: **`false`**  
  - 설명: "Activate Python Environment in the **current Terminal on load of the Extension**."  
  - 확장 로드 시 이미 열려 있는 터미널에 한 번 더 활성화할 수 있음.

- 확장 내부 `pythonFiles/.vscode/settings.json`에는 `files.exclude`, `python.formatting.provider` 만 있고, `activateEnvironment` 없음.

---

## 4. 이중 실행 원인 정리

- **워크스페이스**에서는 현재 `python.terminal.activateEnvironment`를 두지 않았으므로, **기본값 true**가 적용되면 MS Python이 “새 터미널 생성 시” 한 번 `source .../activate`를 실행함.
- **이중으로 찍힌다**면 가능성은:
  1. **MS Python만 있어도**: “새 터미널” 훅과 “확장 로드 시 현재 터미널” 훅이 둘 다 걸려서 두 번 실행되거나, 터미널 생성 로직이 두 번 호출되는 경우.
  2. **Cursor 쪽 자동 주입**: Cursor가 터미널을 열 때 한 번, MS Python이 한 번 각각 넣는 경우.

**적용한 해결**: (1) 사용자 설정에 `terminal.integrated.allowWorkspaceConfiguration: true` 로 워크스페이스 터미널 env 허용. (2) `.vscode/settings.json`에 `python.terminal.activateEnvironment: false` 로 MS Python 자동 활성화 끔. (3) 같은 파일에 `terminal.integrated.env.linux` 로 `VIRTUAL_ENV`/`PATH`만 한 번 주입 (`${workspaceFolder}` 사용). 이중 실행 없이 터미널에서 venv 적용됨.

---

## 5. 참고: 확인한 파일 목록

- `/home/choiec/workspace/learner-portfolio/.vscode/settings.json`
- `/home/choiec/.cursor-server/data/User/` (설정 파일 없음)
- `/home/choiec/.cursor-server/extensions/ms-python.python-*/package.json`, `package.nls.json`
- `/home/choiec/.cursor-server/extensions/ms-python.python-*/resources/report_issue_user_settings.json`
- `/home/choiec/.cursor-server/extensions/ms-toolsai.jupyter-*/pythonFiles/.vscode/settings.json`
- `/home/choiec/.cursor/ide_state.json` (참조만 확인)
