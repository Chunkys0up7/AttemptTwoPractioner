import React, { useState, useEffect, useRef, useCallback } from 'react';
import { GoogleGenAI, Chat, GenerateContentResponse } from "@google/genai";
import { PaperAirplaneIcon, ChatBubbleLeftRightIcon, ChevronDownIcon, ChevronUpIcon, UserCircleIcon, LlmIcon as BotIcon } from '../../icons';
import { ChatMessage, SpecificComponentType, AIComponent } from '../../types';
import Button from '../common/Button';
import Card from '../common/Card'; // Ensure this import is correct and Card.tsx is properly exporting

// Ensure API_KEY is handled by the environment as per guidelines.
// The application MUST NOT provide a UI for entering it.
const API_KEY = process.env.API_KEY;

interface ChatAssistantProps {
  selectedComponentType: SpecificComponentType | null;
  currentComponentData: Partial<AIComponent>; // Pass current form data for context
}

/**
 * AI Chat Assistant component to help users create components.
 * Uses Gemini API for chat functionality.
 * @param {ChatAssistantProps} props - Component props.
 * @returns {JSX.Element} The ChatAssistant component.
 */
const ChatAssistant: React.FC<ChatAssistantProps> = ({ selectedComponentType, currentComponentData }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const chatInstance = useRef<Chat | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const ai = useRef<GoogleGenAI | null>(null);

  useEffect(() => {
    if (API_KEY) {
      try {
        ai.current = new GoogleGenAI({ apiKey: API_KEY });
      } catch (e) {
        console.error("Failed to initialize GoogleGenAI:", e);
        setError("Failed to initialize AI Assistant. API Key might be missing or invalid in environment.");
      }
    } else {
        // This error will be displayed if the API_KEY is not set during build/runtime.
        // It's important not to prompt the user for the key in the UI.
        setError("AI Assistant cannot be initialized: API_KEY is not configured in the environment.");
    }
  }, []);

  const initializeChat = useCallback(() => {
    if (!ai.current) {
      if (!API_KEY) {
         setError("AI Assistant cannot be initialized: API_KEY is not configured in the environment.");
      } else {
         setError("AI Assistant not initialized. Please ensure the API Key is valid.");
      }
      return;
    }
    
    let systemInstruction = "You are an expert AI assistant. Help the user create and configure an AI component for an AI Ops Console.";
    if (selectedComponentType) {
      systemInstruction += ` The user is currently working on a component of type: ${selectedComponentType}.`;
    }
    systemInstruction += " Provide concise, helpful, and relevant information. If asked for code, provide it in markdown code blocks.";
    
    try {
      chatInstance.current = ai.current.chats.create({
        model: 'gemini-2.5-flash-preview-04-17',
        config: {
          systemInstruction: systemInstruction,
          // Disable thinking for lower latency responses, suitable for a chat bot.
          thinkingConfig: { thinkingBudget: 0 } 
        },
      });
      // Add a welcome message or type-specific intro
      const initialBotMessage: ChatMessage = {
        id: `bot-${Date.now()}`,
        text: selectedComponentType 
              ? `Hi! How can I help you with your ${selectedComponentType} component today?`
              : "Hi! How can I assist you with creating a component?",
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages([initialBotMessage]);
    } catch (e) {
      console.error("Failed to create chat:", e);
      setError("Failed to initialize chat session.");
      setMessages([]);
    }
  }, [selectedComponentType]);

  useEffect(() => {
    // Re-initialize chat if the component type changes and the chat is open
    if (isOpen && ai.current) {
      initializeChat();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedComponentType, isOpen]); // initializeChat dependency is implicitly handled

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!userInput.trim() || isLoading || !chatInstance.current) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      text: userInput,
      sender: 'user',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setUserInput('');
    setIsLoading(true);
    setError(null);

    try {
      // Include relevant form data as context for the bot
      let promptWithContext = userInput;
      if (Object.keys(currentComponentData).length > 0) {
        let contextString = "\n\n--- Current Component Configuration ---\n";
        if (currentComponentData.name) contextString += `Name: ${currentComponentData.name}\n`;
        if (currentComponentData.description) contextString += `Description: ${currentComponentData.description}\n`;
        
        if (selectedComponentType === 'Python Script' || selectedComponentType === 'TypeScript Script') {
          if(currentComponentData.typeSpecificData?.codeContent) contextString += `Code:\n${currentComponentData.typeSpecificData.codeContent}\n`;
        } else if (selectedComponentType === 'LLM Prompt Agent' && currentComponentData.typeSpecificData?.llmPrompt) {
          const { systemPrompt, userPromptTemplate } = currentComponentData.typeSpecificData.llmPrompt;
          if (systemPrompt) contextString += `System Prompt: ${systemPrompt}\n`;
          if (userPromptTemplate) contextString += `User Prompt Template: ${userPromptTemplate}\n`;
        }
        // Add more context for other types as needed
        contextString += "--- End of Configuration ---\n";
        promptWithContext = `${userInput}${contextString}`;
      }
      
      const stream = await chatInstance.current.sendMessageStream({ message: promptWithContext });
      
      let botResponseText = '';
      // Use a new ID for the bot's message block
      const botMessageId = `bot-${Date.now()}`;
      // Add a placeholder for the bot's message to update it as chunks arrive
      setMessages(prev => [...prev, { id: botMessageId, text: '...', sender: 'bot', timestamp: new Date() }]);

      for await (const chunk of stream) { // chunk is GenerateContentResponse
        botResponseText += chunk.text;
        setMessages(prev => prev.map(msg => 
          msg.id === botMessageId ? { ...msg, text: botResponseText } : msg
        ));
      }
    } catch (e) {
      console.error("Error sending message to Gemini:", e);
      setError("Sorry, I couldn't get a response. Please try again.");
      const errorMessage: ChatMessage = {
        id: `bot-error-${Date.now()}`,
        text: "An error occurred while fetching the response.",
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className={`fixed bottom-4 right-4 z-30 transition-all duration-300 ease-in-out ${isOpen ? 'w-96' : 'w-auto'}`}>
      <Card className="shadow-2xl !p-0 flex flex-col" noPadding>
        <div 
          className="flex items-center justify-between p-3 bg-primary text-white cursor-pointer rounded-t-xl"
          onClick={() => {
            setIsOpen(!isOpen);
            if (!isOpen && !messages.length && API_KEY) { // Initialize chat on first open if API_KEY exists
              initializeChat();
            }
          }}
        >
          <div className="flex items-center space-x-2">
            <ChatBubbleLeftRightIcon className="w-6 h-6" />
            <span className="font-semibold">AI Coding Assistant</span>
          </div>
          {isOpen ? <ChevronDownIcon className="w-5 h-5" /> : <ChevronUpIcon className="w-5 h-5" />}
        </div>

        {isOpen && (
          <>
            <div className="h-80 flex flex-col bg-neutral-50 p-3 space-y-3 overflow-y-auto">
              {messages.map(msg => (
                <div key={msg.id} className={`flex items-end space-x-2 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
                  {msg.sender === 'bot' && <BotIcon className="w-6 h-6 text-primary flex-shrink-0 self-start"/>}
                  <div 
                    className={`max-w-[80%] p-2.5 rounded-lg shadow-sm text-sm
                      ${msg.sender === 'user' 
                        ? 'bg-primary text-white rounded-br-none' 
                        : 'bg-white text-neutral-700 border border-neutral-200 rounded-bl-none'}`}
                  >
                    {/* Basic markdown for code blocks - can be improved with a library */}
                    {msg.text.split('\n').map((line, i) => {
                        if (line.startsWith('```')) return <hr key={i} className="my-1 border-dashed" />; // Simple separator for code blocks
                        return <p key={i} className="whitespace-pre-wrap break-words">{line}</p>;
                    })}
                  </div>
                  {msg.sender === 'user' && <UserCircleIcon className="w-6 h-6 text-neutral-400 flex-shrink-0 self-start"/>}
                </div>
              ))}
              <div ref={messagesEndRef} />
              {isLoading && messages[messages.length -1]?.sender === 'user' && ( // Show typing indicator if last message was user
                <div className="flex items-end space-x-2">
                  <BotIcon className="w-6 h-6 text-primary flex-shrink-0"/>
                  <div className="max-w-[80%] p-2.5 rounded-lg shadow-sm text-sm bg-white text-neutral-700 border border-neutral-200 rounded-bl-none">
                    <div className="flex space-x-1">
                      <span className="w-1.5 h-1.5 bg-neutral-400 rounded-full animate-pulse delay-75"></span>
                      <span className="w-1.5 h-1.5 bg-neutral-400 rounded-full animate-pulse delay-150"></span>
                      <span className="w-1.5 h-1.5 bg-neutral-400 rounded-full animate-pulse delay-300"></span>
                    </div>
                  </div>
                </div>
              )}
            </div>
            {error && <p className="p-2 text-xs text-red-600 bg-red-50 border-t border-red-200">{error}</p>}
            <div className="p-3 border-t border-neutral-200 bg-white rounded-b-xl">
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSendMessage()}
                  placeholder={API_KEY ? "Ask for help..." : "AI Assistant unavailable"}
                  className="flex-grow p-2.5 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary disabled:bg-neutral-100 bg-white text-neutral-900 placeholder-neutral-500"
                  disabled={isLoading || !API_KEY}
                />
                <Button 
                  onClick={handleSendMessage} 
                  variant="primary" 
                  size="md" 
                  className="!p-2.5"
                  disabled={isLoading || !userInput.trim() || !API_KEY}
                  isLoading={isLoading}
                >
                  <PaperAirplaneIcon className="w-5 h-5" />
                </Button>
              </div>
            </div>
          </>
        )}
      </Card>
    </div>
  );
};

export default ChatAssistant;