import { createBrowserRouter } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { RootLayout } from '@/components/layout/RootLayout';
import { LoadingScreen } from '@/components/common/LoadingScreen';

// Lazy load pages for code splitting
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const AgentConsole = lazy(() => import('@/pages/AgentConsole'));
const MemoryVisualizer = lazy(() => import('@/pages/MemoryVisualizer'));
const ComplianceDashboard = lazy(() => import('@/pages/ComplianceDashboard'));
const OrionStation = lazy(() => import('@/pages/OrionStation'));
const Playground = lazy(() => import('@/pages/Playground'));
const Simulations = lazy(() => import('@/pages/Simulations'));

// Wrapper for lazy loaded components
const SuspenseWrapper = ({ children }: { children: React.ReactNode }) => (
  <Suspense fallback={<LoadingScreen />}>{children}</Suspense>
);

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: (
          <SuspenseWrapper>
            <Dashboard />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'agent',
        element: (
          <SuspenseWrapper>
            <AgentConsole />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'memory',
        element: (
          <SuspenseWrapper>
            <MemoryVisualizer />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'compliance',
        element: (
          <SuspenseWrapper>
            <ComplianceDashboard />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'orion',
        element: (
          <SuspenseWrapper>
            <OrionStation />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'playground',
        element: (
          <SuspenseWrapper>
            <Playground />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'simulations',
        element: (
          <SuspenseWrapper>
            <Simulations />
          </SuspenseWrapper>
        ),
      },
    ],
  },
]);
