import { RouterProvider } from 'react-router-dom';
import { Providers } from './providers';
import { router } from './router';
import { Toaster } from 'sonner';

function App() {
  return (
    <Providers>
      <RouterProvider router={router} />
      <Toaster
        position="top-right"
        richColors
        theme="dark"
        expand={false}
        closeButton
      />
    </Providers>
  );
}

export default App;
