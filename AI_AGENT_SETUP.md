# 🤖 AI Agent Setup & Configuration Guide

## ✅ AI Agent Status: **FULLY IMPLEMENTED**

Your AI agent is located in the backend and is already integrated into the system!

---

## 📍 Where is the AI Agent?

### Core AI Service

**Location**: `backend/app/services/ai_service.py`

This file contains the `AIContextGenerator` class that:

- Generates intelligent meeting context using Mistral AI
- Analyzes meeting details (title, description, attendees, time)
- Creates structured context with topics, checklists, and suggestions
- Learns from previous meetings for better recommendations

### Integration Points

1. **Service Layer**: `backend/app/services/base.py` → `ContextService` class
2. **Controller**: `backend/app/controllers/meeting_controller.py` → Auto-generates context on meeting creation
3. **Context Controller**: `backend/app/controllers/context_controller.py` → Manages context CRUD operations

---

## 🔧 How It Works

### When You Create a Meeting:

1. **Meeting Created** → The meeting is saved to the database
2. **AI Agent Triggered** → `ContextService.generate_and_create_context()` is called
3. **AI Analysis** → Mistral AI analyzes:
   - Meeting title and description
   - Attendee list
   - Meeting time
   - Historical context from previous meetings
4. **Context Generated** → AI creates:
   - Meeting type classification
   - AI-generated brief summary
   - Key topics to discuss
   - Preparation checklist
   - Suggested agenda
   - Estimated importance level
   - Recommended prep time
   - Attendee context
   - Potential outcomes
   - Follow-up suggestions

---

## 🚀 Setting Up Mistral AI (Required)

The AI agent uses **Ollama** to run Mistral locally or via API.

### Option 1: Local Setup (Recommended)

1. **Install Ollama**

   ```bash
   # Windows
   winget install Ollama.Ollama

   # Or download from: https://ollama.com/download
   ```

2. **Pull Mistral Model**

   ```bash
   ollama pull mistral
   ```

3. **Start Ollama Service**

   ```bash
   ollama serve
   ```

   This runs on `http://localhost:11434` by default

4. **Verify It's Running**
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Option 2: Remote Ollama Server

If you have Ollama running on another server:

1. **Update Backend `.env`**
   ```env
   MISTRAL_BASE_URL=http://your-server-ip:11434
   ```

---

## 📝 Configuration

### Backend Configuration (`.env`)

```env
# AI/Mistral Configuration
MISTRAL_BASE_URL=http://localhost:11434
```

### Default Settings

Located in `backend/app/services/ai_service.py`:

- **Model**: `mistral:latest`
- **Temperature**: 0.7 (balanced creativity)
- **Top P**: 0.9
- **Top K**: 40
- **Timeout**: 60 seconds

---

## 🎯 Features & Capabilities

### 1. **Intelligent Meeting Analysis**

- Automatically classifies meeting type (1-on-1, team sync, client call, etc.)
- Generates concise 2-3 sentence brief
- Identifies key discussion topics

### 2. **Preparation Assistance**

- Creates customized preparation checklist
- Suggests agenda items
- Estimates required prep time
- Rates meeting importance

### 3. **Attendee Context**

- Analyzes attendee roles
- Provides context for each participant
- Suggests communication strategies

### 4. **Learning & Improvement**

- Learns from previous meetings
- Improves recommendations over time
- Adapts to user patterns

### 5. **Fallback Handling**

- Provides basic context if AI is unavailable
- Graceful error handling
- Never blocks meeting creation

---

## 🧪 Testing the AI Agent

### 1. **Check if Ollama is Running**

```bash
curl http://localhost:11434/api/tags
```

Expected response:

```json
{
  "models": [
    {
      "name": "mistral:latest",
      "modified_at": "..."
    }
  ]
}
```

### 2. **Create a Test Meeting**

Use the frontend form (as shown in your screenshot):

- ✅ Check "Auto-generate AI Context"
- Fill in meeting details
- Click "Create Meeting"

### 3. **View Generated Context**

The AI will generate context which you can view:

- In the meeting detail page
- Via API: `GET /api/v1/contexts/meeting/{meeting_id}`

---

## 🐛 Troubleshooting

### Issue: "Context generation failed"

