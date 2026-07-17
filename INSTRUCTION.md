You are now acting as the Lead System Architect and Senior AI Engineer for PROJECT THEMIS.

Your responsibility is NOT to redesign the project from scratch.

Your responsibility is to carefully review the entire existing codebase, architecture, documentation, API contracts, frontend, backend, AI pipeline, Unity integration, ESP32 communication, database models, and every related component, then update them to follow the latest PROJECT THEMIS V6 architecture decisions.

IMPORTANT:

DO NOT remove existing features unless they directly conflict with the new architecture.

DO NOT simplify the project.

DO NOT reduce functionality.

Instead, preserve everything that is still valid and only refactor the components that need to evolve into the new architecture.

==================================================
PROJECT THEMIS V6 FINAL ARCHITECTURE
==================================================

PROJECT THEMIS is no longer a People Counting System.

PROJECT THEMIS is now an AI-powered Railway Decision Intelligence Platform.

The primary objective is NOT counting passengers.

The primary objective is estimating carriage occupancy and available usable space in real time to support operational decisions.

==================================================
NEW CORE PHILOSOPHY
==================================================

Replace every concept related to:

- People Counting
- Human Counting
- Passenger Counting

with

Spatial Occupancy Intelligence.

The AI estimates how much usable space remains inside a carriage.

The AI does NOT need to know the exact number of passengers.

The AI estimates occupancy using spatial analysis.

==================================================
AI PIPELINE
==================================================

Replace previous pipeline:

Camera
↓

YOLO
↓

Person Counting
↓

Occupancy

with:

4 Ceiling Fisheye Cameras
↓

Image Capture
↓

Image Preprocessing

- Resize
- Normalize
- Fisheye Dewarping

↓

Spatial Occupancy Segmentation

↓

Occupancy Grid Generation

↓

Spatial Occupancy Score

↓

Density Classification

↓

Spatial Fusion Engine

↓

Redistribution Engine

↓

Dashboard

↓

Announcement

↓

Hardware Controller

↓

Historical Database

↓

CALES Engine

↓

Inspection Priority

==================================================
SPATIAL OCCUPANCY SEGMENTATION
==================================================

The AI should NOT focus on detecting humans.

Instead, it should estimate:

Occupied Space

vs

Free Space.

Anything occupying usable standing space should be considered occupied.

Examples:

- Human
- Luggage
- Backpack
- Stroller
- Wheelchair
- Bicycle
- Large Object

The AI does NOT need to classify each object.

Only estimate whether the usable standing area is occupied.

==================================================
FLOOR SEGMENTATION
==================================================

Remove every terminology related to:

Floor Visibility

Replace with

Spatial Occupancy Segmentation

or

Free Space Segmentation

The objective is estimating usable space, NOT detecting floor color.

==================================================
OUTPUT VARIABLES
==================================================

Replace old variables such as:

people_count

human_count

passenger_count

pax_per_m2

with

occupancy_ratio

free_space_ratio

density_indicator

occupancy_grid

spatial_occupancy_score

==================================================
FUSION ENGINE
==================================================

Redesign the Fusion Engine.

Instead of merging detections,

merge Occupancy Maps.

Each of the four fisheye cameras first generates its own Occupancy Grid.

The Spatial Fusion Engine combines all four occupancy grids into a single carriage occupancy map.

No global people tracking.

No ReID.

No duplicate counting.

==================================================
REDISTRIBUTION ENGINE
==================================================

Redistribution must occur ONLY after occupancy analysis.

Pipeline:

Spatial Occupancy Score

↓

Density Classification

↓

Redistribution Analysis

↓

Find Best Target Carriage

↓

Recommendation

↓

Announcement

↓

Door Logic

The Door Controller must NEVER open immediately after RED density.

Door automation only occurs if:

1. Current carriage is RED

AND

2. Another carriage has significantly lower occupancy

Otherwise:

Door remains closed.

==================================================
ANNOUNCEMENT
==================================================

Announcement is generated AFTER redistribution recommendation.

Example:

"Carriage 6 has available capacity.
Passengers are advised to move to Carriage 6."

NOT

"Carriage is full."

==================================================
JSON CONTRACT
==================================================

Update every API response.

Old:

{
  "people_count":183,
  "floor_visibility":18,
  "pax_per_m2":4.1
}

Replace with

{
  "car_id":"car_04",
  "occupancy_ratio":0.86,
  "free_space_ratio":0.14,
  "density_indicator":"RED",
  "recommended_target":"car_06",
  "door_action":"OPEN_MIDDLE",
  "announcement":"MOVE_TO_CAR_06",
  "spatial_occupancy_score":0.86,
  "cales_score":0.82,
  "inspection_priority":1
}

==================================================
UNITY
==================================================

Unity remains a Digital Twin.

Unity captures images every 5 seconds.

Unity sends images to FastAPI.

Unity receives PipelineState.

Unity visualizes:

- Indicator Light
- Dashboard
- Door Animation
- Recommendation
- Historical Statistics

==================================================
ESP32
==================================================

ESP32 only executes commands.

ESP32 does NOT perform AI.

Commands include:

Door

Indicator Light

Speaker

==================================================
IMPORTANT
==================================================

Before modifying any file:

1. Read the entire project.

2. Understand dependencies.

3. Detect every component still using People Counting.

4. Refactor only what is necessary.

5. Preserve architecture consistency.

6. Keep naming conventions consistent.

7. Never leave old and new concepts mixed together.

==================================================
EXPECTED OUTPUT
==================================================

For every modified file provide:

1. Why the file needs to change.

2. Architecture reasoning.

3. Exact implementation.

4. Potential side effects.

5. Updated flow.

6. Compatibility with remaining modules.

7. Whether additional files also need updating.

If another file must also change because of the update, continue updating it automatically until the whole architecture is internally consistent.

Think like a CTO reviewing a production system, not like an autocomplete model.


ARCHITECTURE CONSISTENCY RULE

The highest priority is maintaining architectural consistency across the entire project.

If a single architectural decision changes, automatically identify every related component that must also be updated.

This includes:

- Backend
- AI Pipeline
- Unity
- API Contracts
- Dashboard
- Database
- ESP32
- Documentation
- Sequence Diagrams
- Flowcharts
- README
- Configuration Files
- Environment Variables
- Constants
- Data Models
- Variable Names
- Comments
- Tests

Never update only one file if the architecture requires multiple dependent updates.

The final result must behave as if the project had been designed using the latest architecture from the beginning.

Before finishing, perform a complete architecture consistency audit and report every modification made, every dependency updated, and every remaining issue if any.
