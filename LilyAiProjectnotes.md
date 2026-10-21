LilyAi Project Notes

Master Project Specification, Architecture Decisions, and Repository Blueprint

Project: LilyAi
Document: "LilyAiProjectnotes.md"
Status: Planning consolidated; implementation must follow the approved milestones
Primary platform: Android 11
Primary development language: Python
Build target: Installable Android APK
Development priority: Develop directly on the Android phone where practical
Current phase: Architecture consolidation and compatibility planning

---

1. Instructions for Future AI Coding Sessions

You are the development assistant for LilyAi.

Read this document before proposing architectural changes, generating code, creating files, or building an APK.

Your responsibility is to help the project owner build LilyAi through understandable, incremental, copy-and-paste-friendly development.

Mandatory rules

1. Treat this document as the project's consolidated requirements and architecture reference.
2. Use Python as the primary application logic and tool-development language.
3. Use Kotlin or Java where native Android functionality requires it, especially Android permissions, accessibility services, floating overlays, lifecycle management, and native integration.
4. Keep the application compatible with the target phone and Android version unless a documented compatibility test justifies a change.
5. Do not assume that a library, model, Android API, or Python package works on the target device. Verify compatibility early.
6. Build incrementally. Test each milestone before moving to the next.
7. Explain which files need to be created or edited, their repository paths, and the purpose of each change.
8. Prefer complete, consistent file contents over disconnected code fragments when the user needs to copy and paste files.
9. Never silently change a confirmed architecture decision. Explain the problem and request approval before changing an important decision.
10. Do not claim an APK was built, installed, or tested unless the corresponding operation actually succeeded.
11. Distinguish implemented features from planned features, experimental features, and unavailable features.
12. Do not create code, files, or APK builds when the project owner explicitly requests planning only.
13. Do not invent missing decisions from earlier discussions. If an original topic's complete decision record is unavailable, identify the uncertainty and ask only when it affects the next implementation step.
14. Provide beginner-friendly explanations and commands that can be followed on the phone.
15. Preserve existing working code and avoid unnecessary rewrites.

How to work with the project owner

For each implementation task:

- State the objective.
- Identify prerequisites and compatibility risks.
- List the exact files to create or modify.
- Provide complete code where appropriate.
- Explain how to run the test.
- Define the expected result.
- Explain likely failures and how to diagnose them.
- Wait for test results before assuming success.

The owner prefers a practical offline APK, not a cloud-only assistant or a collection of disconnected prototypes.

---

2. Project Vision

LilyAi is a phone-based AI assistant intended to operate primarily on the user's own Android device.

The application should combine local AI inference, persistent memory, web search, terminal access, and controlled interaction with other Android applications.

The goal is an all-rounder assistant that can accept a prompt while the user is using another application, reason about a task, and execute permitted actions through approved Android interfaces.

The design should favor privacy, local operation, low resource consumption, reliability, and user control.

Main capabilities

1. Offline AI conversation using a locally installed language model.
2. A floating overlay chat interface that can appear above other applications.
3. Text input and conversation history.
4. Controlled keyboard interaction.
5. Screen interaction through permitted Android accessibility capabilities.
6. Touch and swipe automation.
7. A visible Stop control to interrupt ongoing work.
8. A local Python execution environment for approved tools and scripts.
9. A terminal interface for user-approved commands.
10. Optional web search using the owner's Tavily API.
11. Local persistent memory and knowledge storage.
12. Optional cloud memory synchronization using Turso.
13. Optional in-app model downloading with progress and integrity checks.
14. Task history, action logs, errors, approvals, and outcomes.
15. Configurable overlay position, size, opacity, and panel dimensions.
16. Supervised multi-step automation.
17. A modular architecture that permits future expansion without rebuilding the entire application.

Not every feature must be available in the first APK. The core architecture and development sequence must support these capabilities progressively.

---

3. Target Device and Resource Budget

Target hardware

Property| Target
Phone| OPPO A92
Android version| Android 11
Processor| Qualcomm Snapdragon 665
Physical RAM| 8 GB
Advertised additional RAM| 3 GB
Internal storage| 128 GB
Maximum AI-related storage allocation| 30 GB
Preferred development environment| Directly on Android where practical

The additional 3 GB of advertised RAM must not be treated as equivalent to physical RAM. It may use storage-backed memory expansion and cannot be relied on as a substitute for real memory.

Storage policy

The 30 GB limit is a maximum allocation for AI-related data, not a requirement to consume the full amount.

Plan separate storage budgets for:

- Language model weights.
- Model runtime and supporting files.
- Tokenizers and model configuration.
- Local knowledge documents and indexes.
- Embeddings, if used.
- Conversation history and approved memory.
- Temporary downloads and update staging.
- Logs and task records.

Do not allow downloaded models, temporary files, caches, and duplicated model versions to grow without limits.

Reserve adequate internal storage for Android, the APK, updates, and the user's other applications.

RAM policy

The 8 GB physical RAM target must be treated as a constrained environment.

The operating system and other applications require memory even when LilyAi is the foreground application.

Therefore:

- Avoid loading multiple language models simultaneously.
- Prefer one primary local model.
- Load optional components only when needed.
- Release model resources when the user explicitly closes the inference session or when safe lifecycle management requires it.
- Keep overlay rendering lightweight.
- Avoid excessive background services.
- Avoid unnecessary copying of large model files and tensors.
- Test inference while other common applications are open.
- Monitor memory pressure, application restarts, thermal behavior, and sustained inference speed.

