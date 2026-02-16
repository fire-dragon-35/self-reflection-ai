<script lang="ts">
  import { ClerkProvider, SignedIn, SignedOut, SignInButton, UserButton } from 'svelte-clerk/client';
  import LandingPage from './lib/LandingPage.svelte';
  import MainPage from './lib/MainPage.svelte';
  import { dark } from '@clerk/themes'
  
  const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
  const githubUrl = "https://github.com/fire-dragon-35/self-reflection-ai"
</script>

<ClerkProvider publishableKey={clerkPubKey} appearance={{theme: dark}}>
  <div class="min-h-screen bg-[#0a0e14] flex flex-col">
    <!-- header -->
    <header class="bg-[#151a21] border-b border-gray-800">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <h1 class="text-xl font-semibold">Reflektion <span class="text-red-500 text-sm">Alpha</span></h1>
        
        <SignedIn>
          <div class="flex items-center gap-4">
            <a 
              href={githubUrl} 
              target="_blank"
              class="text-sm text-gray-400 hover:text-gray-100"
            >
              Source code
            </a>
            <button class="text-sm px-3 py-1.5 bg-blue-500 hover:bg-blue-600 rounded-lg">
              Free • 1.2k/10k ⚡
            </button>
            <UserButton />
          </div>
        </SignedIn>
        
        <SignedOut>
          <div class="flex items-center gap-4">
            <a 
              href={githubUrl} 
              target="_blank"
              class="text-sm text-gray-400 hover:text-gray-100"
            >
              Source code
            </a>
            <SignInButton mode="modal">
              <button class="btn-primary text-sm">
                Sign in
              </button>
            </SignInButton>
          </div>
        </SignedOut>
      </div>
    </header>

    <div class="flex-1">
      <SignedIn>
        <MainPage />
      </SignedIn>

      <SignedOut>
        <LandingPage />
      </SignedOut>
    </div>

    <!-- footer -->
    <footer class="py-6">
      <div class="max-w-7xl mx-auto px-6 text-center text-sm text-gray-400">
        Reflektion 2026
      </div>
    </footer>
  </div>
</ClerkProvider>