<script lang="ts">
  import { ClerkProvider, SignedIn, SignedOut, SignIn, UserButton } from 'svelte-clerk/client';
  import Chat from './lib/Chat.svelte';
  
  const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
</script>

<ClerkProvider publishableKey={clerkPubKey}>
  <div class="min-h-screen bg-gray-50">
    <SignedIn>
      <header class="bg-white shadow-sm">
        <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">Reflektion</h1>
          <UserButton />
        </div>
      </header>
      
      <main class="max-w-4xl mx-auto p-4">
        <Chat />
      </main>
    </SignedIn>
    
    <SignedOut>
      <div class="min-h-screen flex items-center justify-center">
        <div class="text-center">
          <h1 class="text-4xl font-bold mb-8">Reflektion</h1>
          <p class="text-gray-600 mb-8">AI-powered self-reflection</p>
          <SignIn />
        </div>
      </div>
    </SignedOut>
  </div>
</ClerkProvider>