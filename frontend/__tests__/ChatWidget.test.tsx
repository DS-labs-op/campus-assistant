import { render, screen, fireEvent } from '@testing-library/react';
import ChatWidget from '../src/components/ChatWidget';

// Mock the useChat hook - must match the path used by ChatInterface
jest.mock('@/hooks/useChat', () => ({
  useChat: () => ({
    messages: [],
    isLoading: false,
    sendMessage: jest.fn(),
    suggestions: [],
  }),
}));

// Mock the useLanguage hook
jest.mock('@/hooks/useLanguage', () => ({
  useLanguage: () => ({
    language: 'en',
    setLanguage: jest.fn(),
  }),
}));

describe('ChatWidget', () => {
  it('renders chat toggle button initially', () => {
    render(<ChatWidget />);

    const toggleButton = screen.getByRole('button', { name: /open chat assistant/i });
    expect(toggleButton).toBeInTheDocument();
  });

  it('opens chat panel when toggle button is clicked', () => {
    render(<ChatWidget />);

    const toggleButton = screen.getByRole('button', { name: /open chat assistant/i });
    fireEvent.click(toggleButton);

    // After clicking, chat panel should be visible as a dialog
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Campus Assistant')).toBeInTheDocument();
  });

  it('displays welcome message when chat is opened', () => {
    render(<ChatWidget />);

    const toggleButton = screen.getByRole('button', { name: /open chat assistant/i });
    fireEvent.click(toggleButton);

    // Welcome message should be visible
    expect(screen.getByText(/Welcome to Campus Assistant/i)).toBeInTheDocument();
  });

  it('can close chat with close button', () => {
    render(<ChatWidget />);

    // Open chat
    const toggleButton = screen.getByRole('button', { name: /open chat assistant/i });
    fireEvent.click(toggleButton);

    // Verify dialog is open
    expect(screen.getByRole('dialog')).toBeInTheDocument();

    // Close chat
    const closeButton = screen.getByRole('button', { name: /close chat/i });
    fireEvent.click(closeButton);

    // Dialog should be gone, toggle button should be back
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /open chat assistant/i })).toBeInTheDocument();
  });
});
