# System Architecture

## Overview

AETHOS implements a sophisticated multi-stage AI orchestration system that processes visual data through a deterministic pipeline of specialized models and services.

## Architecture Flow

```
User Upload Image
        ↓
Flask Backend (app.py)
        ↓
Agent Service (agent_service.py)
        ↓
----------------------------------------
| YOLOv8 | BLIP | Tesseract OCR | Wiki |
----------------------------------------
        ↓
Data Enrichment & Synthesis
        ↓
Result Interface (templates/result.html)
```

## Core Components

### 1. Flask Backend (`app.py`)
- **Routes**: `/analyze`, `/orchestrate`, `/audit`, `/brand`
- **File Handling**: Secure upload processing with 20MB limit
- **Response Rendering**: Dynamic template rendering with ML results

### 2. AI Services Layer (`services/`)

#### Object Detection (`object_detection.py`)
- **Model**: YOLOv8 (nano, medium, large variants)
- **Function**: Detect objects with confidence scores
- **Output**: Object labels + confidence metrics

#### Image Captioning (`capture_service.py`)
- **Model**: BLIP (Bootstrapping Language-Image Pre-training)
- **Function**: Generate natural language descriptions
- **Output**: Contextual image captions

#### OCR Service (`ocr_service.py`)
- **Engine**: Tesseract OCR
- **Function**: Extract text from images
- **Output**: Structured text content

#### Knowledge Enrichment (`wiki_service.py`)
- **API**: Wikipedia REST API
- **Function**: Fetch contextual information for detected objects
- **Output**: Enriched object metadata

#### Agent Orchestration (`agent_service.py`)
- **Architecture**: Deterministic "Critic Loop" pattern
- **Function**: Coordinate multi-model outputs into coherent responses
- **Modes**: Analysis, Audit, Brand, Orchestrate

### 3. Frontend Layer
- **Templates**: Jinja2-based HTML templates
- **Static Assets**: CSS/JS for terminal-inspired UI
- **Upload Handling**: Client-side file validation

## Data Flow

1. **Input Processing**: Image upload via multipart/form-data
2. **Parallel Execution**: All AI models run concurrently
3. **Data Synthesis**: Agent service combines results
4. **Response Generation**: Structured JSON/HTML output
5. **Knowledge Enhancement**: Wikipedia API integration

## Technology Stack

- **Backend**: Python 3.10+, Flask
- **AI/ML**: Ultralytics YOLOv8, Transformers BLIP, Tesseract OCR
- **Data**: Wikipedia API, Geopy
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Deployment**: Ready for Docker/Render/Railway

## Performance Considerations

- **Model Selection**: YOLOv8n for speed, YOLOv8l for accuracy
- **Caching**: Wikipedia responses cached to reduce API calls
- **File Limits**: 20MB upload limit for memory management
- **Async Processing**: Non-blocking model execution

## Security Features

- **File Validation**: Secure filename handling
- **Size Limits**: Configurable upload restrictions
- **Path Sanitization**: Prevent directory traversal
- **Input Validation**: Command parsing and sanitization
