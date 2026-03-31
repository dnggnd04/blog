import { render, screen } from '@testing-library/react';
import App from './App';

test('renders blog title', () => {
  render(<App />);
  // Tìm thẻ h1 có văn bản "Blog của tôi"
  const titleElement = screen.getByRole('heading', { level: 1, name: /Blog của tôi/i });
  expect(titleElement).toBeInTheDocument();
});