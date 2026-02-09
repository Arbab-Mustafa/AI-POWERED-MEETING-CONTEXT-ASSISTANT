FRONTEND - ContextMeet UI

Architecture: Component-based with Next.js
Language: TypeScript + React
Framework: Next.js 14 + Tailwind CSS

FOLDER STRUCTURE:

src/
app/ - Next.js app directory and pages
components/ - Reusable React components
services/ - API client and services
hooks/ - Custom React hooks
store/ - State management (Zustand)
types/ - TypeScript type definitions
utils/ - Utility functions
public/ - Static assets

SETUP INSTRUCTIONS:

1. Install Node.js (18+ recommended)

2. Install dependencies:
   npm install

3. Configure environment:
   cp .env.example .env.local
   Update .env.local with your settings

4. Run development server:
   npm run dev

Frontend will be available at: http://localhost:3000

ARCHITECTURE PRINCIPLES:

1. Component-Based
   - Reusable components in components/ folder
   - Single responsibility per component
   - Props-driven and composable

2. Type Safety
   - Full TypeScript coverage
   - Type definitions in types/ folder
   - No any types used

3. State Management
   - Zustand for global state (auth, user)
   - React hooks for local state
   - Minimal state at top level

4. Styling
   - Tailwind CSS for styling
   - Consistent color scheme
   - No custom CSS unless necessary
   - Light, professional design
   - No emoji usage

5. Performance
   - Code splitting via dynamic imports
   - Image optimization
   - Lazy loading where applicable
   - Proper caching strategies

COMPONENT STRUCTURE:

Each component should:

- Be in its own file (kebab-case name)
- Export as named export
- Include proper TypeScript types
- Have clear props interface
- Max 300-400 lines per component

Example:
src/components/MeetingCard.tsx

- Displays a single meeting
- Receives Meeting type as prop
- Exports MeetingCard component
- Fully typed and self-contained

STATE MANAGEMENT:

Using Zustand for:

- User authentication state
- User preferences
- Global notifications

Using React hooks for:

- Form state
- UI state (modals, dropdowns)
- Temporary data

STYLING GUIDELINES:

Colors:

- Primary: #2563eb (blue-600)
- Secondary: #1e40af (blue-800)
- Success: #10b981 (green)
- Error: #ef4444 (red)
- Gray scale for neutral elements

Typography:

- Headers: Bold, larger sizes
- Body: Regular weight, readable
- Labels: Medium weight
- Muted text: gray-600

Spacing:

- Use Tailwind spacing scale (4px base)
- Consistent padding and margins
- Proper whitespace between sections
