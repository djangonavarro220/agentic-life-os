# Agentic Life OS

```mermaid
flowchart TD
  A[User or scheduled runtime job] --> B[life-os umbrella skill]
  B --> C[Resolve runtime and data directory]
  C --> D[Read skill-index.yaml]
  D --> E[Read private config]
  E --> K[Resolve configured source pointers]
  K --> F[Load needed subskills only]
  F --> G[Run routine or manual task]
  G --> H[Write tracking state outside repo]
```

Life OS keeps real data in runtime or external systems. Its private config stores source pointers and access instructions so the plugin can adapt to the user's existing setup without changing it.