The project must not promise pressure-free operation until the chosen model and runtime have passed real-device tests.

---

4. Confirmed Project Decisions

The following decisions are carried forward from the available project conversation.

Decision group A: Application architecture

- The product is a native Android APK with Python as the main application logic language.
- Native Android code is permitted where Android APIs require it.
- Python must be embedded into the APK, subject to an early compatibility test.
- The application needs a Python/Android bridge.
- The application must use a defined architecture rather than relying on one large script.
- Local inference integration must be tested early.
- Overlay functionality must use appropriate Android integration.
- A task runtime must separate reasoning from the actual execution of actions.
- Dependencies must be selected with target-device compatibility in mind.
- Recommended architecture choices previously marked B are retained as selected decisions. Where the exact option text is not available in this consolidated record, do not invent its original wording.

Decision group B: Python and terminal

- The terminal experience follows previously selected Option B.
- The Python execution environment follows previously selected Option B.
- Terminal command permissions follow previously selected Option B.
- The terminal and Python execution environment must be treated as controlled execution capabilities, not as unrestricted authority for the AI.
- Permissions and safeguards must be explicit.
- Long-running operations must be cancellable where the underlying operation supports cancellation.
- A task must not be considered stopped merely because the UI stopped displaying progress.

The exact original wording of the three Option B choices is not reproduced in the available summary. Confirm any disputed implementation detail against the original conversation before making a consequential architectural change.

Decision group C: Memory

- Local storage is supported.
- Turso is the planned cloud memory service.
- Only selected memories and procedures should be synchronized.
- Private task history and detailed execution logs remain local by default.
- Cloud synchronization must not automatically upload all private activity.
- LilyAi may suggest useful memories or procedures, but the owner must approve them before they become persistent approved knowledge.
- Memory management should be separate from raw conversation history.

Decision group D: Task history

- Record task steps, approvals, outcomes, and errors separately from readable conversation messages.
- Keep private task history and logs local by default.
- Make task history understandable and useful for troubleshooting.
- Preserve sufficient information to understand what happened without storing unnecessary sensitive data.

Decision group E: Overlay customization

The overlay must support basic customization of:

- Floating bubble position.
- Bubble size.
- Bubble opacity.
- Chat panel size.

Customization should be persisted locally and restored on subsequent launches.

Decision group F: Supervised automation

- Supervised mode is the default.
- A session requires approval.
- Unexpected conditions must stop or pause the workflow rather than trigger uncontrolled continuation.
- Repetitive automation sessions have a maximum of 10 runs.
- That maximum is a session-level limit, not permission to run indefinitely.
- A visible Stop control must be available during execution.
- Action permissions and approval boundaries must be enforced by the execution system rather than by model instructions alone.

Decision group G: Model and deployment

- Target one primary local language model initially.
- A model may be downloaded optionally within the application.
- Model downloads require progress reporting and integrity checks.
- The maximum AI-related storage allocation is 30 GB.
- The chosen model must be appropriate for the actual target device and runtime.
- Model compatibility must be established before extensive application development depends on it.

Decision group H: Architecture freeze and development handoff

For Topic 26, the recorded selections are:

1. Architecture: Option B — architecture freeze and consolidation.
2. Build sequence: Option B.
3. Early compatibility tests: Option B.
4. Milestone acceptance criteria: Option B.
5. Development handoff: Option B.

These decisions mean that the next development phase must consolidate the design, establish a repeatable build sequence, validate risky dependencies early, define measurable acceptance tests, and maintain a clear handoff between planning and implementation.

The original full wording of every Option B selection is not available in this summary. These descriptions capture the recorded decision labels and should not be expanded into fabricated historical quotations.

---

5. Android Interaction and Permissions

LilyAi must interact with Android through supported APIs and explicit user authorization.

Floating overlay

The overlay should provide:

- A floating bubble.
- A compact prompt interface.
- A larger conversation panel.
- A Stop control.
- A clear execution status.
- Access to task approval controls.
- Customizable appearance and position.

Use the Android overlay permission where required.

The application must explain why overlay access is needed and provide an appropriate way to open Android settings if the permission has not been granted.

Do not assume overlay permission is enabled.

Screen interaction

Use an Android accessibility service where appropriate for permitted UI interaction.

The service should:

- Operate only with user-granted authorization.
- Execute supported gestures and accessibility actions.
- Report failures.
- Detect when the expected screen or UI element is unavailable.
- Pause when an unexpected condition makes the next action unsafe.
- Avoid silently continuing after a failed or ambiguous action.

Accessibility APIs do not provide unrestricted control over every application or protected system surface.

Keyboard interaction

Prefer supported input mechanisms.

Keyboard input may depend on the target application, available accessibility nodes, the active input method, and Android restrictions.

Do not promise universal typing or interaction across all apps.

Touch and swipe

Where supported, use the appropriate accessibility gesture APIs.

Before executing a sequence:

1. Determine the intended action.
2. Verify the relevant UI state where possible.
3. Apply the action.
4. Check whether the expected outcome occurred.
5. Stop or request guidance if the outcome is unexpected.

Permission management

Keep permissions separated by capability. Examples include:

- Overlay permission.
- Accessibility service authorization.
- Network access.
- Notifications, where required.
- Storage or document access, where required.
- Any additional permissions justified by a concrete feature.