**Solution 1: Verify Ollama is Running**

```bash
# Check service status
ollama list

# If not running:
ollama serve
```

**Solution 2: Check Model is Downloaded**

```bash
# List available models
ollama list

# If mistral is not there:
ollama pull mistral
```

**Solution 3: Check Backend Logs**
Look for errors in uvicorn output:

```
Context generation failed for meeting...
```

### Issue: "No AI context generated"

Check if the checkbox "Auto-generate AI Context" is enabled in the frontend.

### Issue: "Timeout errors"

Increase timeout in `backend/app/services/ai_service.py`:

```python
self.timeout = 120.0  # Increase from 60 to 120 seconds
```

---

## 📊 AI Context Structure

When the AI generates context, it returns:

```python
{
    "meeting_type": "team_sync",  # or: one_on_one, client_call, brainstorm, etc.
    "brief": "Weekly team synchronization to discuss progress...",
    "topics": [
        "Sprint progress review",
        "Blocker discussion",
        "Next week planning"
    ],
    "checklist": [
        "Review completed tasks",
        "Prepare status update",
        "List any blockers"
    ],
    "agenda": [
        "Progress updates",
        "Blocker discussion",
        "Action items"
    ],
    "importance": "high",  # or: medium, low
    "prep_time": "15",  # minutes
    "attendees": {
        "engineer@example.com": "Team member - Engineering",
        "manager@example.com": "Team lead"
    },
    "outcomes": [
        "Clear action items defined",
        "Blockers identified and assigned"
    ],
    "follow_up": [
        "Send meeting notes",
        "Update task tracker"
    ],
    "confidence": 85  # AI confidence score (0-100)
}
```

---

## 🔄 Manual Context Generation

You can also manually trigger context generation:

### Via API

```bash
POST /api/v1/contexts/generate/{meeting_id}?force_regenerate=true
```

### Via Frontend

1. Navigate to meeting detail page
2. Click "Regenerate Context" button (if implemented)

---

## 🎨 Customizing AI Behavior

### Modify the Prompt

Edit `backend/app/services/ai_service.py` → `_build_prompt()` method to customize:

- Output format
- Analysis depth
- Focus areas
- Additional context

### Adjust AI Parameters

Edit `backend/app/services/ai_service.py` → `_call_ollama()` method:

```python
"options": {
    "temperature": 0.7,  # 0.0 = deterministic, 1.0 = creative
    "top_p": 0.9,        # Nucleus sampling
    "top_k": 40          # Top-k sampling
}
```

---

## ✨ Recent Fixes Applied

1. ✅ Fixed Pydantic v2 compatibility issues
2. ✅ Fixed meeting repository update method signatures
3. ✅ Fixed context service integration
4. ✅ Fixed meeting creation with proper Meeting model instantiation
5. ✅ Added missing repository methods (get_by_id, get_recent_for_user, etc.)

---

## 🚦 Next Steps

1. **Install Ollama** (if not already installed)
2. **Pull Mistral model**: `ollama pull mistral`
3. **Start Ollama**: `ollama serve`
4. **Restart your backend**: The uvicorn server should pick up changes
5. **Create a test meeting** with "Auto-generate AI Context" checked
6. **Check the logs** to see AI generation in action!

---

## 📚 Related Files

- **AI Service**: [backend/app/services/ai_service.py](backend/app/services/ai_service.py)
- **Context Service**: [backend/app/services/base.py](backend/app/services/base.py) (ContextService class)
- **Meeting Controller**: [backend/app/controllers/meeting_controller.py](backend/app/controllers/meeting_controller.py)
- **Context Controller**: [backend/app/controllers/context_controller.py](backend/app/controllers/context_controller.py)
- **Context Repository**: [backend/app/repositories/base.py](backend/app/repositories/base.py) (ContextRepository class)
- **Context Model**: [backend/app/models/db.py](backend/app/models/db.py) (Context class)

---

## 🎉 Summary

Your AI agent is **fully implemented and ready to use**! Just ensure Ollama is running with the Mistral model, and the system will automatically generate intelligent meeting context for every meeting you create.

The AI agent will help you:

- Prepare better for meetings
- Save time on meeting prep
- Get personalized insights
- Improve meeting effectiveness

Happy meeting! 🚀
