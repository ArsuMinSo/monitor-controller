# Architecture Improvement Plan

## Current Issues
1. Complex async/sync coordination in WebSocket broadcasting
2. Polling fallbacks indicating unreliable real-time updates
3. Tight coupling between HTTP handlers and WebSocket manager
4. State scattered across multiple components

## Phase 1: Immediate Fixes (1-2 days)

### 1.1 Simplify WebSocket Broadcasting
- Replace complex `broadcast_queue_state_sync` with dedicated thread approach
- Remove polling fallbacks from frontend
- Add proper error handling for WebSocket disconnections

### 1.2 Clean Up Frontend
- Remove `setTimeout(() => refreshQueue(), 100)` calls
- Trust WebSocket updates exclusively
- Add connection status indicators

## Phase 2: Architecture Cleanup (1-2 weeks)

### 2.1 Extract State Management
```python
# state_manager.py
class StateManager:
    def __init__(self):
        self.state = {
            "slideshows": [],
            "current_slideshow": None,
            "current_slide": 0,
            "playing": False,
            "queue": {"queue": [], "current_index": 0, "is_playing": False}
        }
        self.subscribers = []
    
    def update(self, path, value):
        # Update state and notify subscribers
        pass
    
    def subscribe(self, callback):
        self.subscribers.append(callback)
```

### 2.2 Event-Driven Updates
```python
# events.py
from enum import Enum

class EventType(Enum):
    QUEUE_UPDATED = "queue_updated"
    SLIDESHOW_CHANGED = "slideshow_changed"
    CLIENT_CONNECTED = "client_connected"

class EventBus:
    def __init__(self):
        self.handlers = {}
    
    def emit(self, event_type, data):
        # Emit event to all handlers
        pass
    
    def on(self, event_type, handler):
        # Register event handler
        pass
```

## Phase 3: Technology Migration (Future)

### 3.1 Replace HTTP Server with FastAPI
- Async by default
- Better error handling
- Built-in WebSocket support
- Automatic API documentation

### 3.2 Add Redis for State Management
- Centralized state store
- Built-in pub/sub for real-time updates
- Persistence across restarts

### 3.3 Frontend Modernization
- React/Vue with proper state management
- WebSocket client with automatic reconnection
- Optimistic UI updates

## Best Approach for Your Situation

**For Current Project: Keep existing architecture, fix the core issues**
1. Simplify async/sync coordination 
2. Remove polling fallbacks
3. Add proper error handling
4. Document the architecture decisions

**For Next Project: Start fresh with modern stack**
1. FastAPI + Redis + React/Vue
2. Event-driven architecture from day one
3. Proper separation of concerns
4. Modern development practices

## Technology Recommendations

### Backend
- **FastAPI** - Modern Python web framework with async support
- **Redis** - For state management and pub/sub
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server

### Frontend  
- **React/Vue** - Component-based UI
- **Redux/Vuex** - State management
- **Socket.IO** - Reliable WebSocket with fallbacks
- **TypeScript** - Type safety

### Infrastructure
- **Docker** - Containerization
- **nginx** - Reverse proxy
- **PostgreSQL** - Persistent data storage