Do not request every permission during the first launch without explanation.

---

6. Stop Button and Execution Control

The Stop button is a core system requirement.

It must not be implemented as a decorative UI element.

Required behavior

When Stop is pressed:

1. Immediately register the cancellation request.
2. Prevent the task scheduler from starting additional actions.
3. Cancel queued work.
4. Signal cooperative cancellation to the running tool or Python task.
5. Cancel active inference when supported by the model runtime.
6. Stop future gestures and keyboard actions.
7. Terminate or isolate a running subprocess when safe and necessary.
8. Record the cancellation event and the last known task state.
9. Update the UI to show whether the task has stopped or whether cleanup remains in progress.

Cancellation limitations

Not every native call, model inference operation, or third-party library supports immediate interruption.

The UI must distinguish between:

- Cancellation requested.
- Cancellation in progress.
- Execution stopped.
- A component did not respond to cancellation.

A timeout or forced termination may be needed for unresponsive subprocesses.

Never start a replacement task that can continue interacting with the phone while the original task is still uncontrolled.

The cancellation design must account for races between a stop request and an action that is about to execute.

---

7. AI Model and Offline Inference

The first release should use one primary local language model.

The project prioritizes balanced reasoning, tool use, and speed.

Model-selection requirements

Do not select a model solely by parameter count or advertised benchmark performance.

Evaluate:

- Model format.
- Quantization.
- Supported inference runtime.
- Android ABI compatibility.
- CPU and available accelerator support.
- Peak RAM usage.
- Token generation speed.
- Prompt processing speed.
- Context length and memory requirements.
- Tool-calling reliability.
- License and redistribution requirements.
- Model file size.
- Performance under thermal load.

A small or quantized model may be more practical than a larger model on the Snapdragon 665.

A model that fits on storage does not necessarily fit comfortably in RAM.

Early model test

Before committing to a model integration:

1. Select a candidate runtime and model.
2. Verify that the runtime can execute on the target Android environment.
3. Load the model without exhausting available memory.
4. Run a basic offline prompt.
5. Test a longer prompt.
6. Measure response speed and memory usage.
7. Check whether inference can be interrupted or safely abandoned.
8. Repeat while another application is open.
9. Record the actual results.

Keep the selected model configurable so that model integration can be changed without rewriting the overlay and task scheduler.

Offline guarantees

Offline mode must continue to work without a network connection for features whose required components are already installed.

At minimum, the design should support local conversation, local memory access, and local task management without depending on Tavily or Turso.

Cloud memory synchronization and web search are optional online capabilities.

---

8. Web Search Using Tavily

The project owner already has a Tavily API key.

Tavily should provide an optional web-search tool for tasks that need current external information.

Required design

Create a dedicated search tool interface that:

- Accepts a search query.
- Sends a request to Tavily when network access is available.
- Parses the response.
- Returns structured results to the task runtime.
- Preserves source URLs and useful snippets.
- Handles network errors, timeouts, and API failures.
- Reports when web search is unavailable.
- Allows the model to summarize the returned evidence.

Do not present search results as if they were generated from offline model knowledge.

API key protection

- Never commit a real API key to the repository.
- Never hard-code the key into public source files.
- Never print the key in logs.
- Never include the key in screenshots, exception messages, or diagnostic exports.
- Keep configuration and secrets out of version control.
- Remember that a key embedded in an APK can potentially be extracted.

A user-supplied API key stored locally is suitable for a hobby application, but it cannot be guaranteed secret from a determined person who can inspect the installed application.

Do not require Tavily for local inference.

---

9. Memory Architecture: Local Storage and Turso

LilyAi must distinguish conversational history from reusable memory and task execution records.

Local data categories

Recommended categories include:

1. Approved user preferences.
2. Approved facts and project knowledge.
3. Reusable procedures.
4. Conversation history.
5. Task timeline and execution events.
6. Tool results and relevant references.
7. Application settings.
8. Model metadata and download state.

Use a local structured database, such as SQLite, for metadata, task records, and local memory.

Large documents, model files, and other binary data should not be stored as database blobs without a clear reason.

Cloud memory

Turso is the planned cloud memory service.

Only selected, approved memories and procedures should be synchronized.

Do not automatically upload complete conversations, terminal output, screen contents, or private action histories.

Synchronization requirements

The design should support:

- Local-first operation.
- Explicit synchronization boundaries.
- Stable record identifiers.
- Duplicate prevention.
- Retryable synchronization.
- Error reporting.
- Safe conflict handling.
- Clear indication of cloud versus local state.

Do not allow a failed synchronization to prevent local operation.

Approval workflow

Suggested memory workflow:

1. LilyAi identifies a potentially reusable fact or procedure.
2. The application presents a proposed memory.
3. The user reviews and approves or rejects it.
4. Approved memory is saved locally.
5. Eligible approved memory may be synchronized according to the user's settings.

The model must not silently turn unverified statements into permanent facts.

---

10. Python Execution Environment and Terminal

The terminal is a core capability, but it must not bypass the application's safety controls.

Architecture

Separate the terminal interface, command authorization, Python execution, and task scheduler.

The application should not execute arbitrary AI-generated strings directly in an unrestricted shell.

Required behavior

