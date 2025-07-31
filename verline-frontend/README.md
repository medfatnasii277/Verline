# Verline Art Gallery - Frontend

## Overview

The frontend for Verline Art Gallery is a modern React application built with TypeScript and Vite. It provides an intuitive interface for artists to manage their artwork and for enthusiasts to discover, rate, and comment on paintings. The application features real-time notifications, comprehensive user profiles, and responsive design.

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: Tailwind CSS with custom components
- **UI Components**: shadcn/ui component library
- **State Management**: TanStack Query (React Query) for server state
- **Routing**: React Router for navigation
- **Real-time**: WebSocket connections for notifications
- **Authentication**: JWT token-based authentication with context
- **Forms**: React Hook Form with validation
- **Icons**: Lucide React icon library

## Features Implemented

### Authentication & User Management
- User registration and login forms
- Role-based access control (Artist/Enthusiast)
- Profile management with photo upload
- User dashboard with personalized content

### Painting Gallery
- Grid-based painting gallery with responsive design
- Advanced filtering by category, artist, and search terms
- Detailed painting view with zoom functionality
- Artist-only painting upload and management
- Image preview and validation

### Rating & Review System
- Interactive star rating component
- Role-based rating views (artists see ratings received, enthusiasts see ratings given)
- Real-time rating updates and averages

### Comment System
- Threaded comment display with replies
- Role-based comment views (artists see comments on their paintings, enthusiasts see their comments)
- Real-time comment notifications
- Comment editing and deletion

### Real-time Notifications
- WebSocket integration for instant notifications
- Toast notifications for user actions
- Notification history and management

### User Profiles
- Comprehensive profile pages with artwork galleries
- Bio, location, and website information
- Profile picture upload and management
- User statistics and activity tracking

## Installation & Setup

### Prerequisites
- Node.js 18+ 
- npm or yarn package manager

### Installation Steps

1. **Navigate to frontend directory**
   ```bash
   cd verline-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   Create a `.env` file in the frontend root:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Build for production**
   ```bash
   npm run build
   ```

## Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── ui/              # shadcn/ui components
│   ├── Header.tsx       # Navigation header
│   ├── PaintingCard.tsx # Painting display component
│   └── ...
├── contexts/            # React contexts
│   └── AuthContext.tsx  # Authentication state management
├── pages/               # Page components
│   ├── Home.tsx         # Homepage with gallery
│   ├── Login.tsx        # Authentication pages
│   ├── Profile.tsx      # User profile management
│   ├── PaintingDetail.tsx # Detailed painting view
│   └── ...
├── services/            # API service layer
│   └── api.ts           # Backend API integration
├── hooks/               # Custom React hooks
│   └── use-toast.ts     # Toast notification hook
├── lib/                 # Utility functions
│   └── utils.ts         # Helper functions
└── theme/               # Styling configuration
    └── victorianTheme.ts # Custom theme configuration
```

## API Integration

The frontend integrates with the Verline backend API through:

- **Authentication**: JWT token management with automatic refresh
- **Real-time Updates**: WebSocket connections for live notifications
- **File Uploads**: Image upload for paintings and profile pictures
- **RESTful APIs**: Full CRUD operations for all resources

## Key Components

### Authentication Flow
- Login/Register forms with validation
- JWT token storage and management
- Automatic token refresh and logout
- Protected routes based on authentication status

### Gallery Interface
- Responsive grid layout for paintings
- Lazy loading for performance
- Search and filter functionality
- Pagination for large datasets

### Profile Management
- Role-based profile interfaces
- Tabbed navigation for different data views
- Image upload with preview
- Form validation and error handling

### Real-time Features
- WebSocket connection management
- Automatic reconnection on disconnect
- Real-time notification delivery
- Connection status indicators

## Development Notes

### State Management
- TanStack Query for server state synchronization
- React Context for authentication state
- Local state for UI interactions
- Optimistic updates for better UX

### Performance Optimizations
- Code splitting with React.lazy
- Image lazy loading and optimization
- Query caching and background refetching
- Memoization of expensive computations

### Responsive Design
- Mobile-first approach with Tailwind CSS
- Flexible grid layouts
- Touch-friendly interface elements
- Optimized for various screen sizes

## Build & Deployment

### Development
```bash
npm run dev          # Start development server
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
```

### Production
```bash
npm run build        # Build for production
npm run preview      # Preview production build
```

## Browser Support

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## Contributing

1. Follow the existing code style and patterns
2. Use TypeScript for all new components
3. Implement responsive design for all UI elements
4. Include proper error handling and loading states
5. Test on multiple browsers and devices
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/1aeacbd2-36db-4d14-99f9-1cfc08b9ddb9) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/tips-tricks/custom-domain#step-by-step-guide)
