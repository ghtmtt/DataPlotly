---
title: Workflow {{ env.WORKFLOW }} failed for {{ env.DOCKER_TAG }}
labels: bug
---

Workflow {{ env.WORKFLOW }} failed for {{ env.DOCKER_TAG }} at: {{ date | date('YYYY-MM-DD HH:mm:ss') }}

{{ env.TEST_RESULT }}