- Display the command or script before execution when approval is required.
- Apply command permission rules.
- Use bounded execution time.
- Capture standard output and standard error.
- Record the exit status.
- Support cancellation where possible.
- Avoid blocking the main UI thread.
- Handle exceptions and subprocess failures.
- Keep logs local by default.
- Provide clear messages for commands that are not permitted.

Python environment

Embedded Python must be tested on Android before depending on third-party packages.

The compatibility test should cover:

- Python startup.
- Script execution.
- File access in the application's private directory.
- Standard output and error.
- Package availability.
- Native extension compatibility.
- Threading and subprocess behavior.
- Cancellation and cleanup.
- Communication between Python and Android code.

Some desktop Python packages require native libraries or system facilities that are unavailable on Android.

Do not assume that installing a package on desktop Linux means it will work inside the APK.

Terminal permissions

The terminal must follow an explicit permission model.

Use narrowly scoped permissions and distinguish harmless local operations from commands that can modify data, access the network, or interact with the device.

Never promise unrestricted root access. An ordinary Android application does not automatically have root privileges.

---

11. Supervised Task Runtime

The task runtime coordinates planning, tools, actions, cancellation, and logging.

It must be separate from the language model itself.

Suggested task lifecycle

"CREATED → PLANNING → AWAITING_APPROVAL → RUNNING → VERIFYING → COMPLETED"

Additional terminal states include:

- "FAILED"
- "CANCELLED"
- "BLOCKED"
- "NEEDS_USER_INPUT"

Not every task requires an approval transition, but the configured permission policy must determine when approval is mandatory.

Task execution rules

- Keep one authoritative state for each task.
- Validate tool arguments before execution.
- Check permissions immediately before consequential actions.
- Do not treat model-generated plans as executable authority.
- Record tool outcomes.
- Verify actions when possible.
- Stop on unexpected conditions.
- Keep cancellation state available to every executing component.
- Prevent accidental duplicate execution.
- Limit retries and automation loops.
- Record why a task stopped.

Repetitive automation

The selected default is supervised mode.

The planned session limit is 10 runs.

Each session should have:

- A clearly defined goal.
- A session approval.
- A run counter.
- A maximum run limit.
- Cancellation support.
- A record of each run.
- A defined stopping condition.
- A rule to stop when unexpected conditions occur.

A retry must not bypass an approval that is required for the original action.

---

12. Task Timeline, Logs, and Troubleshooting

Task records should be separate from user-facing chat messages.

Recommended event fields:

- Task identifier.
- Event identifier.
- Timestamp.
- Event type.
- Task state.
- Action or tool name.
- Approval status.
- Relevant result summary.
- Error category and message.
- Cancellation state.

Potential event types include:

- Task created.
- Plan prepared.
- Approval requested.
- Approval granted or rejected.
- Tool started.
- Tool completed.
- Action verified.
- Action failed.
- Cancellation requested.
- Task stopped.
- Task completed.

Keep sensitive information out of logs wherever possible.

Do not log API secrets, passwords, or unnecessary screen contents.

Logs should help answer:

- What did LilyAi attempt?
- Was approval required?
- Was approval granted?
- Which tool ran?
- What was the result?
- Why did the task stop?
- Did cancellation actually complete?

---

13. User Interface

Primary interface

The primary interface is a floating prompt and conversation panel.

The first version should prioritize usability and stability over visual complexity.

Recommended components:

- Floating bubble.
- Expandable chat panel.
- Prompt input.
- Send button.
- Stop button.
- Execution status.
- Approval dialog or panel.
- Tool activity display.
- Task history access.
- Settings access.

Status visibility

The user should be able to distinguish:

- Thinking.
- Preparing a plan.
- Waiting for approval.
- Running a tool.
- Interacting with the screen.
- Searching the web.
- Waiting for a result.
- Cancelling.
- Completed.
- Failed.
- Blocked.

Do not leave the user guessing whether the assistant is still working.

Appearance customization

Support basic customization of bubble position, bubble size, opacity, and panel size.

Store settings locally and validate saved values before applying them.

UI responsiveness

Long-running inference, file processing, downloads, network calls, and scripts must not block the main UI thread.

The Stop button must remain accessible during task execution.

---

14. Repository Skeleton

Use the following structure as the intended starting layout.

This is a proposed logical repository blueprint, not a claim that these files already exist.

