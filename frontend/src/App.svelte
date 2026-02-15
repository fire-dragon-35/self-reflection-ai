<script lang="ts">
  import { ClerkProvider, SignedIn, SignedOut, SignInButton, UserButton } from 'svelte-clerk/client';
  import Chat from './lib/Chat.svelte';
  import Insights from './lib/Insights.svelte';
  import { dark } from '@clerk/themes'
  import heroImage from './assets/hero.jfif';
  import overviewImage from './assets/overview_reflektion.jfif';
  
  const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
</script>

<ClerkProvider publishableKey={clerkPubKey} appearance={{theme: dark}}>
  <div class="min-h-screen bg-[#0a0e14] flex flex-col">
    <!-- Navbar -->
    <header class="bg-[#151a21] border-b border-gray-800">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <h1 class="text-xl font-semibold">Reflektion <span class="text-red-500 text-sm">Alpha</span></h1>
        
        <SignedIn>
          <div class="flex items-center gap-4">
            <a 
              href="https://github.com/fire-dragon-35/self-reflection-ai" 
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
              href="https://github.com/fire-dragon-35/self-reflection-ai" 
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
    
    <!-- Main content -->
    <div class="flex-1">
      <SignedIn>
        <main class="max-w-7xl mx-auto p-6">
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
            <div class="lg:col-span-2">
              <Chat />
            </div>
            <div>
              <Insights />
            </div>
          </div>
          
          <!-- How it works section -->
          <div class="bg-[#1a1f2e] border border-gray-800 rounded-lg p-8">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              <!-- Content -->
              <div>
                <h2 class="text-2xl font-semibold mb-8">How it works & Privacy</h2>
                
                <div class="space-y-6">
                  <div>
                    <h3 class="font-semibold text-lg mb-4">The process</h3>
                    <div class="space-y-4">
                      <div class="border-l-2 border-blue-500 pl-4">
                        <p class="font-semibold mb-1">Chat</p>
                        <p class="text-sm text-gray-400">Talk about your day, relationships, or anything on your mind</p>
                      </div>
                      <div class="border-l-2 border-blue-500 pl-4">
                        <p class="font-semibold mb-1">Analyze</p>
                        <p class="text-sm text-gray-400">Generate insights about your Big Five personality and attachment style</p>
                      </div>
                      <div class="border-l-2 border-blue-500 pl-4">
                        <p class="font-semibold mb-1">Understand</p>
                        <p class="text-sm text-gray-400">Track patterns and understand yourself better over time</p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="border-t border-gray-700 pt-6">
                    <h3 class="font-semibold text-lg mb-4">Your privacy matters</h3>
                    <div class="space-y-3 text-sm text-gray-300">
                      <p><span class="font-semibold text-gray-100">Claude API:</span> Only receives a random identifier, for example 'user_12345'. No personal details such as name or email address are sent.</p>
                      <p><span class="font-semibold text-gray-100">Be mindful:</span> Still be cautious with sensitive information, as you would with any AI.</p>
                      <p><span class="font-semibold text-gray-100">Encrypted storage:</span> Chat history and analysis are encrypted and stored on our end for greater user experience. Will not be read by us.</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Image -->
              <div class="hidden lg:flex justify-center items-center">
                <div class="relative w-full scale-100">
                  <img src={overviewImage} alt="Reflektion overview" class="relative w-full rounded-xl shadow-2xl" />
                </div>
              </div>
            </div>
          </div>
        </main>
      </SignedIn>
      
      <SignedOut>
        <div class="max-w-6xl mx-auto px-6 py-20">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 class="text-5xl font-semibold mb-6">Reflektion</h1>
              <p class="text-xl text-gray-400 mb-8">
                AI-powered self-reflection for understanding your patterns and personality.
              </p>
              
              <p class="text-gray-300 mb-8 leading-relaxed">
                Reflektion helps you understand yourself through conversations with AI. 
                Chat about your thoughts and experiences, then get insights about your personality and attachment style.
              </p>
              
              <div class="space-y-4 mb-8">
                <div class="border-l-2 border-blue-500 pl-4">
                  <p class="font-semibold mb-1">Chat</p>
                  <p class="text-sm text-gray-400">Talk about your day, relationships, or anything on your mind</p>
                </div>
                <div class="border-l-2 border-blue-500 pl-4">
                  <p class="font-semibold mb-1">Analyze</p>
                  <p class="text-sm text-gray-400">Generate insights about your Big Five personality and attachment style</p>
                </div>
                <div class="border-l-2 border-blue-500 pl-4">
                  <p class="font-semibold mb-1">Grow</p>
                  <p class="text-sm text-gray-400">Track patterns and understand yourself better over time</p>
                </div>
              </div>
              
              <p class="text-sm text-gray-400">
                Fully encrypted • Anonymous • Open source
              </p>
            </div>
            
            <div>
              <img src={heroImage} alt="Reflektion" class="rounded-lg border border-gray-800 w-full" />
            </div>
          </div>
        </div>
      </SignedOut>
    </div>

    <!-- Footer -->
    <footer class="py-6">
      <div class="max-w-7xl mx-auto px-6 text-center text-sm text-gray-400">
        Reflektion 2026
      </div>
    </footer>
  </div>
</ClerkProvider>