# Agent Implementation Checklist & Milestone Roadmap

## Milestone 0: Repository Audit & Design
- [x] Inspect existing repository structure, files, dependencies, and git history
- [x] Verify Python runtime and virtual environment (`Python 3.12.10`, `venv`)
- [x] Install missing dependencies (`greenlet`, `asyncpg`, `qdrant-client`, `rank_bm25`, `langgraph`)
- [x] Run and verify existing backend test suite (`pytest` passes 2/2 tests)
- [x] Document system architecture (`docs/architecture.md`)
- [x] Create project roadmap & checklist (`docs/implementation_checklist.md`)
- [x] Audit external credentials & prepare configuration defaults

## Milestone 1: Working Voice Prototype
- [x] Initialize frontend application with Next.js 16 (App Router), TypeScript, and Tailwind CSS v4
- [x] Implement Web Audio API microphone capture and volume amplitude analysis for real waveform visualization
- [x] Implement backend WebSocket voice streaming session endpoint (`/api/v1/voice/session` and `/api/v1/voice/stream`)
- [x] Implement voice session state machine (Idle, Connecting, Listening, Processing, Speaking, Interrupted, Failed, Ended)
- [x] Implement real-time audio visualizer with multi-band dynamic cyan/blue waveforms reacting to actual sound levels
- [x] Implement live transcript display and bi-directional typed fallback chat
- [x] Add English and Malayalam native language selection with code-switching intent support
- [x] Connect backend voice responder (Google GenAI integration + high-fidelity local cadence synthesizer fallback)
- [x] Acceptance verification: Verified voice session creation, spoken answer playback, interruption handling, and typed fallback (6/6 tests passing)

## Milestone 2: Vehicle Discovery Vertical Slice
- [ ] Populate synthetic demo dealership and vehicle inventory seed data with source & verification timestamps
- [ ] Implement deterministic vehicle search and filtering endpoint (`/api/v1/vehicles`)
- [ ] Implement vehicle detail and comparison endpoints (`/api/v1/vehicles/{id}`, `/api/v1/vehicles/compare`)
- [ ] Connect voice assistant tool execution to `search_vehicles`
- [ ] Render interactive vehicle cards in the customer UI during conversation
- [ ] Acceptance verification: Voice query for vehicles returns real backend inventory cards with verified specifications

## Milestone 3: Multi-Agent Orchestration
- [ ] Implement LangGraph supervisor workflow with typed state (`AgentState`)
- [ ] Implement specialist agent nodes: Discovery, Knowledge, Finance, Lead Qualification, Appointment, Verification & Handoff
- [ ] Implement bounded retries, execution limits, and structured error boundaries
- [ ] Add structured tracing and observability for agent runs and tool invocations
- [ ] Acceptance verification: Complex customer intents correctly routed, validated, and logged

## Milestone 4: Finance and CRM
- [ ] Implement deterministic reducing-balance EMI calculator adhering strictly to section 10 formula
- [ ] Add comprehensive unit tests for zero interest, standard tenure, invalid inputs, and boundary conditions
- [ ] Implement customer preferences and lead generation models and database tables
- [ ] Implement authenticated lead management endpoints for CRM ingestion
- [ ] Build interactive EMI calculator widget in customer interface
- [ ] Acceptance verification: Voice prompt generates persisted lead and calculated EMI scenario

## Milestone 5: Appointment Coordination
- [ ] Implement appointment availability check tool and slot validation
- [ ] Implement test-drive request creation with idempotency and duplicate prevention
- [ ] Implement salesperson handoff with structured summary and context notes
- [ ] Display confirmed vs pending appointment states in customer interface
- [ ] Acceptance verification: Successful test drive booked, failure cases handled without false confirmation

## Milestone 6: Dealership Dashboard
- [ ] Build dealership staff authentication (JWT) and role-based permissions
- [ ] Build Overview dashboard with funnel indicators and metrics
- [ ] Build Lead Management table with filtering, search, and detail modal
- [ ] Build Conversation Details viewer with transcripts, tool calls, and handoff summaries
- [ ] Build Appointment calendar and management screen
- [ ] Acceptance verification: Authorized staff manage leads and review conversation traces

## Milestone 7: Reliability and Evaluation
- [ ] Write integration and end-to-end test suites across backend and frontend
- [ ] Build evaluation benchmark comparing Single-Agent, RAG-Agent, and Multi-Agent Supervisor
- [ ] Run 100+ synthetic scenarios testing English, Malayalam, ambiguous queries, and tool failures
- [ ] Acceptance verification: Evaluation metrics documented with reproducibility instructions

## Milestone 8: Pilot Deployment & Documentation
- [ ] Verify Docker Compose configuration for local and staging deployment
- [ ] Write user guide, setup instructions, and final project demonstration script
- [ ] Acceptance verification: Clean deployment from scratch on fresh machine