LilyAi/
├── README.md
├── LilyAiProjectnotes.md
├── LICENSE
├── .gitignore
├── .editorconfig
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DECISIONS.md
│   ├── BUILD_GUIDE.md
│   ├── DEVICE_COMPATIBILITY.md
│   ├── PERMISSIONS.md
│   ├── SECURITY.md
│   └── TEST_PLAN.md
│
├── app/
│   ├── build.gradle
│   └── src/
│       └── main/
│           ├── AndroidManifest.xml
│           │
│           ├── java/
│           │   └── <package_path>/
│           │       ├── MainActivity.kt
│           │       ├── overlay/
│           │       │   ├── OverlayService.kt
│           │       │   └── OverlayController.kt
│           │       ├── accessibility/
│           │       │   └── LilyAccessibilityService.kt
│           │       ├── bridge/
│           │       │   └── PythonBridge.kt
│           │       ├── runtime/
│           │       │   ├── TaskService.kt
│           │       │   └── CancellationController.kt
│           │       ├── permissions/
│           │       │   └── PermissionManager.kt
│           │       └── model/
│           │           └── ModelManager.kt
│           │
│           ├── python/
│           │   └── lilyai/
│           │       ├── __init__.py
│           │       ├── config.py
│           │       ├── assistant.py
│           │       │
│           │       ├── llm/
│           │       │   ├── __init__.py
│           │       │   ├── engine.py
│           │       │   └── model_manager.py
│           │       │
│           │       ├── agent/
│           │       │   ├── __init__.py
│           │       │   ├── planner.py
│           │       │   ├── task_manager.py
│           │       │   ├── state_machine.py
│           │       │   └── cancellation.py
│           │       │
│           │       ├── tools/
│           │       │   ├── __init__.py
│           │       │   ├── registry.py
│           │       │   ├── web_search.py
│           │       │   ├── python_runner.py
│           │       │   └── device_actions.py
│           │       │
│           │       ├── permissions/
│           │       │   ├── __init__.py
│           │       │   └── policy.py
│           │       │
│           │       ├── memory/
│           │       │   ├── __init__.py
│           │       │   ├── local_store.py
│           │       │   ├── approved_memory.py
│           │       │   └── sync.py
│           │       │
│           │       ├── history/
│           │       │   ├── __init__.py
│           │       │   └── task_log.py
│           │       │
│           │       └── utils/
│           │           ├── __init__.py
│           │           └── logging_utils.py
│           │
│           └── res/
│               ├── layout/
│               ├── drawable/
│               ├── mipmap/
│               └── values/
│
├── tests/
│   ├── test_task_state.py
│   ├── test_cancellation.py
│   ├── test_permission_policy.py
│   ├── test_memory.py
│   ├── test_task_log.py
│   └── test_tool_registry.py
│
├── scripts/
│   ├── check_environment.py
│   └── validate_project.py
│
├── .github/
│   └── workflows/
│       └── android-build.yml
│
└── assets/
    └── README.md

Skeleton rules

1. Replace "<package_path>" with the actual Android package directory.
2. Use Kotlin where native Android integration is necessary; Python remains the primary application logic language.
3. Adapt the Gradle structure to the chosen Android Gradle Plugin and embedded Python runtime.
4. Do not create every placeholder file immediately.
5. Create files only when their milestone is reached.
6. Avoid maintaining duplicate implementations of the same task state or permission policy.
7. Keep generated build outputs, API keys, downloaded model weights, and private local databases out of Git.
8. Store large models in application-managed storage, not in the source repository.
9. The skeleton is subject to the early Python/Android bridge compatibility test.

---

15. Proposed Module Responsibilities

Module| Responsibility
"assistant.py"| Coordinate assistant requests
"llm/engine.py"| Provide a stable interface to local inference
"llm/model_manager.py"| Manage model availability and metadata
"agent/planner.py"| Prepare task plans
"agent/task_manager.py"| Manage task lifecycle and orchestration
"agent/state_machine.py"| Validate legal task transitions
"agent/cancellation.py"| Propagate cancellation
"tools/registry.py"| Register and validate available tools
"tools/web_search.py"| Integrate Tavily
"tools/python_runner.py"| Run authorized Python scripts
"tools/device_actions.py"| Interface with permitted device actions
"permissions/policy.py"| Enforce tool and action permissions
"memory/local_store.py"| Manage local structured memory
"memory/approved_memory.py"| Manage approval of reusable knowledge
"memory/sync.py"| Coordinate optional cloud synchronization
"history/task_log.py"| Record task timeline events
"OverlayService.kt"| Manage the native floating interface
"LilyAccessibilityService.kt"| Perform supported accessibility interactions
"PythonBridge.kt"| Coordinate native Android and Python calls
"CancellationController.kt"| Coordinate Android-side cancellation

These boundaries are intended to prevent the model, user interface, and execution environment from becoming tightly coupled.

---

16. Technology Selection Policy

The exact dependency versions must be selected and recorded during implementation.

Android

Choose a compatible combination of:

- Android SDK.
- Android Gradle Plugin.
- Gradle.
- Kotlin.
- AndroidX dependencies.
- Minimum and target SDK settings.
- Embedded Python runtime.
- Native library ABIs.

Android 11 is the baseline compatibility target. Newer Android versions should also be considered when practical.

Do not choose an unnecessarily new build toolchain without checking compatibility with the Python embedding approach.

Python

Prefer the standard library where practical.

Add dependencies only when they materially improve the application.

For every dependency, verify:

- Android compatibility.
- Supported Python version.
- Native extension requirements.
- License.
- Storage cost.
- Runtime memory cost.
- Maintenance status.
- Whether an offline alternative exists.

Local inference

Keep the model runtime behind a stable interface so that the selected engine can be replaced without rewriting the entire application.

Test the chosen runtime on the actual phone before committing to the final integration.

Database

Use a local database for application records.

Use Turso only for the approved cloud memory synchronization scope.

Do not require an internet connection to open the local database.

---

17. Build and Development Workflow

The goal is to develop directly on the Android phone where practical.

However, the build environment must be validated rather than assumed.

Early environment checks

Before creating the full application:

1. Confirm the phone's Android version and architecture.
2. Determine whether the chosen development environment can run the required build tools.
3. Verify Java availability.
4. Verify Gradle and Android SDK compatibility.
5. Verify the embedded Python build process.
6. Determine whether native libraries can be built or obtained for the required Android ABI.
7. Build and install a minimal APK.
8. Confirm that the APK launches successfully.

