/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    colors: {
      transparent: 'transparent',
      current: 'currentColor',
      chalk: '#F3F5F4',
      surface: '#FFFFFF',
      ink: '#1C2733',
      pencil: '#5B6772',
      line: '#D7DDDB',
      petrol: {
        DEFAULT: '#14565F',
        hover: '#0F4249',
        tint: '#E3EEEF',
      },
      marigold: {
        DEFAULT: '#E0A526',
        tint: '#FBF1D6',
      },
      moss: '#2F7D52',
      brick: '#B23A2E',
    },
    borderRadius: {
      none: '0px',
      badge: '4px',
      control: '6px',
      DEFAULT: '6px',
      full: '9999px',
    },
    boxShadow: {
      none: 'none',
      menu: '0 2px 8px rgba(28, 39, 51, 0.08)',
      dialog: '0 4px 16px rgba(28, 39, 51, 0.12)',
    },
    fontFamily: {
      sans: ['"IBM Plex Sans"', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
    },
    extend: {
      fontSize: {
        base: ['15px', '22px'],
      },
      transitionDuration: {
        DEFAULT: '150ms',
      },
    },
  },
  plugins: [],
};
