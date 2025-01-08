export interface Message {
    id: string;
    content: string;
    sender: 'user' | 'dot';
    timestamp: Date;
  }
  
  export interface ChatState {
    messages: Message[];
    isConnected: boolean;
    isLoading: boolean;
  }