If building directly on the phone proves unreliable, select a reproducible alternative build path, such as a compatible remote build environment or GitHub Actions.

The preference for phone-based development does not justify keeping a broken build pipeline.

Reproducibility

Record the selected versions and build commands.

A future developer should be able to reproduce the APK without guessing dependency versions.

Use a clean build before declaring a release milestone complete.

---

18. Development Sequence and Milestones

The implementation must proceed in dependency order.

Milestone 0 — Architecture consolidation

Objective: Freeze the initial architecture.

Tasks:

- Maintain this document as the consolidated specification.
- Record exact dependency choices.
- Define the Android package name.
- Define minimum SDK and target SDK.
- Define the Python embedding strategy.
- Define the model runtime candidate.
- Define the build environment.
- Identify unresolved architecture questions.

Acceptance criteria:

- No contradictory architectural decisions remain.
- Unknown historical option details are not fabricated.
- The initial scope is clear.
- Compatibility risks have owners and test plans.

Milestone 1 — Environment and APK compatibility

Objective: Prove that the chosen toolchain works.

Tasks:

- Prepare the build environment.
- Create a minimal Android application.
- Build and install the APK.
- Verify startup on the OPPO A92.
- Record device and build details.

Acceptance criteria:

- A real APK is produced.
- Installation succeeds.
- The application launches.
- Build instructions are reproducible.

Milestone 2 — Embedded Python

Objective: Prove that Python works inside the Android application.

Tasks:

- Embed Python.
- Add the minimal native bridge.
- Execute a Python function.
- Return a result to Android.
- Test errors and cancellation behavior.

Acceptance criteria:

- Python runs inside the installed application.
- Native-to-Python communication works.
- Errors do not crash the app unexpectedly.
- The main UI remains responsive.

Milestone 3 — Local language model

Objective: Validate one primary offline model.

Tasks:

- Select a candidate runtime and model.
- Integrate model loading.
- Execute an offline prompt.
- Measure memory and speed.
- Test under realistic phone conditions.

Acceptance criteria:

- A local prompt succeeds without internet access.
- Model memory usage is measured.
- The phone remains usable during inference.
- The model fits within the chosen resource budget.
- Limitations are documented.

Milestone 4 — Core chat interface

Objective: Create a usable conversation interface.

Tasks:

- Add the prompt input.
- Add message rendering.
- Connect the interface to local inference.
- Add progress and error status.
- Keep long-running work off the UI thread.

Acceptance criteria:

- The user can send prompts.
- Responses appear correctly.
- The interface remains responsive.
- Offline conversation works.

Milestone 5 — Overlay and permissions

Objective: Enable the floating prompt interface.

Tasks:

- Implement the overlay service.
- Add the floating bubble.
- Add expand and collapse behavior.
- Implement permission guidance.
- Add the required appearance settings.

Acceptance criteria:

- The overlay works after permission is granted.
- Permission denial is handled safely.
- The bubble can be repositioned.
- The overlay can be closed.
- It behaves correctly during application lifecycle changes.

Milestone 6 — Task runtime and Stop control

Objective: Establish controlled execution.

Tasks:

- Implement task states.
- Add cancellation propagation.
- Add a visible Stop button.
- Record task events.
- Prevent queued actions from running after cancellation.

Acceptance criteria:

- Stop cancels queued actions.
- Supported active operations are interrupted.
- The UI reports cancellation truthfully.
- No new device action starts after cancellation has been acknowledged by the scheduler.
- Failed cancellation is visible and handled.

Milestone 7 — Permissions and device actions

Objective: Add supervised device interaction.

Tasks:

- Integrate the accessibility service.
- Define tool permissions.
- Add approval handling.
- Implement a small set of supported actions.
- Verify results after actions.

Acceptance criteria:

- The service requires user authorization.
- Unauthorized actions are rejected.
- Expected actions execute on a supported test screen.
- Unexpected conditions stop the task.
- Every action has a recorded outcome.

Milestone 8 — Python terminal

Objective: Provide controlled script execution.

Tasks:

- Add the terminal interface.
- Connect to the Python execution environment.
- Implement command and script permissions.
- Capture output and errors.
- Add bounded execution and cancellation.

Acceptance criteria:

- Approved scripts run.
- Output is visible.
- Failures are reported.
- Restricted commands are rejected.
- The UI remains responsive.

Milestone 9 — Local memory and task history

Objective: Preserve approved knowledge and execution history.

Tasks:

- Implement local structured storage.
- Separate approved memory from conversation history.
- Record task events.
- Add memory review and approval.
- Test database recovery and duplicate handling.

Acceptance criteria:

- Local memory survives an application restart.
- Private task logs remain local by default.
- Rejected memory proposals are not silently persisted as approved facts.
- Task history explains the result of an execution.

Milestone 10 — Tavily web search

Objective: Add optional online search.

Tasks:

- Implement the Tavily integration.
- Handle the API key safely.
- Parse search results.
- Preserve source references.
- Handle offline and failed network requests.

Acceptance criteria:

- Search works with a valid key and network connection.
- Source URLs are retained.
- API failures are handled.
- Offline conversation still works without Tavily.

Milestone 11 — Turso synchronization

Objective: Synchronize approved memory.

Tasks:

- Configure the cloud connection.
- Define the synchronization schema.
- Implement stable identifiers.
- Add retries and conflict handling.
- Restrict synchronization to eligible memory records.

