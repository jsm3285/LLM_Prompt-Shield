import React, { useRef } from 'react';
import PromptManager from '../components/PromptManager';
import Chatbot from '../components/Chatbot';

export default function LlmTestPage() {
  const chatbotRef = useRef(null);

  const handleSelectPrompt = (promptText) => {
    if (chatbotRef.current?.setInputText) {
      chatbotRef.current.setInputText(promptText);
    }
  };

  const handleExecutePrompt = (promptText) => {
    if (chatbotRef.current?.sendPromptDirectly) {
      chatbotRef.current.sendPromptDirectly(promptText);
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: '1.5rem', height: 'calc(100vh - 140px)', minHeight: '680px' }}>
      {/* Left: Dedicated Prompt Scenarios Library */}
      <section style={{ height: '100%', overflow: 'hidden' }}>
        <PromptManager
          onSelectPrompt={handleSelectPrompt}
          onExecutePrompt={handleExecutePrompt}
        />
      </section>

      {/* Right: Clean Full-Height LLM Testing & A/B Comparison Interface */}
      <section style={{ height: '100%', overflow: 'hidden' }}>
        <Chatbot ref={chatbotRef} />
      </section>
    </div>
  );
}
