import { render, screen, fireEvent } from '@testing-library/react';
import ChatWidget from '../src/components/ChatWidget';

// Mock the useChat hook
jest.mock('../src/hooks/useChat', () => ({
  useChat: () => ({
    messages: [],
    isLoading: false,
    error: null,
    sessionId: 'test-session',
    suggestedQuestions: ['Question 1?', 'Question 2?'],
    sendMessage: jest.fn(),
    clearError: jest.fn(),
  }),
}));

// Mock the useLanguage hook
jest.mock('../src/hooks/useLanguage', () => ({
  useLanguage: () => ({
    language: 'en',
    setLanguage: jest.fn(),
    languages: [
      { code: 'en', name: 'English', nativeName: 'English' },
      { code: 'hi', name: 'Hindi', nativeName: 'हिंदी' },
    ],
  }),
}));

describe('ChatWidget', () => {
  it('renders chat toggle button initially', () => {
    render(<ChatWidget />);

    const toggleButton = screen.getByRole('button');
    expect(toggleButton).toBeInTheDocument();
  });

  it('opens chat panel when toggle button is clicked', () => {
    render(<ChatWidget />);

    const toggleButton = screen.getByRole('button');
    fireEvent.click(toggleButton);

    // After clicking, chat panel should be visible
    expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
  });

  it('displays suggested questions', () => {
    render(<ChatWidget />);

    const toggleButton = screen.getByRole('button');
    fireEvent.click(toggleButton);

    expect(screen.getByText('Question 1?')).toBeInTheDocument();
    expect(screen.getByText('Question 2?')).toBeInTheDocument();
  });
});