Acceptance criteria:

- Approved eligible memories can synchronize.
- Private task logs are not uploaded by default.
- Duplicate records are prevented.
- Local operation survives cloud failure.

Milestone 12 — Hardening and release preparation

Objective: Validate the integrated application.

Tasks:

- Test cancellation races.
- Test permissions and unexpected UI states.
- Test memory and storage limits.
- Test low-memory behavior.
- Test repeated overlay opening and closing.
- Test offline operation.
- Test downloads and integrity checks.
- Test long-running automation.
- Verify privacy-sensitive logging.
- Produce a clean release APK.

Acceptance criteria:

- Core offline features work.
- Stop and permission controls pass.
- Storage use remains within the configured budget.
- Major failure paths have been tested.
- The release build and test results are documented.

Milestones may be split into smaller implementation tasks. Do not skip prerequisite compatibility tests merely to produce a feature demonstration.

---

19. Testing Strategy

Testing must include unit tests, integration tests, and actual-device tests.

Python unit tests

Prioritize:

- Task state transitions.
- Cancellation handling.
- Permission policies.
- Tool argument validation.
- Memory approval.
- Duplicate prevention.
- Task timeline recording.
- Retry limits.

Android integration tests

Test:

- Python bridge.
- Overlay lifecycle.
- Accessibility authorization.
- Activity and service lifecycle.
- Background operation behavior.
- Model loading.
- Cancellation propagation.

Real-device tests

Test on the OPPO A92 wherever possible:

- Cold startup.
- Model loading.
- Offline prompts.
- Long prompts.
- Overlay use over another app.
- Screen locking and unlocking.
- App switching.
- Memory pressure.
- Thermal behavior.
- Failed network requests.
- Model download interruptions.
- Stop during inference.
- Stop during an automation sequence.
- Repeated sessions.

Do not substitute a desktop test for an Android compatibility test.

---

20. Security and Privacy

LilyAi is a local assistant capable of interacting with other applications. Security boundaries must be part of the architecture.

Core principles

- Least privilege.
- Explicit user approval.
- Local-first storage.
- Minimal data collection.
- No hard-coded secrets.
- Bounded execution.
- Clear action logs.
- Cancellation support.
- Safe failure behavior.

Untrusted input

Treat model output, web pages, retrieved documents, and terminal output as untrusted data.

Instructions found in a web page or document must not override LilyAi's permission policy.

A tool result must not automatically authorize a subsequent action.

Consequential actions

Actions such as deleting data, changing security settings, sending messages, purchasing goods, or exposing private information may require explicit confirmation according to the action policy.

Do not rely solely on a model's self-assessment of whether an action is safe.

Data boundaries

- Keep local databases in application-private storage where appropriate.
- Do not expose secrets through logs.
- Avoid uploading screen contents unless a separately approved feature requires it.
- Make cloud synchronization scope clear.
- Keep large downloaded models separate from sensitive task history.

---

21. Model Downloads and Storage Management

The application may provide an optional in-app model downloader.

Required functionality:

- Display download progress.
- Handle interrupted downloads.
- Verify integrity using a trusted expected hash when available.
- Validate the downloaded model's expected metadata.
- Prevent incomplete downloads from being treated as installed.
- Support safe cleanup of temporary files.
- Check available storage before downloading.
- Avoid keeping redundant model copies unnecessarily.

A checksum confirms that a file matches an expected value; it does not independently establish that the original file is trustworthy.

Keep the configured AI storage allocation at or below 30 GB.

The actual initial model budget should be selected after the model runtime has been validated.

---

22. Git and Repository Hygiene

The repository must contain source code, documentation, tests, and build configuration.

It should not contain private runtime data.

Exclude from version control

Examples include:

- API keys.
- Local environment files containing secrets.
- Model weights.
- Temporary model downloads.
- Local user databases.
- Conversation histories.
- Private task logs.
- Android build outputs.
- Python caches.
- Local IDE state.
- Signing credentials.

Suggested ".gitignore" entries

# Android build outputs
.gradle/
build/
app/build/
local.properties
*.apk
*.aab

# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Secrets and local configuration
.env
.env.*
!.env.example

# Local data
data/
models/
downloads/
*.db
*.sqlite
*.sqlite3

# Signing credentials
*.jks
*.keystore

# IDE files
.idea/
.vscode/

Review ignore rules before committing. Do not exclude source files or configuration templates needed to reproduce the build.

---

23. Build Automation and GitHub Actions

GitHub Actions may be used for reproducible builds when direct phone builds are impractical.

The workflow should:

1. Check out the repository.
2. Install the selected JDK.
3. Configure the compatible Android SDK.
4. Set up the pinned Gradle toolchain.
5. Run automated tests.
6. Build the intended APK.
7. Preserve build logs and relevant test results.
8. Publish an artifact only when the build succeeds.

Do not place Tavily keys, signing credentials, or other secrets directly in workflow files.

If the embedded Python runtime requires special build steps or native artifacts, document and validate those steps before relying on CI.

A successful CI build does not prove that the APK works correctly on the OPPO A92. Device testing remains mandatory.

---

24. Topic Decision Register

This register preserves the project decisions available in the current consolidated project context. It is not a claim that every original topic transcript has been reconstructed verbatim.

