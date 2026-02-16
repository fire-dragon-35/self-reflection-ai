<script lang="ts">
  import { SignInButton } from 'svelte-clerk/client';
  import demoImage from '../assets/demo.png';
</script>

<section class="max-w-6xl mx-auto px-6 py-20">
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
    <div>
      <h1 class="text-5xl lg:text-6xl font-semibold mb-6 leading-tight">
        Understand yourself through AI.
      </h1>
      <p class="text-xl text-gray-300 mb-8">
        Private conversations. Real insights.
      </p>
      <SignInButton mode="modal">
        <button class="btn-primary text-lg px-8 py-3">
          Sign in
        </button>
      </SignInButton>
    </div>

    <div>
      <img src={demoImage} alt="Reflektion app demo" class="rounded-lg border border-gray-800 w-full h-auto" />
    </div>
  </div>
</section>

<section class="max-w-4xl mx-auto px-6 py-16">
  <div class="space-y-6">
    <div class="border-l-2 border-blue-600 pl-6">
      <h3 class="font-semibold mb-1">Chat</h3>
      <p class="text-gray-400">Talk to AI about your thoughts and relationships</p>
    </div>
    
    <div class="border-l-2 border-blue-600 pl-6">
      <h3 class="font-semibold mb-1">Analyze</h3>
      <p class="text-gray-400">Get insights about your personality and attachment style</p>
    </div>
    
    <div class="border-l-2 border-blue-600 pl-6">
      <h3 class="font-semibold mb-1">Reflect</h3>
      <p class="text-gray-400">Understand patterns in how you think and relate to others</p>
    </div>
  </div>
</section>

<section class="max-w-4xl mx-auto px-6 py-16">
  <h3 class="text-2xl font-semibold mb-4">Built for privacy</h3>
  <p class="text-gray-300 leading-relaxed mb-8">
    Other apps store and sell your conversation data. We encrypt everything and never share it with anyone. 
    When you chat, Claude only sees a random user ID, not your name, email, or identity.
  </p>
  
  <p class="text-sm text-gray-400 border-t border-gray-800 pt-6">
    Reflektion is not therapy or medical advice. It's a tool for self-knowledge and reflection.
  </p>
</section>