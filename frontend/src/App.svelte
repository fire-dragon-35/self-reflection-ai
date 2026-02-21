<script lang="ts">
  import { ClerkProvider, SignedIn, SignedOut, SignInButton } from 'svelte-clerk/client';
  import LandingPage from './lib/LandingPage.svelte';
  import MainPage from './lib/MainPage.svelte';
  import Navbar from './lib/Navbar.svelte';
  import { dark } from '@clerk/themes';
  import logo from './assets/logo.svg';
  
  const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
  const githubUrl = "https://github.com/fire-dragon-35/self-reflection-ai";
  
  let navbarRef: any;
</script>

<ClerkProvider publishableKey={clerkPubKey} appearance={{theme: dark}}>
  <div class="min-h-screen bg-[#0a0e14] flex flex-col">
    <header class="bg-[#151a21] border-b border-gray-800">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <img src={logo} alt="Reflektion" class="w-8 h-8" />
          <h1 class="text-xl font-semibold">
            Reflektion <span class="text-red-500 text-xs italic" style="font-family: cursive;">Alpha</span>
          </h1>
        </div>
        
        <SignedIn>
          <Navbar bind:this={navbarRef} />
        </SignedIn>
        
        <SignedOut>
          <SignInButton mode="modal">
            <button class="btn-primary text-sm">
              Sign in
            </button>
          </SignInButton>
        </SignedOut>
      </div>
    </header>

    <div class="flex-1">
      <SignedIn>
        <MainPage {navbarRef} />
      </SignedIn>

      <SignedOut>
        <LandingPage />
      </SignedOut>
    </div>

    <footer class="py-6">
      <div class="max-w-7xl mx-auto px-6 text-center text-sm text-gray-400">
        <div class="mb-2">
          <a 
            href={githubUrl} 
            target="_blank"
            class="hover:text-gray-100 underline"
          >
            Source code
          </a>
        </div>
        <div>Reflektion 2026</div>
      </div>
    </footer>
  </div>
</ClerkProvider>