Topic| Recorded subject or decision| Status
Topic 1| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 2| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 3| Repetitive automation: supervised mode, approved session, stop on unexpected conditions; maximum 10 runs per session.| Decisions recorded
Topic 4| Turso cloud memory for selected memories and procedures; private task history remains local by default; suggested memories require approval.| Decisions recorded
Topic 5| Embed Python in the APK subject to an early compatibility test; optional in-app model download with progress and integrity checks.| Decisions recorded
Topic 6| Action control is part of the project scope; preserve explicit approval and cancellation boundaries.| Partial consolidated record
Topic 7| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 8| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 9| Task timeline records steps, approvals, outcomes, and errors separately from readable conversation; private logs local by default; bubble position, size, opacity, and panel size customizable.| Decisions recorded
Topic 10| Topic-specific detailed decisions are not fully available in the current summary.| Verify original record if needed
Topic 11| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 12| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 13| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 14| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 15| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 16| Framework, Python/Android bridge, build method, inference integration, overlay architecture, task runtime, and dependencies: recorded selections were Option B.| Decisions recorded; exact option descriptions need source verification
Topic 17| Development planning continued from Topic 16; complete independent decision text is not present in the current summary.| Verify original record if needed
Topic 18| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 19| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 20| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 21| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 22| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 23| Terminal experience, Python execution environment, and terminal command permissions: Option B for each decision.| Decisions recorded; exact option descriptions need source verification
Topic 24| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 25| Original detailed decision text is not present in the available summary.| Verify original record if needed
Topic 26| Architecture freeze and consolidation; selected build sequence, early compatibility tests, milestone acceptance criteria, and development handoff: Option B for each decision.| Decisions recorded; exact option descriptions need source verification

Topic register maintenance rule

When an original topic transcript or decision record becomes available:

1. Verify the selected option and its complete meaning.
2. Update the corresponding topic entry.
3. Preserve decisions that remain unchanged.
4. Record any approved revision and its reason.
5. Do not invent historical decisions to make the table appear complete.

The consolidated requirements in Sections 2–23 should guide implementation where they provide sufficient detail. Unavailable original option wording must not be represented as an exact historical decision.

---

25. Known Risks and Unresolved Questions

The following issues must be resolved by testing or a documented implementation decision.

Critical compatibility risks

1. Whether the selected embedded Python distribution works with the target Android toolchain.
2. Whether the selected inference runtime supports the OPPO A92's Android version and CPU architecture.
3. Whether the selected model can run within an acceptable memory and thermal budget.
4. Whether the chosen build environment can reliably build the complete APK.
5. Whether the required native dependencies can be bundled and loaded correctly.

Execution risks

6. Whether all relevant tool operations can respond to cancellation.
7. How to safely handle an unresponsive Python process.
8. How to verify that screen actions succeeded.
9. How to handle Android background-service restrictions.
10. How to prevent duplicate or overlapping automation sessions.

Data risks

11. How to manage local database migrations.
12. How to handle Turso synchronization conflicts.
13. How to protect API credentials.
14. How to enforce the 30 GB storage allocation.
15. How to clean up interrupted downloads without deleting a working model.

These risks should be tracked with a test, an expected result, and a fallback plan.

---

26. Definition of a Successful First Release

The first useful release does not need every advanced capability.

It should establish a stable foundation.

A successful initial release should:

- Install and launch on the target phone.
- Run a compatible local model.
- Support offline conversation.
- Provide a functional floating prompt interface.
- Remain responsive during inference.
- Support an operational Stop control.
- Enforce the initial tool permission policy.
- Provide a controlled Python execution path.
- Store task history locally.
- Respect the storage allocation.
- Document known limitations.
- Provide a reproducible build process.

Tavily search, Turso synchronization, advanced screen automation, and expanded terminal functionality can be introduced in subsequent milestones.

Do not describe planned functionality as complete merely because its module or interface exists.

---

27. Development Handoff Checklist

Before implementation begins, confirm:

- [ ] This document is committed as "LilyAiProjectnotes.md".
- [ ] Original decision records are retained where available.
- [ ] Unknown Topic 1–26 details are not fabricated.
- [ ] Android package name is selected.
- [ ] SDK and build tool versions are documented.
- [ ] Python embedding strategy is identified.
- [ ] A minimal APK compatibility test is planned.
- [ ] Local model runtime candidates are identified.
- [ ] Model resource measurements are planned.
- [ ] Overlay and accessibility permissions are documented.
- [ ] Cancellation behavior has explicit acceptance criteria.
- [ ] Terminal permissions are defined before arbitrary execution is introduced.
- [ ] Local memory and cloud memory boundaries are documented.
- [ ] API keys and private data are excluded from Git.
- [ ] The first implementation milestone is clearly defined.

---

28. Final Instructions to the Development Assistant

Use this document as the working project specification.

Begin by checking the repository's actual contents and identifying the first incomplete milestone. Do not assume the proposed repository skeleton already exists.

Before changing the architecture, compare the proposed change with the recorded decisions and explain any conflict.

Prioritize a working, testable offline Android application over ambitious features that have not passed compatibility tests.

Keep Python at the center of the application logic while using native Android code where necessary.

Protect the user's data, enforce permissions, and make cancellation a real execution capability.

Make incremental progress, preserve working components, document test results, and ask the owner before making consequential architectural changes.

The goal is a reliable, privacy-conscious, offline-first LilyAi APK that can grow into a supervised, tool-using phone assistant without exceeding the device's practical resource limits.
